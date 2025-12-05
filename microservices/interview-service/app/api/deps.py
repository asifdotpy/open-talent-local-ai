"""
Dependency functions for FastAPI routes.
"""

from typing import Generator

from app.db.session import SessionLocal

def get_db() -> Generator:
    """
    Database dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()