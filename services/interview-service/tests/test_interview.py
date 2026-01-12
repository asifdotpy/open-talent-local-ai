"""Main tests for the Interview Service, covering core functionalities."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def interview_payload():
    """Valid payload for starting an interview."""
    return {
        "searchCriteria": {
            "jobTitle": "Senior Software Engineer",
            "requiredSkills": ["Python", "FastAPI", "System Design"],
            "companyCulture": ["Remote", "Agile"],
            "experienceLevel": "Senior",
        },
        "candidateProfile": {
            "fullName": "Jane Doe",
            "sourceUrl": "https://example.com/janedoe",
            "summary": "Experienced software engineer with a focus on backend development.",
            "workExperience": [
                {
                    "title": "Lead Backend Engineer",
                    "company": "Tech Solutions Inc.",
                    "duration": "3 years",
                }
            ],
            "skills": {"matched": ["Python", "FastAPI"], "unmatched": ["React"]},
            "alignmentScore": 0.9,
            "initialQuestions": [
                {
                    "question": "Describe your experience with large-scale distributed systems.",
                    "reasoning": "To assess system design and architecture skills.",
                }
            ],
        },
    }


def test_start_interview(test_client: TestClient, interview_payload):
    """Test the /interview/start endpoint with a valid payload."""
    response = test_client.post("/api/v1/interview/start", json=interview_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Handoff received successfully. Interview process initiated."
    assert "interview_session_id" in data
    assert data["candidate"] == "Jane Doe"
