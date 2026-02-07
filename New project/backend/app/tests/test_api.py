import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base
from app import models
import app.db.session as session
from app.main import app
from app.core.security import FIXTURE_USER


def setup_db(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_path}")
    session.engine = engine
    session.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session.SessionLocal()
    db.add(models.User(id=1, plan="free", country="US"))
    db.commit()
    db.close()


def auth_header(client: TestClient):
    res = client.post("/api/auth/login", json={"username": FIXTURE_USER["username"], "password": FIXTURE_USER["password"]})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_event_and_insight_flow(tmp_path):
    setup_db(tmp_path)
    client = TestClient(app)
    headers = auth_header(client)

    res = client.post("/api/events", json={
        "user_id": 1,
        "event_type": "signup",
        "metadata": {"source": "ad"},
        "timestamp": datetime.utcnow().isoformat(),
    }, headers=headers)
    assert res.status_code == 200

    res = client.post("/api/feedback", json={
        "user_id": 1,
        "text": "Love it",
        "rating": 5,
        "timestamp": datetime.utcnow().isoformat(),
    }, headers=headers)
    assert res.status_code == 200

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow() + timedelta(days=1)
    res = client.post("/api/insights/generate", json={
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "cohort_label": None,
    }, headers=headers)
    assert res.status_code == 200

    res = client.get("/api/insights?limit=10", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
