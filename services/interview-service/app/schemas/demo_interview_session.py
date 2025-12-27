"""Pydantic models for Demo Interview Session."""

from datetime import datetime

from pydantic import BaseModel


class DemoInterviewSessionBase(BaseModel):
    session_id: str
    candidate_name: str | None = None

class DemoInterviewSessionCreate(DemoInterviewSessionBase):
    pass

class DemoInterviewSessionResponse(DemoInterviewSessionBase):
    id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True
