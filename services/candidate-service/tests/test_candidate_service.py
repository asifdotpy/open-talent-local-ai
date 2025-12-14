"""
Tests for Candidate Service
Following TDD principles - tests written before implementation
Port: 8008
Purpose: Candidate management, applications, profiles
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.fixture
def candidate_service_url():
    return "http://localhost:8008"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def candidate_data() -> Dict[str, Any]:
    return {
        "email": "candidate@example.com",
        "first_name": "John",
        "last_name": "Candidate",
        "phone": "+1234567890",
        "resume_url": "https://example.com/resume.pdf"
    }


@pytest.fixture
def application_data() -> Dict[str, Any]:
    return {
        "job_id": "job123",
        "candidate_id": "candidate123",
        "status": "applied",
        "cover_letter": "I am interested in this position"
    }


class TestCandidateServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, candidate_service_url, async_client):
        response = await async_client.get(f"{candidate_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, candidate_service_url, async_client):
        response = await async_client.get(f"{candidate_service_url}/")
        assert response.status_code == 200


class TestCandidateManagement:
    @pytest.mark.asyncio
    async def test_create_candidate(self, candidate_service_url, async_client, candidate_data, auth_headers):
        response = await async_client.post(
            f"{candidate_service_url}/api/v1/candidates",
            json=candidate_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_candidate(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{candidate_service_url}/api/v1/candidates/123",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_candidates(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{candidate_service_url}/api/v1/candidates",
            headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_update_candidate(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.put(
            f"{candidate_service_url}/api/v1/candidates/123",
            json={"first_name": "Jane"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_delete_candidate(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.delete(
            f"{candidate_service_url}/api/v1/candidates/123",
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 204, 404]


class TestApplicationTracking:
    @pytest.mark.asyncio
    async def test_create_application(self, candidate_service_url, async_client, application_data, auth_headers):
        response = await async_client.post(
            f"{candidate_service_url}/api/v1/applications",
            json=application_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_applications(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{candidate_service_url}/api/v1/applications",
            headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_get_candidate_applications(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{candidate_service_url}/api/v1/candidates/123/applications",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_application_status(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.patch(
            f"{candidate_service_url}/api/v1/applications/app123",
            json={"status": "interview_scheduled"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]


class TestCandidateProfile:
    @pytest.mark.asyncio
    async def test_get_candidate_resume(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{candidate_service_url}/api/v1/candidates/123/resume",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_upload_resume(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{candidate_service_url}/api/v1/candidates/123/resume",
            json={"resume_url": "https://example.com/resume.pdf"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_candidate_skills(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{candidate_service_url}/api/v1/candidates/123/skills",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_add_skill(self, candidate_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{candidate_service_url}/api/v1/candidates/123/skills",
            json={"skill": "Python", "proficiency": "expert"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
