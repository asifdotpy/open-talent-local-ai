import json

from pydantic import BaseModel
from sqlalchemy import Column, String, Text

from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    key_responsibilities_json = Column(Text)  # Stored as JSON string
    required_skills_json = Column(Text)  # Stored as JSON string

    @property
    def key_responsibilities(self):
        return json.loads(self.key_responsibilities_json) if self.key_responsibilities_json else []

    @property
    def required_skills(self):
        return json.loads(self.required_skills_json) if self.required_skills_json else []


class JobDetails(BaseModel):
    """Pydantic model representing the details of a job,
    which corresponds to a Project in the database.
    """

    id: str
    title: str
    description: str
    key_responsibilities: list[str]
    required_skills: list[str]

    class Config:
        from_attributes = True
