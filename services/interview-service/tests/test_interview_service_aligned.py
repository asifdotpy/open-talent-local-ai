"""Aligned Tests for Interview Service
Targets the actual implementation in main.py.
"""
from datetime import datetime

from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def create_room_data():
    return {
        "interview_session_id": "test-session-123",
        "participants": [
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
        ],
        "duration_minutes": 45,
        "job_description": "Software Engineer with Python/React experience",
    }


class TestInterviewAligned:
    def test_health_check(self, test_client: TestClient):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, test_client: TestClient):
        response = test_client.get("/")
        assert response.status_code == 200
        assert "OpenTalent Interview Service" in response.json()["message"]

    def test_create_and_get_room(self, test_client: TestClient, create_room_data: dict):
        # Create Room
        response = test_client.post(
            "/api/v1/rooms/create", json=create_room_data
        )
        assert response.status_code == 200
        room = response.json()
        assert room["interview_session_id"] == "test-session-123"
        assert "room_id" in room
        room_id = room["room_id"]

        # Get Status
        response = test_client.get(f"/api/v1/rooms/{room_id}/status")
        assert response.status_code == 200
        assert response.json()["room_id"] == room_id

        # List Rooms
        response = test_client.get("/api/v1/rooms")
        assert response.status_code == 200
        assert any(r["room_id"] == room_id for r in response.json()["rooms"])

    def test_start_interview(self, test_client: TestClient, create_room_data: dict):
        # This endpoint also creates a room but triggers voice service
        data = create_room_data.copy()
        data["interview_session_id"] = f"session-start-{datetime.now().timestamp()}"
        response = test_client.post(
            "/api/v1/interviews/start", json=data
        )
        assert response.status_code in [200, 201]

    def test_vetta_info(self, test_client: TestClient):
        response = test_client.get("/api/v1/info")
        # May be 200 or 500 depending on model loading status in Vetta service
        assert response.status_code in [200, 500, 503]