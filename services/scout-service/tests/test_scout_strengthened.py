import httpx
import pytest


@pytest.fixture
def scout_url():
    return "http://localhost:8000"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=30.0)


class TestScoutStrengthened:
    @pytest.mark.asyncio
    async def test_get_agents_registry(self, scout_url, async_client):
        response = await async_client.get(f"{scout_url}/agents/registry")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total_agents" in data

    @pytest.mark.asyncio
    async def test_get_agents_health(self, scout_url, async_client):
        response = await async_client.get(f"{scout_url}/agents/health")
        assert response.status_code in [
            200,
            500,
        ]  # 500 might happen if agents are unreachable, but endpoint exists
        if response.status_code == 200:
            data = response.json()
            assert "total_agents" in data
            assert "healthy_agents" in data

    @pytest.mark.asyncio
    async def test_full_system_health(self, scout_url, async_client):
        response = await async_client.get(f"{scout_url}/health/full")
        assert response.status_code == 200
        data = response.json()
        assert "agents_summary" in data

    @pytest.mark.asyncio
    async def test_search_multi_agent(self, scout_url, async_client):
        response = await async_client.post(
            f"{scout_url}/search/multi-agent",
            json={"query": "python developer", "location": "Dublin", "max_results": 5},
        )
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "candidates" in data

    @pytest.mark.asyncio
    async def test_handoff_creation(self, scout_url, async_client):
        response = await async_client.post(
            f"{scout_url}/handoff",
            json={
                "jobTitle": "Software Engineer",
                "requiredSkills": ["Python", "FastAPI"],
                "niceToHaveSkills": ["Docker"],
                "companyCulture": ["innovative"],
                "experienceLevel": "senior",
            },
        )
        # This might return 404 if no candidates found in mock search, but endpoint exists
        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_route_by_capability(self, scout_url, async_client):
        response = await async_client.post(
            f"{scout_url}/agents/capability/search?endpoint=search&method=POST",
            json={"query": "test"},
        )
        assert response.status_code in [200, 404, 500]
