"""CRUD operations for demo interview sessions."""

from sqlalchemy.orm import Session

from app.db.models.demo_interview_session import DemoInterviewSession
from app.schemas.demo_interview_session import (
    DemoInterviewSessionCreate,
)


def create_demo_session(db: Session, session_data: DemoInterviewSessionCreate) -> DemoInterviewSession:
    """Creates a new demo interview session."""
    session = DemoInterviewSession(
        session_id=session_data.session_id,
        candidate_name=session_data.candidate_name,
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_demo_session_by_id(db: Session, session_id: str) -> DemoInterviewSession | None:
    """Retrieves a demo interview session by session_id."""
    return db.query(DemoInterviewSession).filter(DemoInterviewSession.session_id == session_id).first()


def get_demo_session_by_db_id(db: Session, db_id: int) -> DemoInterviewSession | None:
    """Retrieves a demo interview session by database ID."""
    return db.query(DemoInterviewSession).filter(DemoInterviewSession.id == db_id).first()


def update_demo_session_status(db: Session, session_id: str, status: str) -> DemoInterviewSession | None:
    """Updates the status of a demo interview session."""
    session = get_demo_session_by_id(db, session_id)
    if session:
        session.status = status
        db.commit()
        db.refresh(session)
    return session
