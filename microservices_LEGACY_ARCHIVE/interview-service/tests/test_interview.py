"""Tests for the interview process."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def test_start_interview(client: TestClient, db: Session) -> None:
    """Test the start_interview endpoint."""
    payload = {
        "searchCriteria": {
            "jobTitle": "Software Engineer",
            "requiredSkills": ["Python", "FastAPI"],
            "niceToHaveSkills": ["React", "Docker"],
            "companyCulture": ["Agile", "Remote"],
            "experienceLevel": "Senior",
        },
        "candidateProfile": {
            "fullName": "John Doe",
            "sourceUrl": "https://example.com/johndoe",
            "summary": "A senior software engineer with experience in Python and FastAPI.",
            "workExperience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Acme Inc.",
                    "duration": "2 years",
                    "responsibilities": ["Developed and maintained web applications using Python and FastAPI."],
                }
            ],
            "education": [
                {
                    "institution": "University of Example",
                    "degree": "B.S. in Computer Science",
                    "year": "2018",
                }
            ],
            "skills": {"matched": ["Python", "FastAPI"], "unmatched": ["Java"]},
            "alignmentScore": 0.85,
            "initialQuestions": [
                {
                    "question": "Tell me about your experience with FastAPI.",
                    "reasoning": "To assess the candidate's hands-on experience with the required framework.",
                }
            ],
        },
    }

    response = client.post(f"{settings.API_V1_STR}/interview/start", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Handoff received successfully. Interview process initiated."
    assert data["candidate"] == "John Doe"
    assert "interview_session_id" in data
    assert "initial_response" in data
    assert "video_url" in data["initial_response"]
    assert "audio_url" in data["initial_response"]
