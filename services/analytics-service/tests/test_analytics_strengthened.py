import httpx
import pytest


@pytest.fixture
def analytics_service_url():
    return "http://localhost:8007"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=10.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


class TestAnalyticsStrengthened:
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, analytics_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{analytics_service_url}/api/v1/analyze/sentiment",
            json={"text": "This is a great experience, I love the platform!"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["emotion"] == "positive"
        assert "great" in data["keywords"]

    @pytest.mark.asyncio
    async def test_analyze_quality(self, analytics_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{analytics_service_url}/api/v1/analyze/quality",
            json={
                "response_text": "I have used Python for 5 years in backend development.",
                "question_context": "Tell me about your experience with Python.",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "clarity" in data
        assert "technical_accuracy" in data

    @pytest.mark.asyncio
    async def test_analyze_bias(self, analytics_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{analytics_service_url}/api/v1/analyze/bias",
            json={"text": "Candidate was very expressive."},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "bias_score" in data

    @pytest.mark.asyncio
    async def test_analyze_expertise(self, analytics_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{analytics_service_url}/api/v1/analyze/expertise",
            json={
                "response_text": "I implemented a microservices architecture using Docker and Kubernetes.",
                "question_context": "Explain your experience with container orchestration.",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "level" in data
        assert "confidence" in data

    @pytest.mark.asyncio
    async def test_analyze_performance(self, analytics_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{analytics_service_url}/api/v1/analyze/performance",
            json={
                "room_id": "room_123",
                "response_analyses": [
                    {
                        "quality": {"overall_score": 8.5},
                        "sentiment": {"polarity": 0.5},
                        "bias_detection": {"flags": []},
                        "expertise_assessment": {"level": "advanced"},
                    }
                ],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert data["expertise_level"] == "advanced"

    @pytest.mark.asyncio
    async def test_generate_report(self, analytics_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{analytics_service_url}/api/v1/analyze/report",
            json={
                "room_id": "room_123",
                "room_created_at": "2026-01-01T22:00:00",
                "analyses": [
                    {
                        "quality": {"overall_score": 8.5},
                        "sentiment": {"polarity": 0.5},
                        "bias_detection": {"flags": []},
                        "expertise_assessment": {"level": "advanced"},
                    }
                ],
                "responses": [{"text": "Hello world"}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "interview_effectiveness" in data
