"""API routes for handling the interview process."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import interview as interview_crud
from app.crud.demo_interview_session import create_demo_session, get_demo_session_by_id

# Demo-only imports
from app.schemas.demo_interview_session import (
    DemoInterviewSessionCreate,
    DemoInterviewSessionResponse,
)
from app.schemas.interview import HandoffPayload
from app.services import audit_service, avatar_service, conversation_service

router = APIRouter()


# --- DEMO-ONLY ENDPOINTS ---
@router.post("/demo-session", response_model=DemoInterviewSessionResponse, status_code=201)
def create_demo_interview_session(*, db: Session = Depends(deps.get_db), payload: DemoInterviewSessionCreate):
    """Create a demo interview session with minimal candidate data. Returns session_id."""
    demo = create_demo_session(db, payload)
    return demo.as_dict()


@router.get("/demo-session/{session_id}", response_model=DemoInterviewSessionResponse)
def get_demo_interview_session(session_id: str, db: Session = Depends(deps.get_db)):
    """Retrieve demo candidate data by session_id."""
    demo = get_demo_session_by_id(db, session_id)
    if not demo:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Demo session not found")
    return demo.as_dict()


@router.post("/start", status_code=201)
def start_interview(*, db: Session = Depends(deps.get_db), payload: HandoffPayload) -> dict:
    """Receives a candidate handoff from the Agent service and initiates
    the interview process.
    """
    # Log the incoming payload for auditing purposes.
    audit_service.log_interview_payload(payload)

    # Create the interview record in the database
    interview = interview_crud.create_interview(db=db, payload=payload)

    # Initiate the conversation with the Conversation Service.
    first_dialogue = conversation_service.initiate_conversation(candidate_profile=payload.candidateProfile)

    # Get the first response from the Avatar Service.
    avatar_response = avatar_service.get_avatar_response(dialogue=first_dialogue)

    # Return a session ID and initial response to the client.
    return {
        "message": "Handoff received successfully. Interview process initiated.",
        "candidate": payload.candidateProfile.fullName,
        "interview_session_id": interview.session_id,
        "initial_response": avatar_response,
    }
