# System version model for tracking DB version

from sqlmodel import Field, SQLModel


class SystemVersion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    version: str
    description: str | None = None
