# System version model for tracking DB version
from typing import Optional

from sqlmodel import Field, SQLModel


class SystemVersion(SQLModel, table=True):
    __tablename__ = "system_version"

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str
    description: Optional[str] = None
