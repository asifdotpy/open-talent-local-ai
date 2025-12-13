# TalentAI Platform - Integration Service Design Specification

> **Document Status**: Deep Scan Complete
> **Date**: December 13, 2025
> **Purpose**: Comprehensive integration service architecture for TalentAI microservices platform

---

## Executive Summary

This document provides a comprehensive analysis of the TalentAI microservices platform and proposes the architecture for a dedicated **Integration Service** that will serve as the central orchestration layer.

**Key Findings:**
- 14 active microservices with varying ports and responsibilities
- Existing integration via direct HTTP calls using `httpx.AsyncClient`
- No centralized service discovery or API gateway
- Integration tests exist (`integration_test.py`) but no integration service

**Proposed Solution:** Create an **Integration Service** that manages:
- Service discovery and health monitoring
- Request routing and load balancing
- Circuit breaker patterns for fault tolerance
- Centralized logging and request tracing
- Authentication/authorization gateway

---

## 1. Current Architecture Analysis

### 1.1 Service Inventory

| Service Name | Port | Type | Dependencies | Status |
|-------------|------|------|--------------|--------|
| **conversation-service** | 8003 | Orchestrator | ollama, interview endpoints | ✅ Active |
| **voice-service** | 8002, 8006 | Processing | STT/TTS, WebRTC | ✅ Active |
| **avatar-service** | 8001 | Rendering | Voice service integration | ✅ Active |
| **interview-service** | 8004 | Orchestrator | conversation, voice, avatar, analytics | ✅ Active |
| **scout-service** | 8005 | Discovery | conversation, voice | ✅ Active |
| **analytics-service** | 8007 | Analytics | conversation | ✅ Active |
| **candidate-service** | 8008 | Data | conversation | ✅ Active |
| **user-service** | 8001 (conflict!) | Auth | PostgreSQL | ✅ Active |
| **ollama** | 11434 | AI Model | N/A | ✅ Active |
| **project-service** | TBD | Management | TBD | 📋 Planned |
| **notification-service** | TBD | Notifications | TBD | 📋 Planned |
| **security-service** | TBD | Security | TBD | 📋 Planned |
| **explainability-service** | TBD | AI Explainability | interview | 📋 Planned |
| **ai-auditing-service** | TBD | Audit | interview | 📋 Planned |

> ⚠️ **PORT CONFLICT DETECTED**: `user-service` and `avatar-service` both use port 8001

### 1.2 Communication Patterns

#### Direct HTTP Communication
```python
# Pattern found across multiple services
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.post(
        "http://localhost:8002/webrtc/start",
        json=payload
    )
```

**Services using httpx.AsyncClient:**
- `interview-service/main.py` - Lines 578, 759
- `avatar-service/app/routes/avatar_routes.py` - Line 98
- `conversation-service/app/services/*.py` - Multiple instances
- `voice-service/webrtc_worker.py` - Lines 93, 146, 468

#### Docker Compose Service Discovery
```yaml
services:
  conversation-service:
    depends_on:
      - ollama
  interview-service:
    depends_on:
      - conversation-service
      - voice-service
      - avatar-service
      - analytics-service
```

### 1.3 Integration Gaps Identified

1. **No API Gateway**: Each service exposes its own port with no centralized entry point
2. **Hardcoded URLs**: Services use `http://localhost:PORT` instead of service discovery
3. **No Circuit Breaker**: Failed service calls propagate errors without retry/fallback
4. **Duplicated CORS**: Every service implements its own CORS middleware
5. **No Request Tracing**: No correlation IDs across service boundaries
6. **Port Management**: Manual port assignment risks conflicts
7. **No Rate Limiting**: Services unprotected from request storms
8. **Authentication Scattered**: No centralized auth/authz layer

---

## 2. Integration Patterns Observed

### 2.1 Orchestration Pattern (interview-service)
The `interview-service` acts as an orchestrator:
```
User Request
    → interview-service
        → voice-service (STT)
        → conversation-service (AI)
        → voice-service (TTS)
        → avatar-service (Video)
```

### 2.2 Integration Test Flow
From `integration_test.py`:
```python
# Test Dependencies
1. Check all services healthy
2. Create interview room → interview-service
3. Generate voice → avatar-service
4. Process STT/TTS → voice-service
5. Concurrent load testing
6. Error resilience testing
```

### 2.3 Common API Patterns

**Health Checks:**
- All services expose `/health` endpoint
- Return JSON with `status`, `service`, `version`, `components`

**Documentation:**
- `/docs` - Swagger UI
- `/redoc` - ReDoc
- `/api-docs` - Custom route listing
- `/openapi.json` - OpenAPI schema

**CORS Configuration:**
```python
allow_origins=[
    "http://localhost:3000",   # React frontend
    "http://localhost:5173",   # Vite dev
    "http://localhost:8080",   # Alt frontend
    "http://localhost:8081"
]
```

---

## 3. Proposed Integration Service Architecture

### 3.1 Service Overview

