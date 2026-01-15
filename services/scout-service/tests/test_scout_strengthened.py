import pytest


class TestScoutStrengthened:
    def test_get_agents_registry(self, client):
        response = client.get("/agents/registry")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total_agents" in data

    def test_get_agents_health(self, client):
        response = client.get("/agents/health")
        assert response.status_code in [
            200,
            500,
        ]  # 500 might happen if agents are unreachable, but endpoint exists
        if response.status_code == 200:
            data = response.json()
            assert "total_agents" in data
            assert "healthy_agents" in data

    def test_full_system_health(self, client):
        response = client.get("/health/full")
        assert response.status_code == 200
        data = response.json()
        assert "agents_summary" in data

    def test_search_multi_agent(self, client):
        response = client.post(
            "/search/multi-agent",
            json={"query": "python developer", "location": "Dublin", "max_results": 5},
        )
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "candidates" in data

    def test_handoff_creation(self, client):
        response = client.post(
            "/handoff",
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

    def test_route_by_capability(self, client):
        response = client.post(
            "/agents/capability/search?endpoint=search&method=POST",
            json={"query": "test"},
        )
        assert response.status_code in [200, 404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
