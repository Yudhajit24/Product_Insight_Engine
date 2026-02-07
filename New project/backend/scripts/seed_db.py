import csv
import os
import ast
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app import models

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "out"


def load_csv(path: Path):
    with path.open("r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    database_url = os.getenv("DATABASE_URL", "sqlite+pysqlite:///./app.db")
    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    users = load_csv(DATA_DIR / "users.csv")
    events = load_csv(DATA_DIR / "events.csv")
    feedback = load_csv(DATA_DIR / "feedback.csv")

    db = SessionLocal()
    for row in users:
        db.merge(models.User(
            id=int(row["id"]),
            created_at=row["created_at"],
            plan=row["plan"],
            country=row["country"],
        ))
    db.commit()

    for row in events:
        db.add(models.Event(
            user_id=int(row["user_id"]),
            event_type=row["event_type"],
            metadata=ast.literal_eval(row["metadata"]),
            timestamp=row["timestamp"],
        ))
    db.commit()

    for row in feedback:
        db.add(models.Feedback(
            user_id=int(row["user_id"]),
            text=row["text"],
            rating=int(row["rating"]),
            timestamp=row["timestamp"],
        ))
    db.commit()
    db.close()

    print("Seed complete")


if __name__ == "__main__":
    main()
