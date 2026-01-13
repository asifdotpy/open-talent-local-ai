# Desktop Integration Service

**Service Name:** desktop-integration-service
**Port:** 8009
**Version:** 1.0.0
**Purpose:** Unified API gateway for OpenTalent Desktop App integration

## Overview

The Desktop Integration Service acts as a central API gateway and orchestration layer between the OpenTalent desktop application and the distributed microservices architecture. It provides a unified, simplified API interface for desktop clients while managing complex backend service interactions.

## Architecture Role

```
OpenTalent Desktop App (Electron)
         ↓
Desktop Integration Service (Port 8009)
    ↓           ↓           ↓
Granite      Interview   Analytics
Interview    Service     Service
Service      (8004)      (8007)
(Custom)
    ↓           ↓           ↓
Conversation Voice      Avatar
Service      Service    Service
(8003)       (8002)     (8001)
```

## Key Features

### 1. API Gateway & Routing
- Single entry point for desktop app
- Intelligent request routing to appropriate microservices
- Service discovery and health monitoring
- Load balancing across service instances

### 2. Data Aggregation
- Combines data from multiple services into unified responses
- Reduces desktop app API calls (1 request vs. 5+ requests)
- Optimized payload structures for desktop use cases

### 3. Desktop-Specific Optimizations
- Lightweight responses for bandwidth efficiency
- Caching layer for frequently accessed data
- Offline data synchronization support
- Desktop-friendly error messages

### 4. Security & Rate Limiting
- API key management for desktop clients
- Request rate limiting per client
- Input validation and sanitization
- CORS configuration for Electron apps

### 5. Model Management
- Unified model configuration across services
- Model availability checking
- Hardware requirement validation
- Automatic model selection based on system specs

### 6. Interview Orchestration
- End-to-end interview flow management
- Question generation with context
- Response analysis and scoring
- Interview session persistence

## API Endpoints

### Health & Status

#### `GET /health`
```json
{
  "status": "healthy",
  "services": {
    "granite_interview": "healthy",
    "conversation": "healthy",
    "voice": "healthy",
    "avatar": "healthy",
    "interview": "healthy"
  }
}
```

#### `GET /api/v1/system/status`
```json
{
  "desktop_integration_service": "1.0.0",
  "available_services": ["granite-interview", "conversation", "voice"],
  "models_ready": true,
  "ollama_status": "online"
}
```

### Model Management

#### `GET /api/v1/models`
List all available models across all services.

```json
{
  "models": [
    {
      "id": "vetta-granite-2b-gguf-v4",
      "name": "Vetta Granite 2B (Interview-Trained)",
      "provider": "granite-interview-service",
      "size": "1.2GB",
      "ram_required": "8-12GB",
      "status": "available",
      "quality": "excellent",
      "use_case": "interview_generation"
    },
    {
      "id": "llama3.2:1b",
      "name": "Llama 3.2 1B (Fallback)",
      "provider": "ollama",
      "size": "600MB",
      "ram_required": "4-6GB",
      "status": "loaded",
      "quality": "good",
      "use_case": "general_chat"
    }
  ]
}
```

#### `POST /api/v1/models/select`
Automatically select best model based on system specs.

```json
Request:
{
  "available_ram_gb": 12,
  "use_case": "interview",
  "prefer_quality": true
}

Response:
{
  "selected_model": "vetta-granite-2b-gguf-v4",
  "reason": "Best quality for 12GB RAM system",
  "estimated_performance": {
    "first_response": "2-3s",
    "subsequent": "1-2s"
  }
}
```

### Interview Management

#### `POST /api/v1/interviews/start`
Start a new interview session.

```json
Request:
{
  "role": "Software Engineer",
  "model": "vetta-granite-2b-gguf-v4",
  "candidate_profile": {
    "experience_years": 3,
    "skills": ["Python", "JavaScript", "React"]
  },
  "options": {
    "total_questions": 5,
    "difficulty": "intermediate"
  }
}

Response:
{
  "session_id": "interview_abc123",
  "first_question": "Hello, I'm OpenTalent Interviewer. Question 1: Can you describe your experience with Python?",
  "context": {
    "current_question": 1,
    "total_questions": 5
  },
  "metadata": {
    "model_used": "vetta-granite-2b-gguf-v4",
    "latency_ms": 2800
  }
}
```

#### `POST /api/v1/interviews/{session_id}/respond`
Submit candidate response and get next question.

```json
Request:
{
  "response": "I have 3 years of Python experience, working primarily on backend APIs and data processing pipelines."
}

Response:
{
  "session_id": "interview_abc123",
  "next_question": "That's great. Question 2: Can you walk me through your approach to debugging a slow API endpoint?",
  "analysis": {
    "relevance": 0.92,
    "completeness": 0.85,
    "technical_depth": 0.78
  },
  "context": {
    "current_question": 2,
    "total_questions": 5
  },
  "metadata": {
    "latency_ms": 1600
  }
}
```

