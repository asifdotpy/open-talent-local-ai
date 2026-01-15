from datetime import date
from typing import Literal

from pydantic import BaseModel, HttpUrl


class ProfileSource(BaseModel):
    """Records the origin of the candidate data."""

    source_name: Literal["ContactOut", "SalesQL", "LinkedIn", "Manual"]
    source_id: str | None = None  # The record ID from the external system
    retrieved_at: date


class WorkExperience(BaseModel):
    """Represents a single position in a candidate's work history."""

    position: str
    company: str
    start_date: date
    end_date: date | None = None
    description: str | None = None


class Education(BaseModel):
    """Represents an entry in a candidate's education history."""

    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: date | None = None


class SocialProfile(BaseModel):
    """Links to social and professional profiles."""

    network: Literal["LinkedIn", "GitHub", "Twitter", "Portfolio"]
    url: HttpUrl


class EnrichedProfile(BaseModel):
    """A universal data model to accommodate data from ContactOut and other
    sourcing tools, designed to be compatible with the Agent-Interview bridge.
    """

    source: ProfileSource
    work_history: list[WorkExperience] = []
    education_history: list[Education] = []
    social_profiles: list[SocialProfile] = []
    contact_email: str | None = None
    contact_phone: str | None = None


# This would be linked to the main Candidate model, likely via a JSONB field
# or a separate table. For example, in the Candidate SQLAlchemy model:
#
# enriched_data = Column(JSON, nullable=True)
#
