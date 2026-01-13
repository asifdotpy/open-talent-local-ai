from pydantic import BaseModel
from typing import List, Optional


class JobDetails(BaseModel):
    """
    Pydantic model representing the details of a job,
    which corresponds to a Project in the database.
    """

    title: str
    description: str
    key_responsibilities: List[str]
    required_skills: List[str]
