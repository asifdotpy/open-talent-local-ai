"""
SQLAlchemy Base model.
"""

from sqlalchemy.orm import declarative_base
from app.db.models.system_version import SystemVersion # Ensure SystemVersion model is registered

Base = declarative_base()