**Name**: `integration-service`
**Port**: `8000` (API Gateway port)
**Technology**: FastAPI + Python 3.11+
**Database**: Redis (service registry + caching)
**Dependencies**: All other microservices

### 3.2 Core Responsibilities

#### A. Service Discovery & Registry
- Maintain dynamic registry of all services
- Health monitoring with automatic failover
- Service endpoint resolution

#### B. API Gateway
- Single entry point for all client requests
- Route requests to appropriate microservice
- Transform requests/responses if needed

#### C. Circuit Breaker & Retry
- Detect failing services and prevent cascading failures
- Implement retry logic with exponential backoff
- Fallback responses when services unavailable

#### D. Request Correlation & Tracing
- Generate correlation IDs for request flows
- Distributed tracing across services
- Centralized logging aggregation

#### E. Authentication & Authorization Gateway
- JWT token validation
- Role-based access control (RBAC)
- API key management

#### F. Rate Limiting & Throttling
- Per-client rate limiting
- Service-level quotas
- Burst protection

---

## 4. Integration Service Implementation Plan

### 4.1 Directory Structure

```
microservices/
└── integration-service/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                    # FastAPI app
    │   ├── config/
    │   │   ├── settings.py            # Configuration
    │   │   └── service_registry.yaml  # Service definitions
    │   ├── core/
    │   │   ├── service_discovery.py   # Service registry
    │   │   ├── circuit_breaker.py     # Fault tolerance
    │   │   ├── request_router.py      # Dynamic routing
    │   │   └── correlation.py         # Request tracing
    │   ├── middleware/
    │   │   ├── auth.py                # Authentication
    │   │   ├── rate_limit.py          # Rate limiting
    │   │   └── logging.py             # Request logging
    │   ├── routes/
    │   │   ├── gateway.py             # Main gateway routes
    │   │   ├── admin.py               # Admin endpoints
    │   │   └── health.py              # Health checks
    │   └── models/
    │       ├── service.py             # Service model
    │       └── request.py             # Request models
    ├── tests/
    │   ├── test_discovery.py
    │   ├── test_circuit_breaker.py
    │   └── test_routing.py
    ├── requirements.txt
    ├── Dockerfile
    ├── README.md
    └── .env.example
```

### 4.2 Service Registry Schema

```yaml
# config/service_registry.yaml
services:
  - name: conversation-service
    host: conversation-service
    port: 8003
    protocol: http
    health_endpoint: /health
    base_path: /api/v1/conversation
    timeout: 10.0
    retry_policy:
      max_attempts: 3
      backoff: exponential

  - name: voice-service
    host: voice-service
    port: 8002
    protocol: http
    health_endpoint: /health
    base_path: /voice
    timeout: 30.0
    retry_policy:
      max_attempts: 2
      backoff: fixed

  - name: interview-service
    host: interview-service
    port: 8004
    protocol: http
    health_endpoint: /health
    base_path: /api/v1
    timeout: 15.0
    retry_policy:
      max_attempts: 3
      backoff: exponential

  # ... other services
```

### 4.3 Core Components

#### A. Service Discovery Implementation

```python
# app/core/service_discovery.py
import asyncio
from typing import Dict, Optional
import httpx
from app.models.service import Service, ServiceStatus

class ServiceDiscovery:
    def __init__(self, registry_config: dict):
        self.services: Dict[str, Service] = {}
        self.health_check_interval = 30  # seconds
        self._load_registry(registry_config)

    async def get_service_endpoint(self, service_name: str) -> Optional[str]:
        """Get healthy endpoint for service, returns None if unavailable"""
        service = self.services.get(service_name)
        if not service or service.status != ServiceStatus.HEALTHY:
            return None
        return f"{service.protocol}://{service.host}:{service.port}"

    async def health_check_loop(self):
        """Continuous health monitoring"""
        while True:
            await self._check_all_services()
            await asyncio.sleep(self.health_check_interval)

    async def _check_all_services(self):
        """Check health of all registered services"""
        tasks = [self._check_service(svc) for svc in self.services.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
```

#### B. Circuit Breaker Implementation

```python
# app/core/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds before retry
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

#### C. Request Router With Load Balancing

```python
# app/core/request_router.py
import httpx
from typing import Optional
from app.core.service_discovery import ServiceDiscovery
from app.core.circuit_breaker import CircuitBreaker

class RequestRouter:
    def __init__(self, discovery: ServiceDiscovery):
        self.discovery = discovery
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

    async def route_request(
        self,
        service_name: str,
        method: str,
        path: str,
        **kwargs
    ):
        """Route request to service with circuit breaker protection"""
        # Get circuit breaker for this service
        breaker = self._get_circuit_breaker(service_name)

        # Get service endpoint
        endpoint = await self.discovery.get_service_endpoint(service_name)
        if not endpoint:
            raise ServiceUnavailable(f"{service_name} is unavailable")

        # Build full URL
        url = f"{endpoint}{path}"

        # Execute with circuit breaker
        return await breaker.call(
            self._make_request,
            method, url, **kwargs
        )

    async def _make_request(self, method: str, url: str, **kwargs):
        """Actual HTTP request execution"""
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response
```

### 4.4 API Gateway Routes

```python
# app/main.py
from fastapi import FastAPI, Request, Depends
from app.core.service_discovery import ServiceDiscovery
from app.core.request_router import RequestRouter

