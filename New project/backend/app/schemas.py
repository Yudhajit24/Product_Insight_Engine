from datetime import datetime
from pydantic import BaseModel, Field


class EventIn(BaseModel):
    user_id: int
    event_type: str
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime | None = None


class FeedbackIn(BaseModel):
    user_id: int
    text: str
    rating: int | None = None
    timestamp: datetime | None = None


class InsightOut(BaseModel):
    id: int
    type: str
    score: float
    payload: dict
    created_at: datetime
    explanation: str | None = None


class InsightGenerateIn(BaseModel):
    start_time: datetime
    end_time: datetime
    cohort_label: str | None = None


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
