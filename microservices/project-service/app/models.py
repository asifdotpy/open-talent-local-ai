from pydantic import BaseModel


class JobDetails(BaseModel):
    """Pydantic model representing the details of a job,
    which corresponds to a Project in the database.
    """

    title: str
    description: str
    key_responsibilities: list[str]
    required_skills: list[str]
