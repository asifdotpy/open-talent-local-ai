"""Interview Management Routes.

Handles interview lifecycle: start, stop, feedback.
"""

from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/interview", tags=["interview"])


class StartInterviewRequest(BaseModel):
    """Request schema for starting an interview."""

    searchCriteria: dict
    candidateProfile: dict


@router.post("/start", status_code=201)
async def start_interview(request: StartInterviewRequest):
    """Start a new interview session (Mock Implementation)."""
    # Extract candidate name if available
    candidate_name = request.candidateProfile.get("fullName", "Candidate")

    # Generate mock session ID
    session_id = str(uuid4())

    return {
        "message": "Handoff received successfully. Interview process initiated.",
        "candidate": candidate_name,
        "interview_session_id": session_id,
        "initial_response": {
            "video_url": "https://example.com/video_feed",
            "audio_url": "https://example.com/audio_feed",
            "session_token": "mock_token_123",
        },
    }
