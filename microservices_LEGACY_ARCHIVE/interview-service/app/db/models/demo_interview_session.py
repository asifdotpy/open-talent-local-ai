# Demo interview session model for testing
from datetime import datetime

from sqlmodel import Field, SQLModel


class DemoInterviewSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str
    candidate_name: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    status: str | None = "active"