#### `GET /api/v1/interviews/{session_id}/summary`
Get interview summary and assessment.

```json
{
  "session_id": "interview_abc123",
  "role": "Software Engineer",
  "questions_asked": 5,
  "responses_given": 5,
  "overall_score": 8.2,
  "strengths": [
    "Strong technical knowledge",
    "Good communication skills",
    "Practical problem-solving approach"
  ],
  "areas_for_improvement": [
    "Could provide more specific examples",
    "Expand on edge case handling"
  ],
  "detailed_analysis": {
    "technical_knowledge": 8.5,
    "problem_solving": 8.0,
    "communication": 8.3
  },
  "conversation_history": [
    {
      "role": "assistant",
      "content": "Question 1: ...",
      "timestamp": "2025-12-14T10:00:00Z"
    },
    {
      "role": "user",
      "content": "I have 3 years...",
      "timestamp": "2025-12-14T10:01:30Z"
    }
  ]
}
```

### Aggregate Endpoints

#### `GET /api/v1/dashboard`
Get complete dashboard data in one request.

```json
{
  "system_status": {
    "services_healthy": 5,
    "services_total": 5,
    "models_loaded": 2
  },
  "available_models": [...],
  "recent_interviews": [
    {
      "session_id": "interview_xyz",
      "role": "Product Manager",
      "timestamp": "2025-12-14T09:00:00Z",
      "score": 7.8
    }
  ],
  "hardware_info": {
    "cpu_usage": "45%",
    "ram_usage": "8.2GB / 16GB",
    "gpu_available": true
  }
}
```

## Service Dependencies

**Required Services:**
- `granite-interview-service` (port 8005) - Custom Granite models for interview intelligence
- `conversation-service` (port 8003) - Conversation orchestration
- `ollama` (port 11434) - Model serving infrastructure

**Optional Services:**
- `voice-service` (port 8002) - TTS/STT capabilities
- `avatar-service` (port 8001) - 3D avatar rendering
- `analytics-service` (port 8007) - Usage analytics
- `interview-service` (port 8004) - Legacy interview management

## Configuration

### Environment Variables

```bash
# Service Configuration
PORT=8009
HOST=0.0.0.0
DEBUG=false
WORKERS=4

# Service Discovery
GRANITE_INTERVIEW_SERVICE_URL=http://granite-interview-service:8000
CONVERSATION_SERVICE_URL=http://conversation-service:80
VOICE_SERVICE_URL=http://voice-service:8002
AVATAR_SERVICE_URL=http://avatar-service:80
INTERVIEW_SERVICE_URL=http://interview-service:80
ANALYTICS_SERVICE_URL=http://analytics-service:80
OLLAMA_URL=http://ollama:11434

# Caching
REDIS_URL=redis://redis:6379
CACHE_TTL_SECONDS=300

# Security
API_KEY_REQUIRED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Features
ENABLE_VOICE=true
ENABLE_AVATAR=true
ENABLE_ANALYTICS=true
OFFLINE_MODE_SUPPORT=true
```

## Technology Stack

- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11+
- **Async:** asyncio, httpx for async HTTP
- **Caching:** Redis (optional)
- **Monitoring:** Prometheus metrics
- **Documentation:** OpenAPI/Swagger

## Development

### Prerequisites

```bash
# Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt

# Start dependent services
docker-compose up -d granite-interview-service conversation-service ollama
```

### Local Development

```bash
# Start service
python app/main.py

# Service will be available at
# http://localhost:8009

# API documentation at
# http://localhost:8009/docs
```

### Testing

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# End-to-end tests
pytest tests/e2e

# Test coverage
pytest --cov=app tests/
```

## Docker Deployment

### Build Image

```bash
docker build -t talent-desktop-integration-service .
```

### Run Container

```bash
docker run -d \
  --name talent-desktop-integration \
  -p 8009:8009 \
  -e GRANITE_INTERVIEW_SERVICE_URL=http://host.docker.internal:8000 \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  talent-desktop-integration-service
```

### Docker Compose

```yaml
desktop-integration-service:
  build:
    context: desktop-integration-service
    dockerfile: Dockerfile
  container_name: talent-desktop-integration
  ports:
    - "8009:8009"
  environment:
    - GRANITE_INTERVIEW_SERVICE_URL=http://granite-interview-service:8000
    - CONVERSATION_SERVICE_URL=http://conversation-service:80
    - OLLAMA_URL=http://ollama:11434
  depends_on:
    - granite-interview-service
    - conversation-service
    - ollama
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8009/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  restart: unless-stopped
```

## API Client (Desktop App)

### TypeScript Client Example

```typescript
// desktop-app/src/services/desktop-integration-client.ts
class DesktopIntegrationClient {
  private baseURL = 'http://localhost:8009/api/v1';

  async getAvailableModels() {
    const response = await fetch(`${this.baseURL}/models`);
    return response.json();
  }

