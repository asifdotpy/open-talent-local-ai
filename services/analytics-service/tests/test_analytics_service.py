import pytest


class TestAnalyticsServiceBasics:
    def test_service_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200


class TestInterviewAnalytics:
    def test_get_interview_stats(self, client, auth_headers):
        response = client.get("/api/v1/analytics/interviews", headers=auth_headers)
        assert response.status_code in [200, 403]

    def test_get_candidate_analytics(self, client, auth_headers):
        response = client.get(
            "/api/v1/analytics/candidates/candidate123",
            headers=auth_headers,
        )
        assert response.status_code in [200, 404]

    def test_get_interview_performance(self, client, auth_headers):
        response = client.get("/api/v1/analytics/interviews/int123", headers=auth_headers)
        assert response.status_code in [200, 404]


class TestMetrics:
    def test_get_overall_metrics(self, client, auth_headers):
        response = client.get("/api/v1/analytics/metrics", headers=auth_headers)
        assert response.status_code in [200, 403]

    def test_get_time_series_metrics(self, client, auth_headers):
        response = client.get("/api/v1/analytics/metrics/timeseries", headers=auth_headers)
        assert response.status_code in [200, 403]


class TestReporting:
    def test_generate_report(self, client, auth_headers):
        response = client.post(
            "/api/v1/analytics/reports",
            json={"type": "interview_summary", "date_range": "month"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]

    def test_get_report(self, client, auth_headers):
        response = client.get("/api/v1/analytics/reports/report123", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_export_report(self, client, auth_headers):
        response = client.get(
            "/api/v1/analytics/reports/report123/export",
            headers=auth_headers,
        )
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
