"""Tests for Scout Service
Following TDD principles - tests written before implementation
Port: 8010
Purpose: Talent sourcing, candidate discovery, search.
"""


import httpx
import pytest


@pytest.fixture
def scout_service_url():
    return "http://localhost:8010"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


class TestScoutServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, scout_service_url, async_client):
        response = await async_client.get(f"{scout_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, scout_service_url, async_client):
        response = await async_client.get(f"{scout_service_url}/")
        assert response.status_code == 200


class TestCandidateSearch:
    @pytest.mark.asyncio
    async def test_search_candidates(self, scout_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{scout_service_url}/api/v1/search?skills=python&location=usa", headers=auth_headers
        )
        assert response.status_code in [200, 403, 400]

    @pytest.mark.asyncio
    async def test_advanced_search(self, scout_service_url, async_client, auth_headers):
        search_query = {
            "skills": ["python", "javascript"],
            "experience_years": 5,
            "location": "remote",
            "salary_range": [80000, 150000],
        }
        response = await async_client.post(
            f"{scout_service_url}/api/v1/search/advanced", json=search_query, headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_candidate_match_score(self, scout_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{scout_service_url}/api/v1/candidates/candidate123/match", headers=auth_headers
        )
        assert response.status_code in [200, 404]


class TestSourcedLists:
    @pytest.mark.asyncio
    async def test_create_sourced_list(self, scout_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{scout_service_url}/api/v1/lists",
            json={"name": "Python Developers", "criteria": {"skills": ["python"]}},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_sourced_list(self, scout_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{scout_service_url}/api/v1/lists/list123", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_list_candidates(self, scout_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{scout_service_url}/api/v1/lists/list123/candidates", headers=auth_headers
        )
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
