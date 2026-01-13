# Demo interview session model for testing
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class DemoInterviewSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    candidate_name: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    status: Optional[str] = "active"
