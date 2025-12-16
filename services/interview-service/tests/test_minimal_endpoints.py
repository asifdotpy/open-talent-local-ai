"""Minimal endpoint sanity tests for Interview Service.

Covers:
- Health & root endpoints
- Room create and status
- Next-question, analyze-response, adapt-interview with minimal payloads
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import FastAPI app from the local service module
    from main import app
    return TestClient(app)


def _minimal_participants():
    return [
        {
            "user_id": "candidate-1",
            "role": "candidate",
            "display_name": "Jane Candidate",
        },
        {
            "user_id": "interviewer-1",
            "role": "interviewer",
            "display_name": "John Interviewer",
        },
    ]


def test_health_and_root(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

    r = client.get("/")
    assert r.status_code == 200
    assert "TalentAI Interview Service" in r.json().get("message", "")


def test_room_create_and_status_minimal(client: TestClient):
    create = client.post(
        "/api/v1/rooms/create",
        json={
            "interview_session_id": "sess-min-1",
            "participants": _minimal_participants(),
            "duration_minutes": 30,
        },
    )
    assert create.status_code == 200
    room = create.json()
    room_id = room["room_id"]

    status = client.get(f"/api/v1/rooms/{room_id}/status")
    assert status.status_code == 200
    data = status.json()
    assert data["room_id"] == room_id
    assert data["status"] in {"created", "active"}


def test_next_question_minimal(client: TestClient):
    # Create room
    create = client.post(
        "/api/v1/rooms/create",
        json={
            "interview_session_id": "sess-min-2",
            "participants": _minimal_participants(),
        },
    )
    room_id = create.json()["room_id"]

    # Minimal NextQuestionRequest (all optional fields omitted)
    resp = client.post(
        f"/api/v1/rooms/{room_id}/next-question",
        json={},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "question" in data
    assert "question_number" in data


def test_analyze_response_minimal(client: TestClient):
    # Create room
    create = client.post(
        "/api/v1/rooms/create",
        json={
            "interview_session_id": "sess-min-3",
            "participants": _minimal_participants(),
        },
    )
    room_id = create.json()["room_id"]

    # Minimal required fields
    resp = client.post(
        f"/api/v1/rooms/{room_id}/analyze-response",
        json={
            "question_id": "q-1",
            "response_text": "A brief answer.",
            "question_context": "General question",
            "participant_id": "candidate-1",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "analysis" in data
    assert "expertise_level" in data


def test_adapt_interview_minimal(client: TestClient):
    # Create room
    create = client.post(
        "/api/v1/rooms/create",
        json={
            "interview_session_id": "sess-min-4",
            "participants": _minimal_participants(),
        },
    )
    room_id = create.json()["room_id"]

    resp = client.post(
        f"/api/v1/rooms/{room_id}/adapt-interview",
        json={
            "current_phase": "technical",
            "time_remaining_minutes": 10,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "adaptations" in data
    assert "recommendations" in data