  async startInterview(role: string, model: string) {
    const response = await fetch(`${this.baseURL}/interviews/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, model })
    });
    return response.json();
  }

  async submitResponse(sessionId: string, response: string) {
    const res = await fetch(
      `${this.baseURL}/interviews/${sessionId}/respond`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response })
      }
    );
    return res.json();
  }
}
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API Latency (p50) | < 100ms | Excluding model inference |
| API Latency (p95) | < 500ms | Excluding model inference |
| Model Inference (first) | < 3s | Via granite-interview-service |
| Model Inference (cached) | < 2s | Via granite-interview-service |
| Concurrent Requests | 100+ | Per service instance |
| Memory Usage | < 500MB | Per service instance |
| Cache Hit Rate | > 60% | For frequently accessed data |

## Monitoring & Observability

### Health Checks

```bash
# Service health
curl http://localhost:8009/health

# Detailed status
curl http://localhost:8009/api/v1/system/status
```

### Metrics (Prometheus)

```
# Request metrics
desktop_integration_requests_total
desktop_integration_request_duration_seconds

# Service health metrics
desktop_integration_service_up{service="granite-interview"}
desktop_integration_service_up{service="conversation"}

# Model metrics
desktop_integration_model_inference_duration_seconds
desktop_integration_model_inference_total
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Granite interview service is currently unavailable",
    "details": {
      "service": "granite-interview-service",
      "last_healthy": "2025-12-14T10:00:00Z"
    },
    "suggestions": [
      "Check if docker services are running",
      "Verify network connectivity",
      "Try again in a few moments"
    ],
    "fallback": {
      "available": true,
      "provider": "ollama",
      "model": "llama3.2:1b"
    }
  }
}
```

## Security Considerations

1. **API Authentication** - Optional API key validation
2. **Rate Limiting** - Per-client request limits
3. **Input Validation** - All user inputs sanitized
4. **CORS** - Configured for Electron app origins
5. **No Sensitive Data** - Interview content not stored by default
6. **Local-First** - All processing happens locally

## Roadmap

### Phase 1 (Current)
- ✅ Basic API gateway functionality
- ✅ Model management endpoints
- ✅ Interview orchestration
- ✅ Service health monitoring

### Phase 2 (Future)
- [ ] Advanced caching with Redis
- [ ] WebSocket support for real-time updates
- [ ] Batch operations for multiple interviews
- [ ] Voice/avatar integration
- [ ] Advanced analytics aggregation

### Phase 3 (Future)
- [ ] Multi-tenant support
- [ ] Interview recording storage
- [ ] Advanced rate limiting (per feature)
- [ ] Service mesh integration
- [ ] GraphQL API alternative

## Support

**Documentation:** This README
**API Docs:** http://localhost:8009/docs
**Issues:** GitHub Issues
**Contact:** dev@opentalent.ai

---

**Last Updated:** December 13, 2025
**Maintainer:** OpenTalent Core Team
**License:** MIT

---

## Phase 0A Implementation Status: ✅ COMPLETE

**Completed Deliverables:**
- ✅ Settings module (`app/config/settings.py`) - 60 lines
  - Environment configuration with pydantic BaseSettings
  - 7 service URLs configurable
  - Service timeouts, cache TTLs, feature flags

- ✅ Service Discovery (`app/core/service_discovery.py`) - 160 lines
  - ServiceDiscovery class for health monitoring
  - ServiceHealthCache for 5-second caching
  - Parallel health checks on 7 microservices
  - Status aggregation: online/degraded/offline

- ✅ Pydantic Models (`app/models/schemas.py`) - 120 lines
  - 10 validation models (Message, InterviewSession, ModelInfo, etc.)
  - Desktop app contract matching (InterviewSession)
  - Type safety and auto-documentation

- ✅ FastAPI Application (`app/main.py`) - 600 lines
  - 6 endpoint groups: health, models, interviews, dashboard
  - CORS middleware configured
  - Async HTTP client pooling
  - Fallback templates for offline operation

- ✅ Test Suite (`tests/test_phase_0a.py`) - 300+ lines
  - Settings validation tests
  - Pydantic model contract tests
  - App structure and endpoint tests
  - Integration tests with TestClient

**Architecture:**
```
OpenTalent Desktop App (Electron)
         ↓ HTTP
Desktop Integration Service (port 8009)
    ↓         ↓         ↓         ↓
Granite    Voice    Avatar   Interview
Interview  Service  Service  Service
(8005)     (8002)   (8001)   (8004)
    ↓         ↓         ↓         ↓
Conversation Service (8003) & Ollama (11434)
```

**Testing Phase 0A:**
```bash
cd microservices/desktop-integration-service
python tests/test_phase_0a.py
```

**Roadmap:**
- Phase 0B: Health & Models Endpoints Testing (1.5 hrs)
- Phase 0C: Interview Orchestration Testing (3 hrs)
- Phase 0D: Docker Integration & E2E Testing (2 hrs)

**Status Updated:** December 13, 2025
