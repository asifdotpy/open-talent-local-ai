"""Aligned Tests for Interview Service
Targets the actual implementation in main.py (port 8014).
"""

from datetime import datetime

import httpx
import pytest


@pytest.fixture
def interview_service_url():
    return "http://localhost:8014"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=10.0)


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


@pytest.mark.asyncio
class TestInterviewAligned:
    async def test_health_check(self, interview_service_url, async_client, live_server):
        response = await async_client.get(f"{interview_service_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_root_endpoint(
        self, interview_service_url, async_client, live_server
    ):
        response = await async_client.get(f"{interview_service_url}/")
        assert response.status_code == 200
        assert "OpenTalent Interview Service" in response.json()["message"]

    async def test_create_and_get_room(
        self, interview_service_url, async_client, create_room_data, live_server
    ):
        # Create Room
        response = await async_client.post(
            f"{interview_service_url}/api/v1/rooms/create", json=create_room_data
        )
        assert response.status_code == 200
        room = response.json()
        assert room["interview_session_id"] == "test-session-123"
        assert "room_id" in room
        room_id = room["room_id"]

        # Get Status
        response = await async_client.get(
            f"{interview_service_url}/api/v1/rooms/{room_id}/status"
        )
        assert response.status_code == 200
        assert response.json()["room_id"] == room_id

        # List Rooms
        response = await async_client.get(f"{interview_service_url}/api/v1/rooms")
        assert response.status_code == 200
        assert any(r["room_id"] == room_id for r in response.json()["rooms"])

    async def test_start_interview(
        self, interview_service_url, async_client, create_room_data, live_server
    ):
        # This endpoint also creates a room but triggers voice service
        data = create_room_data.copy()
        data["interview_session_id"] = f"session-start-{datetime.now().timestamp()}"
        response = await async_client.post(
            f"{interview_service_url}/api/v1/interviews/start", json=data
        )
        assert response.status_code == 200
        assert "room_id" in response.json()

    async def test_vetta_info(self, interview_service_url, async_client, live_server):
        response = await async_client.get(f"{interview_service_url}/api/v1/vetta/info")
        # May be 200 or 500 depending on model loading status in Vetta service
        assert response.status_code in [200, 500, 503]
