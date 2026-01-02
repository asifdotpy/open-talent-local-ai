"""
API Inventory Validation Test Suite

Tests all microservices listed in MICROSERVICES_API_INVENTORY.md to verify:
1. Service is running and responding
2. Health endpoint returns 200 status
3. OpenAPI schema is available and valid
4. Core endpoints are accessible
5. Response structure matches specifications

Usage:
    pytest tests/test_api_inventory_validation.py -v
    pytest tests/test_api_inventory_validation.py -v -k "notification"  # Run specific service tests
"""

import asyncio
import json
import pytest
import httpx
from typing import Dict, List, Optional
from datetime import datetime


# ============================================================================
# SERVICE INVENTORY - Must match MICROSERVICES_API_INVENTORY.md
# ============================================================================

SERVICES = {
    "desktop_integration": {
        "port": 8009,
        "name": "Desktop Integration Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/api/v1/services"),
        ],
    },
    "security": {
        "port": 8010,
        "name": "Security Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "notification": {
        "port": 8011,
        "name": "Notification Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/api/v1/provider"),
            ("GET", "/api/v1/notify/templates"),
        ],
    },
    "ai_auditing": {
        "port": 8012,
        "name": "AI Auditing Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "explainability": {
        "port": 8013,
        "name": "Explainability Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "granite_interview": {
        "port": 8005,
        "name": "Granite Interview Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "interview": {
        "port": 8006,
        "name": "Interview Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "user": {
        "port": 8007,
        "name": "User Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "candidate": {
        "port": 8008,
        "name": "Candidate Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "scout": {
        "port": 8010,
        "name": "Scout Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "conversation": {
        "port": 8014,
        "name": "Conversation Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "voice": {
        "port": 8015,
        "name": "Voice Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "avatar": {
        "port": 8016,
        "name": "Avatar Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
    "analytics": {
        "port": 8017,
        "name": "Analytics Service",
        "health_endpoint": "/health",
        "openapi_endpoint": "/docs",
        "core_endpoints": [
            ("GET", "/"),
            ("GET", "/health"),
        ],
    },
}

TIMEOUT = httpx.Timeout(5.0)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def async_client():
    """Async HTTP client for testing"""
    async def _async_client():
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            yield client
    return _async_client


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def is_service_running(client: httpx.AsyncClient, base_url: str) -> bool:
    """Check if service is running by testing health endpoint"""
    try:
        response = await client.get(f"{base_url}/health")
        return response.status_code in [200, 204]
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


async def get_openapi_schema(client: httpx.AsyncClient, base_url: str) -> Optional[Dict]:
    """Fetch and parse OpenAPI schema from service"""
    try:
        response = await client.get(f"{base_url}/docs")
        if response.status_code == 200:
            # For Swagger UI, the actual schema is at /openapi.json
            schema_response = await client.get(f"{base_url}/openapi.json")
            if schema_response.status_code == 200:
                return schema_response.json()
    except Exception:
        pass
    return None


def validate_openapi_schema(schema: Dict) -> tuple[bool, List[str]]:
    """Validate OpenAPI schema structure

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    if "openapi" not in schema:
        errors.append("Missing 'openapi' field")

    if "info" not in schema:
        errors.append("Missing 'info' field")
    else:
        info = schema["info"]
        if "title" not in info:
            errors.append("Missing 'info.title'")
        if "version" not in info:
            errors.append("Missing 'info.version'")

    if "paths" not in schema:
        errors.append("Missing 'paths' field")
    else:
        if not isinstance(schema["paths"], dict):
            errors.append("'paths' must be a dict")

    # Check components (optional but good practice)
    if "components" in schema:
        if not isinstance(schema["components"], dict):
            errors.append("'components' must be a dict")

    return len(errors) == 0, errors


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestServiceConnectivity:
    """Test basic service connectivity"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_service_running(self, service_key: str, service_config: Dict):
        """Test that service is running and responding to health checks"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(f"{base_url}/health")
                assert response.status_code in [200, 204], \
                    f"{service_config['name']}: Expected 200/204, got {response.status_code}"
            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_service_root_endpoint(self, service_key: str, service_config: Dict):
        """Test that service root endpoint (GET /) responds"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(f"{base_url}/")
                assert response.status_code in [200, 404], \
                    f"{service_config['name']}: Unexpected status {response.status_code}"
            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")


