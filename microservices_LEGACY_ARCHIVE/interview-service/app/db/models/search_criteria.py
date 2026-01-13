from typing import Optional

from sqlmodel import Field, SQLModel


class SearchCriteria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_title: Optional[str] = None
    required_skills: Optional[str] = None
    nice_to_have_skills: Optional[str] = None
    company_culture: Optional[str] = None
    experience_level: Optional[str] = None
