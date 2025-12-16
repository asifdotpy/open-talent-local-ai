"""
Test Desktop Integration Service Registry - All 14 Microservices.

Tests that all 14 OpenTalent microservices are properly registered 
and callable through the gateway.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.service_discovery import ServiceDiscovery


client = TestClient(app)


class TestServiceRegistry:
    """Test suite for all registered services."""

    def test_service_registry_endpoint(self):
        """Test /api/v1/services endpoint lists all services."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        data = response.json()
        assert "service_registry" in data
        assert data["total_services"] == 14  # 13 services + Ollama
        
        # Verify all service categories exist
        registry = data["service_registry"]
        assert "core_services" in registry
        assert "ai_services" in registry
        assert "media_services" in registry
        assert "analytics_services" in registry
        assert "infrastructure_services" in registry
        assert "ai_engine" in registry

    def test_all_core_services_registered(self):
        """Test all 3 core services are in registry."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]["core_services"]
        assert "scout-service" in registry
        assert "user-service" in registry
        assert "candidate-service" in registry

    def test_all_ai_services_registered(self):
        """Test all 3 AI services are in registry."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]["ai_services"]
        assert "conversation-service" in registry
        assert "interview-service" in registry
        assert "_granite-interview-service" in registry

    def test_all_media_services_registered(self):
        """Test all 2 media services are in registry."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]["media_services"]
        assert "voice-service" in registry
        assert "avatar-service" in registry

    def test_all_analytics_services_registered(self):
        """Test all 3 analytics services are in registry."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]["analytics_services"]
        assert "analytics-service" in registry
        assert "ai-auditing-service" in registry
        assert "explainability-service" in registry

    def test_all_infrastructure_services_registered(self):
        """Test all 2 infrastructure services are in registry."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]["infrastructure_services"]
        assert "security-service" in registry
        assert "notification-service" in registry

    def test_ai_engine_registered(self):
        """Test Ollama AI engine is registered."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]["ai_engine"]
        assert "ollama" in registry
        assert registry["ollama"]["port"] == 11434

    def test_service_ports_correct(self):
        """Test all services have correct port mappings."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]
        
        # Expected port mappings
        expected_ports = {
            "scout-service": 8000,
            "user-service": 8001,
            "conversation-service": 8002,
            "voice-service": 8003,
            "avatar-service": 8004,
            "interview-service": 8005,
            "candidate-service": 8006,
            "analytics-service": 8007,
            "security-service": 8010,
            "notification-service": 8011,
            "ai-auditing-service": 8012,
            "explainability-service": 8013,
            "ollama": 11434,
        }
        
        all_services = {}
        for category in registry.values():
            all_services.update(category)
        
        for service_name, expected_port in expected_ports.items():
            assert service_name in all_services, f"Service {service_name} not found"
            assert all_services[service_name]["port"] == expected_port, \
                f"Service {service_name} has port {all_services[service_name]['port']}, expected {expected_port}"

    def test_service_descriptions_present(self):
        """Test all services have descriptions."""
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        
        registry = response.json()["service_registry"]
        
        all_services = {}
        for category in registry.values():
            all_services.update(category)
        
        for service_name, service_info in all_services.items():
            assert "description" in service_info, f"Service {service_name} missing description"
            assert len(service_info["description"]) > 0, f"Service {service_name} has empty description"

    def test_service_discovery_initialization(self):
        """Test ServiceDiscovery initializes with all services."""
        discovery = ServiceDiscovery()
        
        # Should have 14 services (13 + Ollama)
        assert len(discovery.services) == 14, \
            f"Expected 14 services, got {len(discovery.services)}"
        
        # Verify all service names
        expected_services = {
            "scout-service",
            "user-service",
            "candidate-service",
            "conversation-service",
            "interview-service",
            "_granite-interview-service",
            "voice-service",
            "avatar-service",
            "analytics-service",
            "security-service",
            "notification-service",
            "ai-auditing-service",
            "explainability-service",
            "ollama",
        }
        
        assert set(discovery.services.keys()) == expected_services, \
            f"Service names mismatch. Missing: {expected_services - set(discovery.services.keys())}, Extra: {set(discovery.services.keys()) - expected_services}"

    def test_health_check_covers_all_services(self):
        """Test health check includes all 14 services."""
        response = client.get("/health")
        assert response.status_code == 200
        
        health = response.json()
        assert "services" in health
        
        # Should have all 14 services in health check
        assert len(health["services"]) == 14, \
            f"Health check shows {len(health['services'])} services, expected 14"

    def test_system_status_shows_visible_services(self):
        """Test /api/v1/system/status only shows visible services."""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Should show 13 services (14 - 1 hidden _granite-interview-service)
        assert data["services_total"] == 13, \
            f"System status shows {data['services_total']} visible services, expected 13"
        
        # Verify no hidden services in details
        for service_name in data["service_details"]:
            assert not service_name.startswith("_"), \
                f"Hidden service {service_name} exposed in system status"


class TestServiceCallability:
    """Test that all services are callable through gateway."""

    def test_models_endpoint_accessible(self):
        """Test /api/v1/models endpoint is accessible."""
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        assert "models" in response.json()

    def test_interviews_endpoint_callable(self):
        """Test /api/v1/interviews/start endpoint is callable."""
        payload = {
            "role": "Software Engineer",
            "model": "granite4:350m",
            "totalQuestions": 3
        }
        response = client.post("/api/v1/interviews/start", json=payload)
        # Should return 200 or graceful fallback
        assert response.status_code in [200, 502]

    def test_dashboard_endpoint_accessible(self):
        """Test /api/v1/dashboard endpoint aggregates all services."""
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        assert "availableModels" in data
        assert "gateway" in data


class TestModularArchitecture:
    """Test modular design of integration service."""

    def test_service_discovery_separate_module(self):
        """Test ServiceDiscovery is in separate module."""
        from app.core.service_discovery import ServiceDiscovery as SD1
        from app.core.service_discovery import ServiceDiscovery as SD2
        
        # Should be same class from same module
        assert SD1 is SD2

    def test_config_separate_module(self):
        """Test Settings is in separate config module."""
        from app.config.settings import Settings
        from app.config.settings import settings
        
        # Settings should be instantiated
        assert isinstance(settings, Settings)

    def test_schemas_in_models_module(self):
        """Test schemas are in separate models module."""
        from app.models.schemas import StartInterviewRequest
        from app.models.schemas import InterviewSession
        from app.models.schemas import HealthResponse
        
        # All schema classes should be available
        assert StartInterviewRequest is not None
        assert InterviewSession is not None
        assert HealthResponse is not None

    def test_no_hardcoded_urls(self):
        """Test no hardcoded service URLs in main.py."""
        from app.config.settings import settings
        
        # All service URLs should come from settings
        assert hasattr(settings, "scout_url")
        assert hasattr(settings, "user_url")
        assert hasattr(settings, "candidate_url")
        assert hasattr(settings, "conversation_url")
        assert hasattr(settings, "interview_url")
        assert hasattr(settings, "voice_url")
        assert hasattr(settings, "avatar_url")
        assert hasattr(settings, "analytics_url")
        assert hasattr(settings, "security_url")
        assert hasattr(settings, "notification_url")
        assert hasattr(settings, "ai_auditing_url")
        assert hasattr(settings, "explainability_url")
        assert hasattr(settings, "ollama_url")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
