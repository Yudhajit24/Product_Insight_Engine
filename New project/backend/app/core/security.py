from datetime import datetime, timedelta
from jose import jwt
from .config import settings


FIXTURE_USER = {"username": "demo", "password": "demo", "user_id": 1}


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
