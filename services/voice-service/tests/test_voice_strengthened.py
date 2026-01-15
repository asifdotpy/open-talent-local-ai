

class TestVoiceStrengthened:
    def test_service_info_extended(self, client):
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "stt" in data
        assert "tts" in data
        assert "vad" in data

    def test_api_docs_info(self, client):
        response = client.get("/api-docs")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "service" in data

    def test_health_detailed(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