app = FastAPI(title="TalentAI Integration Service")

# Initialize core components
service_discovery = ServiceDiscovery(config)
request_router = RequestRouter(service_discovery)

@app.on_event("startup")
async def startup():
    """Start health monitoring"""
    asyncio.create_task(service_discovery.health_check_loop())

# Gateway route - forwards to appropriate service
@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_route(
    service_name: str,
    path: str,
    request: Request
):
    """Dynamic routing to microservices"""
    # Extract request details
    method = request.method
    headers = dict(request.headers)
    body = await request.body() if method in ["POST", "PUT", "PATCH"] else None
    query_params = dict(request.query_params)

    # Add correlation ID
    correlation_id = headers.get("X-Correlation-ID", str(uuid.uuid4()))
    headers["X-Correlation-ID"] = correlation_id

    # Route to service
    response = await request_router.route_request(
        service_name=service_name,
        method=method,
        path=f"/{path}",
        headers=headers,
        content=body,
        params=query_params
    )

    return response.json()
```

### 4.5 Admin Endpoints

```python
# app/routes/admin.py

@app.get("/admin/services")
async def list_services():
    """List all registered services and their status"""
    return service_discovery.get_all_services()

@app.get("/admin/services/{service_name}/health")
async def check_service_health(service_name: str):
    """Check specific service health"""
    return await service_discovery.check_service(service_name)

@app.post("/admin/services/{service_name}/circuit-reset")
async def reset_circuit_breaker(service_name: str):
    """Manually reset circuit breaker for service"""
    request_router.reset_circuit_breaker(service_name)
    return {"message": f"Circuit breaker reset for {service_name}"}

@app.get("/admin/metrics")
async def get_metrics():
    """Get integration service metrics"""
    return {
        "total_requests": metrics.total_requests,
        "failed_requests": metrics.failed_requests,
        "avg_response_time": metrics.avg_response_time,
        "circuit_breakers_open": len([b for b in circuit_breakers.values() if b.state == CircuitState.OPEN])
    }
```

---

## 5. Integration with Existing Services

### 5.1 Migration Strategy

**Phase 1: Integration Service Setup**
1. Create `integration-service` directory structure
2. Implement service discovery with existing services
3. Deploy integration service (port 8000)
4. Test health monitoring

**Phase 2: Gradual Migration**
1. Update frontend to call integration service instead of direct services
2. Keep direct service access for backward compatibility
3. Add request logging and monitoring

**Phase 3: Full Migration**
1. Update all inter-service calls to use integration service
2. Disable direct service access from external clients
3. Enable authentication at integration service level

### 5.2 Docker Compose Integration

```yaml
# Add to docker-compose.yml
services:
  integration-service:
    build:
      context: integration-service
      dockerfile: Dockerfile
    container_name: talent-integration-service
    ports:
      - "8000:8000"
    env_file:
      - integration-service/.env
    environment:
      - PYTHONPATH=/app
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - conversation-service
      - voice-service
      - avatar-service
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: talent-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

---

## 6. Benefits of Integration Service

### 6.1 Immediate Benefits
✅ **Single Entry Point**: One API gateway for all services
✅ **Service Discovery**: Dynamic service resolution
✅ **Fault Tolerance**: Circuit breakers prevent cascading failures
✅ **Observability**: Centralized logging and request tracing
✅ **Security**: Unified authentication/authorization layer

### 6.2 Long-term Benefits
✅ **Scalability**: Easy to add new services
✅ **Flexibility**: Services can move/scale independently
✅ **Monitoring**: Comprehensive metrics and alerting
✅ **Testing**: Easier integration testing
✅ **Documentation**: Unified API documentation

---

## 7. Implementation Checklist

- [ ] Create `integration-service` directory structure
- [ ] Implement service discovery component
- [ ] Implement circuit breaker pattern
- [ ] Implement request router
- [ ] Add correlation ID middleware
- [ ] Add rate limiting middleware
- [ ] Add authentication middleware
- [ ] Create admin endpoints
- [ ] Write comprehensive tests
- [ ] Update docker-compose.yml
- [ ] Update existing services to use integration service
- [ ] Create monitoring dashboards
- [ ] Document migration guide

---

## 8. Next Steps

1. **Review this specification** with the team
2. **Approve the architecture** and design decisions
3. **Create integration-service skeleton** with core components
4. **Implement service discovery** first (most critical)
5. **Add circuit breaker** for fault tolerance
6. **Gradually migrate** existing services

---

**Document Version**: 1.0
**Last Updated**: December 13, 2025
**Author**: AI Engineering Team
**Status**: Ready for Review