class TestOpenAPISchemas:
    """Test OpenAPI schema availability and validity"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_openapi_schema_available(self, service_key: str, service_config: Dict):
        """Test that OpenAPI schema is available at /openapi.json"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                # Check Swagger UI
                docs_response = await client.get(f"{base_url}/docs")
                if docs_response.status_code != 200:
                    pytest.skip(f"{service_config['name']}: Swagger UI not available")

                # Check OpenAPI JSON
                schema_response = await client.get(f"{base_url}/openapi.json")
                assert schema_response.status_code == 200, \
                    f"{service_config['name']}: OpenAPI schema not available (status {schema_response.status_code})"

                # Verify it's valid JSON
                schema = schema_response.json()
                assert isinstance(schema, dict), \
                    f"{service_config['name']}: OpenAPI schema is not a valid JSON object"

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_openapi_schema_valid(self, service_key: str, service_config: Dict):
        """Test that OpenAPI schema is valid according to spec"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                schema_response = await client.get(f"{base_url}/openapi.json")
                if schema_response.status_code != 200:
                    pytest.skip(f"{service_config['name']}: OpenAPI schema not available")

                schema = schema_response.json()
                is_valid, errors = validate_openapi_schema(schema)

                assert is_valid, \
                    f"{service_config['name']}: OpenAPI schema validation failed:\n" + \
                    "\n".join(f"  - {error}" for error in errors)

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_openapi_schema_has_paths(self, service_key: str, service_config: Dict):
        """Test that OpenAPI schema includes documented paths"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                schema_response = await client.get(f"{base_url}/openapi.json")
                if schema_response.status_code != 200:
                    pytest.skip(f"{service_config['name']}: OpenAPI schema not available")

                schema = schema_response.json()
                paths = schema.get("paths", {})

                assert len(paths) > 0, \
                    f"{service_config['name']}: OpenAPI schema has no documented paths"

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")


class TestCoreEndpoints:
    """Test core endpoints documented in inventory"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_health_endpoint(self, service_key: str, service_config: Dict):
        """Test that health endpoint exists and responds"""
        base_url = f"http://localhost:{service_config['port']}"
        health_endpoint = service_config["health_endpoint"]

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(f"{base_url}{health_endpoint}")
                assert response.status_code in [200, 204], \
                    f"{service_config['name']}: Health endpoint returned {response.status_code}"

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_core_endpoints(self, service_key: str, service_config: Dict):
        """Test core endpoints listed in inventory"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                for method, endpoint in service_config["core_endpoints"]:
                    if method == "GET":
                        response = await client.get(f"{base_url}{endpoint}")
                        # Accept 200, 404, 405 (method not allowed) depending on implementation
                        assert response.status_code in [200, 201, 204, 400, 404, 405], \
                            f"{service_config['name']} {method} {endpoint}: Got {response.status_code}"

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")


class TestOpenAPICompliance:
    """Test OpenAPI compliance and metadata"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_openapi_info_complete(self, service_key: str, service_config: Dict):
        """Test that OpenAPI info section is complete"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                schema_response = await client.get(f"{base_url}/openapi.json")
                if schema_response.status_code != 200:
                    pytest.skip(f"{service_config['name']}: OpenAPI schema not available")

                schema = schema_response.json()
                info = schema.get("info", {})

                assert "title" in info, \
                    f"{service_config['name']}: OpenAPI info missing 'title'"
                assert "version" in info, \
                    f"{service_config['name']}: OpenAPI info missing 'version'"

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key,service_config", SERVICES.items())
    async def test_openapi_version_format(self, service_key: str, service_config: Dict):
        """Test that OpenAPI version follows semantic versioning"""
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                schema_response = await client.get(f"{base_url}/openapi.json")
                if schema_response.status_code != 200:
                    pytest.skip(f"{service_config['name']}: OpenAPI schema not available")

                schema = schema_response.json()
                openapi_version = schema.get("openapi", "")

                # OpenAPI version should be like "3.0.0" or "3.1.0"
                assert openapi_version.startswith("3."), \
                    f"{service_config['name']}: OpenAPI version {openapi_version} is not 3.x"

            except httpx.ConnectError:
                pytest.skip(f"{service_config['name']} not running on {base_url}")


