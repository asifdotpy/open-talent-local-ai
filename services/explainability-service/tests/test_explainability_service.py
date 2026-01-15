import pytest


class TestExplainabilityServiceBasics:
    def test_service_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200


class TestDecisionExplanation:
    def test_explain_score(self, client, auth_headers):
        response = client.post(
            "/api/v1/explain/score",
            json={"interview_id": "int123", "score": 0.85},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]

    def test_explain_recommendation(self, client, auth_headers):
        response = client.post(
            "/api/v1/explain/recommendation",
            json={"interview_id": "int123", "recommendation": "hire"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]

    def test_explain_decision_path(self, client, auth_headers):
        response = client.post(
            "/api/v1/explain/path",
            json={"interview_id": "int123"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]


class TestFeatureImportance:
    def test_get_feature_importance(self, client, auth_headers):
        response = client.get("/api/v1/features/importance", headers=auth_headers)
        assert response.status_code in [200, 403]

    def test_get_interview_feature_values(self, client, auth_headers):
        response = client.get("/api/v1/interviews/int123/features", headers=auth_headers)
        assert response.status_code in [200, 404]


class TestTransparency:
    def test_get_model_metadata(self, client, auth_headers):
        response = client.get("/api/v1/model/metadata", headers=auth_headers)
        assert response.status_code in [200, 403]

    def test_get_decision_log(self, client, auth_headers):
        response = client.get("/api/v1/decisions/log", headers=auth_headers)
        assert response.status_code in [200, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
