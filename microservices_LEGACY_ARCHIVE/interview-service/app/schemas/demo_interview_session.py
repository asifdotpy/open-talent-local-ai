"""
Pydantic models for Demo Interview Session
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DemoInterviewSessionBase(BaseModel):
    session_id: str
    candidate_name: Optional[str] = None


class DemoInterviewSessionCreate(DemoInterviewSessionBase):
    pass


class DemoInterviewSessionResponse(DemoInterviewSessionBase):
    id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True
