from datetime import datetime
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import pandas as pd

from .core.config import settings
from .core.security import FIXTURE_USER, create_access_token
from .db.session import get_db, engine
from .db.base import Base
from . import crud, models, schemas
from ml.pipeline import generate_insights_for_window, compute_user_feature_vectors, cluster_users


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Signal > Noise")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@app.post("/api/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn) -> schemas.TokenOut:
    if payload.username != FIXTURE_USER["username"] or payload.password != FIXTURE_USER["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=payload.username)
    return schemas.TokenOut(access_token=token)


@app.post("/api/events")
def ingest_events(
    events: Any,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    if isinstance(events, dict):
        events = [events]
    if not isinstance(events, list):
        raise HTTPException(status_code=400, detail="Invalid payload")

    parsed = []
    for item in events:
        parsed.append(schemas.EventIn(**item).model_dump())

    count = crud.create_events(db, parsed)
    return {"status": "ok", "ingested": count}


@app.post("/api/feedback")
def ingest_feedback(
    feedback: Any,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    if isinstance(feedback, dict):
        feedback = [feedback]
    if not isinstance(feedback, list):
        raise HTTPException(status_code=400, detail="Invalid payload")

    parsed = []
    for item in feedback:
        parsed.append(schemas.FeedbackIn(**item).model_dump())

    count = crud.create_feedback(db, parsed)
    return {"status": "ok", "ingested": count}


@app.post("/api/insights/generate", response_model=list[schemas.InsightOut])
def generate_insights(
    payload: schemas.InsightGenerateIn,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    events = db.query(models.Event).filter(
        models.Event.timestamp >= payload.start_time,
        models.Event.timestamp <= payload.end_time,
    ).all()
    feedback = db.query(models.Feedback).filter(
        models.Feedback.timestamp >= payload.start_time,
        models.Feedback.timestamp <= payload.end_time,
    ).all()
    users = db.query(models.User).all()

    events_df = pd.DataFrame([
        {"user_id": e.user_id, "event_type": e.event_type, "timestamp": e.timestamp, "metadata": e.metadata}
        for e in events
    ])
    feedback_df = pd.DataFrame([
        {"user_id": f.user_id, "text": f.text, "rating": f.rating, "timestamp": f.timestamp}
        for f in feedback
    ])
    users_df = pd.DataFrame([
        {"user_id": u.id, "plan": u.plan, "country": u.country, "cohort_label": u.cohort_label}
        for u in users
    ])

    feature_vectors = compute_user_feature_vectors(events_df)
    cohorts = cluster_users(feature_vectors) if not feature_vectors.empty else {}
    if cohorts:
        for user in users:
            if user.id in cohorts:
                user.cohort_label = cohorts[user.id]
        db.commit()

    insights = generate_insights_for_window(events_df, feedback_df, users_df)

    stored = []
    for insight in insights:
        stored.append(crud.create_insight(db, insight))
    return stored


@app.get("/api/insights", response_model=list[schemas.InsightOut])
def list_insights(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return crud.list_insights(db, limit=limit)


@app.post("/api/seed/demo")
def seed_demo(db: Session = Depends(get_db)):
    # Lightweight seed for frontend demo replay
    if db.query(models.User).count() == 0:
        for idx in range(1, 6):
            db.add(models.User(id=idx, plan="pro" if idx % 2 == 0 else "free", country="US"))
        db.commit()
    now = datetime.utcnow()
    events = []
    for user_id in range(1, 6):
        for i in range(20):
            events.append({
                "user_id": user_id,
                "event_type": "feature_use" if i % 3 else "signup",
                "metadata": {"feature": "export" if i % 2 else "import"},
                "timestamp": now,
            })
    crud.create_events(db, events)

    feedback = []
    for user_id in range(1, 6):
        feedback.append({
            "user_id": user_id,
            "text": "Great product" if user_id % 2 else "Confusing UI",
            "rating": 5 if user_id % 2 else 2,
            "timestamp": now,
        })
    crud.create_feedback(db, feedback)
    return {"status": "ok", "users": 5, "events": len(events), "feedback": len(feedback)}
