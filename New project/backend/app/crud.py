from datetime import datetime
from sqlalchemy.orm import Session
from . import models


def create_events(db: Session, events: list[dict]) -> int:
    for e in events:
        db.add(models.Event(
            user_id=e["user_id"],
            event_type=e["event_type"],
            metadata=e.get("metadata", {}),
            timestamp=e.get("timestamp") or datetime.utcnow(),
        ))
    db.commit()
    return len(events)


def create_feedback(db: Session, items: list[dict]) -> int:
    for f in items:
        db.add(models.Feedback(
            user_id=f["user_id"],
            text=f["text"],
            rating=f.get("rating"),
            timestamp=f.get("timestamp") or datetime.utcnow(),
        ))
    db.commit()
    return len(items)


def list_insights(db: Session, limit: int = 10):
    return db.query(models.Insight).order_by(models.Insight.created_at.desc()).limit(limit).all()


def create_insight(db: Session, insight: dict) -> models.Insight:
    obj = models.Insight(
        type=insight["type"],
        score=insight.get("score", 0.0),
        payload=insight.get("payload", {}),
        explanation=insight.get("explanation"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
