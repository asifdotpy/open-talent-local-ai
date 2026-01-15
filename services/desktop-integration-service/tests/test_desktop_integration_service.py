import pytest


class TestDesktopIntegrationServiceBasics:
    def test_service_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()


class TestSystemEndpoints:
    def test_get_system_status(self, client):
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        assert "services_online" in response.json()

    def test_list_services(self, client):
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        assert "service_registry" in response.json()


class TestModelEndpoints:
    def test_list_models(self, client):
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        assert "models" in response.json()

    def test_select_model(self, client):
        # We need an available model ID, fallback has vetta-granite-2b-gguf-v4
        response = client.post(
            "/api/v1/models/select", params={"model_id": "vetta-granite-2b-gguf-v4"}
        )
        assert response.status_code == 200


class TestInterviewEndpoints:
    def test_start_interview(self, client):
        payload = {
            "role": "Software Engineer",
            "model": "vetta-granite-2b-gguf-v4",
            "totalQuestions": 3,
        }
        response = client.post("/api/v1/interviews/start", json=payload)
        assert response.status_code == 200
        assert "messages" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
