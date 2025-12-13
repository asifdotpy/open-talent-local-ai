# Desktop Integration Service - Quick Start Guide

## Phase 0A: Running the Gateway

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js (for Electron desktop app)
node --version
```

### Installation

```bash
# Navigate to service directory
cd /home/asif1/open-talent/microservices/desktop-integration-service

# Install Python dependencies
pip install -r requirements.txt
```

### Starting the Gateway

**Option 1: Direct Python**
```bash
python app/main.py
# Service runs on http://localhost:8009
```

**Option 2: Uvicorn (development)**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
# Auto-reload on code changes
# API docs: http://localhost:8009/docs
```

**Option 3: Docker**
```bash
docker build -t talent-desktop-integration .
docker run -d -p 8009:8009 talent-desktop-integration
```

### Quick Test

```bash
# Check gateway is running
curl http://localhost:8009/

# Get service health (without running microservices)
curl http://localhost:8009/health

# List available models (fallback)
curl http://localhost:8009/api/v1/models

# Interactive API docs
open http://localhost:8009/docs
```

### Running Tests

```bash
# All Phase 0A tests
python tests/test_phase_0a.py

# With pytest (if installed)
pytest tests/test_phase_0a.py -v
pytest tests/test_phase_0a.py -v --tb=short
```

### Starting Microservices (Phase 0B)

```bash
# From project root, start all microservices
docker-compose up -d

# Or individually:
docker-compose up -d granite-interview-service
docker-compose up -d conversation-service
docker-compose up -d voice-service
docker-compose up -d avatar-service
docker-compose up -d interview-service
docker-compose up -d analytics-service
docker-compose up -d ollama
```

### Debugging

```bash
# Check logs in real-time
tail -f /tmp/desktop-integration-service.log

# Enable debug logging
DEBUG=true python app/main.py

# Test individual service discovery
python -c "
import asyncio
from app.core.service_discovery import ServiceDiscovery

async def test():
    sd = ServiceDiscovery()
    health = await sd.check_all_services()
    print(health)

asyncio.run(test())
"
```

### Desktop App Integration

Once gateway is running, desktop app can connect:

```typescript
// From desktop-app/src/services/integration-client.ts
const client = new DesktopIntegrationClient('http://localhost:8009');

// Get available models
const models = await client.getAvailableModels();

// Start interview
const session = await client.startInterview('Software Engineer', 'granite-2b');

// Respond to question
const response = await client.respondToInterview(session.sessionId, 'My answer...');

// Get summary
const summary = await client.getInterviewSummary(session.sessionId);
```

### API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Gateway info |
| `/health` | GET | Service health |
| `/api/v1/system/status` | GET | System status |
| `/api/v1/models` | GET | List models |
| `/api/v1/models/select` | POST | Select model |
| `/api/v1/interviews/start` | POST | Start interview |
| `/api/v1/interviews/respond` | POST | Respond to question |
| `/api/v1/interviews/summary` | POST | Get summary |
| `/api/v1/dashboard` | GET | Dashboard data |

### Configuration

Edit `app/config/settings.py` or use environment variables:

```bash
# Service URLs
export GRANITE_INTERVIEW_SERVICE_URL=http://localhost:8000
export CONVERSATION_SERVICE_URL=http://localhost:8003
export VOICE_SERVICE_URL=http://localhost:8002
export AVATAR_SERVICE_URL=http://localhost:8001
export INTERVIEW_SERVICE_URL=http://localhost:8004
export ANALYTICS_SERVICE_URL=http://localhost:8007
export OLLAMA_URL=http://localhost:11434

# Timeouts
export SERVICE_TIMEOUT=30
export HEALTH_CHECK_TIMEOUT=5

# Port
export PORT=8009

# Start service
python app/main.py
```

### Common Issues

**Issue: "Connection refused" on startup**
- Microservices don't need to be running for Phase 0A
- Gateway will use fallback templates
- This is expected and correct

**Issue: "ModuleNotFoundError: No module named 'pydantic_settings'"**
```bash
pip install pydantic-settings
```

**Issue: "Address already in use :8009"**
```bash
# Kill existing process
lsof -i :8009 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port
PORT=8010 python app/main.py
```

**Issue: Tests failing**
```bash
# Make sure you're in the service directory
cd /home/asif1/open-talent/microservices/desktop-integration-service

# Run with full path
python tests/test_phase_0a.py

# Or with pytest
pip install pytest pytest-asyncio
pytest tests/test_phase_0a.py -v
```

### Next Steps

1. **Phase 0B (1.5 hours):**
   - Start microservices with docker-compose
   - Test health endpoint
   - Test models endpoint
   - Verify caching behavior

2. **Phase 0C (3 hours):**
   - Test interview start/respond/summary endpoints
   - Test conversation flow
   - Verify fallback behavior

3. **Phase 0D (2 hours):**
   - Docker integration tests
   - End-to-end testing with desktop app
   - Performance benchmarking

### Performance Baseline (No Services Running)

Expected response times with fallback templates:
```
GET /              : <10ms
GET /health        : 50-100ms (7 timeout attempts cached)
GET /api/v1/models : <10ms (returns FALLBACK_MODELS)
POST /interviews/start : <10ms (uses template)
```

With microservices running:
```
GET /health        : 100-500ms (all services reply)
GET /api/v1/models : 500-1000ms (queries granite + ollama)
POST /interviews/start : 2-5s (waits for AI model response)
```

### Documentation

- [API Reference](README.md) - Complete endpoint documentation
- [Phase 0A Completion](PHASE_0A_COMPLETION.md) - Implementation details
- [Architecture Overview](../../AGENTS.md) - System architecture

### Support

- Check `/health` endpoint for service status
- Review logs for detailed error information
- Test with `/docs` Swagger UI for interactive testing
- All endpoints return JSON with `error` field on failure

---

**Status:** Phase 0A Complete ✅  
**Version:** 0.1.0  
**Last Updated:** December 13, 2025
