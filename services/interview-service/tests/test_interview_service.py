"""Tests for Interview Service
Following TDD principles - tests written before implementation
Port: 8006
Purpose: Interview management, scheduling, feedback.
"""

from typing import Any

import httpx
import pytest


@pytest.fixture
def interview_service_url():
    return "http://localhost:8006"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def interview_data() -> dict[str, Any]:
    return {
        "candidate_id": "candidate123",
        "job_id": "job123",
        "interview_type": "technical",
        "scheduled_time": "2024-12-20T14:00:00Z",
        "interviewer_id": "interviewer123",
        "duration_minutes": 60,
    }


@pytest.fixture
def feedback_data() -> dict[str, Any]:
    return {
        "rating": 4,
        "technical_skills": 4,
        "communication": 4,
        "comments": "Excellent candidate",
        "recommendation": "hire",
    }


class TestInterviewServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, interview_service_url, async_client):
        response = await async_client.get(f"{interview_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, interview_service_url, async_client):
        response = await async_client.get(f"{interview_service_url}/")
        assert response.status_code == 200


class TestInterviewManagement:
    @pytest.mark.asyncio
    async def test_create_interview(
        self, interview_service_url, async_client, interview_data, auth_headers
    ):
        response = await async_client.post(
            f"{interview_service_url}/api/v1/interviews", json=interview_data, headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_interview(self, interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{interview_service_url}/api/v1/interviews/123", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_interviews(self, interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{interview_service_url}/api/v1/interviews", headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_update_interview(self, interview_service_url, async_client, auth_headers):
        response = await async_client.put(
            f"{interview_service_url}/api/v1/interviews/123",
            json={"scheduled_time": "2024-12-21T14:00:00Z"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_cancel_interview(self, interview_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{interview_service_url}/api/v1/interviews/123/cancel",
            json={"reason": "Scheduling conflict"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]


class TestInterviewFeedback:
    @pytest.mark.asyncio
    async def test_submit_feedback(
        self, interview_service_url, async_client, feedback_data, auth_headers
    ):
        response = await async_client.post(
            f"{interview_service_url}/api/v1/interviews/123/feedback",
            json=feedback_data,
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_feedback(self, interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{interview_service_url}/api/v1/interviews/123/feedback", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_feedback(self, interview_service_url, async_client, auth_headers):
        response = await async_client.put(
            f"{interview_service_url}/api/v1/interviews/123/feedback",
            json={"rating": 5},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]


class TestInterviewScheduling:
    @pytest.mark.asyncio
    async def test_get_available_slots(self, interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{interview_service_url}/api/v1/interviews/available-slots", headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_schedule_interview(
        self, interview_service_url, async_client, interview_data, auth_headers
    ):
        response = await async_client.post(
            f"{interview_service_url}/api/v1/interviews/schedule",
            json=interview_data,
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_reschedule_interview(self, interview_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{interview_service_url}/api/v1/interviews/123/reschedule",
            json={"scheduled_time": "2024-12-22T14:00:00Z"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
