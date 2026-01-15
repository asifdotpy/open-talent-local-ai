import pytest


class TestAnalyticsStrengthened:
    def test_analyze_sentiment(self, client):
        payload = {"text": "I really love working with agentic AI systems!"}
        response = client.post("/api/v1/analyze/sentiment", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "polarity" in data
        assert data["emotion"] == "positive"

    def test_analyze_quality(self, client):
        payload = {
            "response_text": "I have extensive experience building scalable microservices with Python and FastAPI.",
            "question_context": "Tell me about your experience with Python backend development.",
        }
        response = client.post("/api/v1/analyze/quality", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] > 0
        assert "clarity" in data

    def test_analyze_bias(self, client):
        payload = {"text": "We need a young and energetic person for this junior role."}
        response = client.post("/api/v1/analyze/bias", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["bias_score"] > 0
        assert "age_bias" in data["flags"]

    def test_analyze_expertise(self, client):
        payload = {
            "response_text": "I have architected and led several projects using Kubernetes and AWS.",
            "question_context": "Explain your experience with cloud architecture.",
        }
        response = client.post("/api/v1/analyze/expertise", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["level"] in ["advanced", "expert"]
        assert "cloud" in data["technical_skills"]

    def test_analyze_performance(self, client):
        payload = {
            "room_id": "int_123",
            "response_analyses": [
                {
                    "sentiment": {"polarity": 0.5},
                    "quality": {"overall_score": 8.0},
                    "bias_detection": {"flags": []},
                    "expertise_assessment": {"level": "advanced"},
                }
            ],
        }
        response = client.post("/api/v1/analyze/performance", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] > 5
        assert data["sentiment_trend"] == "positive"

    def test_generate_report(self, client):
        payload = {
            "room_id": "room_456",
            "room_created_at": "2024-01-01T10:00:00",
            "responses": [{"text": "sample response"}],
            "analyses": [
                {
                    "sentiment": {"polarity": 0.1},
                    "quality": {"overall_score": 7.0},
                    "bias_detection": {"flags": [], "categories": []},
                    "expertise_assessment": {"level": "intermediate"},
                }
            ],
        }
        response = client.post("/api/v1/analyze/report", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "interview_effectiveness" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