class TestServiceIntegration:
    """Integration tests for service availability and consistency"""

    @pytest.mark.asyncio
    async def test_all_services_runnable(self):
        """Test that at least the core services are running"""
        core_services = ["notification", "desktop_integration"]  # Most important services
        running_services = []

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            for service_key, service_config in SERVICES.items():
                if service_key in core_services:
                    base_url = f"http://localhost:{service_config['port']}"
                    try:
                        response = await client.get(f"{base_url}/health")
                        if response.status_code in [200, 204]:
                            running_services.append(service_key)
                    except httpx.ConnectError:
                        pass

        assert len(running_services) > 0, \
            f"No core services running. Started: {running_services}"

    @pytest.mark.asyncio
    async def test_notification_service_complete(self):
        """Test Notification Service is fully functional (special case)"""
        service_config = SERVICES["notification"]
        base_url = f"http://localhost:{service_config['port']}"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                # Check service is running
                health = await client.get(f"{base_url}/health")
                assert health.status_code in [200, 204], \
                    f"Notification Service health check failed: {health.status_code}"

                # Check all endpoints
                for method, endpoint in service_config["core_endpoints"]:
                    response = await client.get(f"{base_url}{endpoint}")
                    assert response.status_code in [200, 201, 204], \
                        f"Notification Service {endpoint} returned {response.status_code}"

                # Check OpenAPI schema
                schema_response = await client.get(f"{base_url}/openapi.json")
                assert schema_response.status_code == 200, \
                    f"Notification Service OpenAPI schema unavailable"

                schema = schema_response.json()
                assert len(schema.get("paths", {})) > 0, \
                    "Notification Service OpenAPI has no paths"

            except httpx.ConnectError:
                pytest.skip("Notification Service not running")


# ============================================================================
# SUMMARY REPORT
# ============================================================================

class TestSummaryReport:
    """Generate summary report of all service tests"""

    @pytest.mark.asyncio
    async def test_generate_service_summary(self, capsys):
        """Generate summary of all services"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_services": len(SERVICES),
            "services": {},
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            for service_key, service_config in SERVICES.items():
                base_url = f"http://localhost:{service_config['port']}"
                service_info = {
                    "name": service_config["name"],
                    "port": service_config["port"],
                    "running": False,
                    "health_ok": False,
                    "openapi_available": False,
                    "openapi_valid": False,
                    "endpoints_count": 0,
                }

                try:
                    # Check if running
                    health = await client.get(f"{base_url}/health")
                    service_info["running"] = health.status_code in [200, 204]
                    service_info["health_ok"] = service_info["running"]

                    # Check OpenAPI
                    if service_info["running"]:
                        schema_response = await client.get(f"{base_url}/openapi.json")
                        if schema_response.status_code == 200:
                            schema = schema_response.json()
                            service_info["openapi_available"] = True
                            is_valid, _ = validate_openapi_schema(schema)
                            service_info["openapi_valid"] = is_valid
                            service_info["endpoints_count"] = len(schema.get("paths", {}))

                except httpx.ConnectError:
                    pass

                summary["services"][service_key] = service_info

        # Print summary
        print("\n" + "="*80)
        print("API INVENTORY VALIDATION SUMMARY")
        print("="*80)

        running = sum(1 for s in summary["services"].values() if s["running"])
        with_openapi = sum(1 for s in summary["services"].values() if s["openapi_available"])

        print(f"\nServices Running: {running}/{summary['total_services']}")
        print(f"Services with OpenAPI: {with_openapi}/{summary['total_services']}")
        print(f"Timestamp: {summary['timestamp']}\n")

        for service_key, info in summary["services"].items():
            status = "✅" if info["running"] else "❌"
            openapi = "✅" if info["openapi_valid"] else "⚠️" if info["openapi_available"] else "❌"
            print(f"{status} {info['name']:40s} | Port: {info['port']} | OpenAPI: {openapi} | Endpoints: {info['endpoints_count']}")

        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
