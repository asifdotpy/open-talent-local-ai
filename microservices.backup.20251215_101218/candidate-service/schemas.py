from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal
from datetime import date

class ProfileSource(BaseModel):
    """Records the origin of the candidate data."""
    source_name: Literal['ContactOut', 'SalesQL', 'LinkedIn', 'Manual']
    source_id: Optional[str] = None # The record ID from the external system
    retrieved_at: date

class WorkExperience(BaseModel):
    """Represents a single position in a candidate's work history."""
    position: str
    company: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None

class Education(BaseModel):
    """Represents an entry in a candidate's education history."""
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None

class SocialProfile(BaseModel):
    """Links to social and professional profiles."""
    network: Literal['LinkedIn', 'GitHub', 'Twitter', 'Portfolio']
    url: HttpUrl

class EnrichedProfile(BaseModel):
    """
    A universal data model to accommodate data from ContactOut and other
    sourcing tools, designed to be compatible with the Agent-Interview bridge.
    """
    source: ProfileSource
    work_history: List[WorkExperience] = []
    education_history: List[Education] = []
    social_profiles: List[SocialProfile] = []
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

# This would be linked to the main Candidate model, likely via a JSONB field
# or a separate table. For example, in the Candidate SQLAlchemy model:
#
# enriched_data = Column(JSON, nullable=True)
#
