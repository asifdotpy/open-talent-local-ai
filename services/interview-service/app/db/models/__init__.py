# Import all models here to ensure they are registered with SQLAlchemy
from app.db.models.demo_interview_session import DemoInterviewSession
from app.db.models.interview import Interview  # Added
from app.db.models.search_criteria import SearchCriteria  # Added
from app.db.models.system_version import SystemVersion
from app.db.models.user import User

__all__ = ["User", "SystemVersion", "DemoInterviewSession", "Interview", "SearchCriteria"]
