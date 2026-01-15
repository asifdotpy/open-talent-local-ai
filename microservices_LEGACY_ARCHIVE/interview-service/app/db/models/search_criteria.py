from sqlmodel import Field, SQLModel


class SearchCriteria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_title: str | None = None
    required_skills: str | None = None
    nice_to_have_skills: str | None = None
    company_culture: str | None = None
    experience_level: str | None = None
