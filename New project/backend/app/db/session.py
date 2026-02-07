from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings


def _engine():
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


engine = _engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
