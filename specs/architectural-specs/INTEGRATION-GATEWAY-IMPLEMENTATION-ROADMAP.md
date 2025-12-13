# Integration Gateway Implementation Roadmap

> **Scope**: Lean gateway for SelectUSA demo (Phase 0)
> **Timeline**: Days 5-6 (Dec 14-15, 2025)
> **Duration**: ~8-10 hours
> **Port**: 8009
> **Architecture**: Desktop → Gateway → Microservices

---

## Overview

Build a lightweight FastAPI gateway that sits between the Electron desktop app and backend microservices. This is **not** the full enterprise integration service—it's the minimal viable gateway to get the demo working reliably.

### Key Constraints
- Local-only (no cloud, no auth required)
- Desktop app already built with 96 tests passing
- Microservices already running (conversation, voice, avatar, interview, analytics, granite-interview, ollama)
- Must degrade gracefully when services unavailable
- Must match existing `InterviewSession` contract

---

## Phase 0A: Gateway Setup & Health Aggregation (2 hours)

### Step 1: Initialize gateway project structure
**Files to create:**
```
microservices/desktop-integration-service/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app (500-600 lines)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Env loading (pydantic BaseSettings)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── service_discovery.py     # Probe URLs, health checks
│   │   └── models.py                # Pydantic models (ServiceHealth, etc.)
│   └── routes/
│       ├── __init__.py
│       └── health.py                # /health endpoint
├── requirements.txt                 # fastapi, uvicorn, httpx, pydantic, python-dotenv
├── .env.example                     # Service URLs, feature flags
├── .env                             # (local copy, git-ignored)
├── Dockerfile                       # Python 3.11 slim
├── docker-compose.gateway.yml       # Dev compose for testing
└── README.md                        # Quick start guide
```

**Acceptance Criteria:**
- [ ] Project structure matches above
- [ ] `requirements.txt` has all deps (fastapi, uvicorn, httpx, pydantic, python-dotenv, pytest)
- [ ] `.env.example` lists all service URLs with defaults
- [ ] `settings.py` loads and validates env vars
- [ ] Dockerfile builds successfully
- [ ] README has quick start commands

---

### Step 2: Implement `/health` endpoint
**Location:** `app/routes/health.py`

**Returns:**
```json
{
  "status": "online|degraded|offline",
  "timestamp": "2025-12-13T10:30:00Z",
  "gateway": {
    "version": "0.1.0",
    "uptime_seconds": 3600
  },
  "services": [
    {
      "name": "conversation-service",
      "status": "online",
      "latencyMs": 45,
      "lastChecked": "2025-12-13T10:29:55Z"
    },
    {
      "name": "granite-interview-service",
      "status": "offline",
      "error": "Connection refused"
    }
  ]
}
```

**Implementation Details:**
- Probe 7 known service URLs in parallel using `httpx.AsyncClient`
- Timeout: 3 seconds per service
- Retry: 1 attempt only (speed matters)
- Status mapping: `200 OK` → `online`, timeout/error → `offline`
- Measure latency (ms) for each service
- Overall status: `online` if 6+ services healthy, `degraded` if 3-5, `offline` if <3
- Cache results for 5 seconds (avoid hammering during rapid health checks)

**Services to probe:**
1. `CONVERSATION_URL` (8003) → `/health`
2. `VOICE_URL` (8002) → `/health`
3. `AVATAR_URL` (8001) → `/health`
4. `INTERVIEW_URL` (8004) → `/health`
5. `ANALYTICS_URL` (8007) → `/health`
6. `GRANITE_INTERVIEW_URL` (custom) → `/health`
7. `OLLAMA_URL` (11434) → `/api/health` or `/api/tags`

**Acceptance Criteria:**
- [ ] GET `/health` returns 200 in <1 second
- [ ] All 7 services are probed
- [ ] Latency is measured and returned
- [ ] Status bar component in desktop app can parse response
- [ ] Endpoint works even if all services are down (returns `offline`)

---

## Phase 0B: Models Endpoint (1.5 hours)

### Step 3: Implement `/api/v1/models` endpoint
**Location:** `app/routes/models.py`

**Returns:**
```json
{
  "models": [
    {
      "id": "vetta-granite-2b-gguf-v4",
      "name": "Granite 2B (Trained)",
      "paramCount": "2B",
      "ramRequired": "8-12 GB",
      "downloadSize": "1.2 GB",
      "description": "Custom trained on interview dataset",
      "dataset": "vetta-interviews",
      "source": "granite-interview-service"
    },
    {
      "id": "llama3.2:1b",
      "name": "Llama 3.2 (Fallback)",
      "paramCount": "1B",
      "ramRequired": "4-6 GB",
      "downloadSize": "600 MB",
      "description": "Generic fallback model",
      "source": "ollama"
    }
  ]
}
```

**Implementation:**
1. Call `GRANITE_INTERVIEW_URL/api/v1/models` → extract trained models
2. Call `OLLAMA_URL/api/tags` → extract ollama models
3. Merge and normalize schema
4. On error, return static fallback list (hardcoded)
5. Cache for 30 seconds

**Fallback models (hardcoded):**
```python
FALLBACK_MODELS = [
    {
        "id": "granite4:2b",
        "name": "Granite 4 2B (Fallback)",
        "paramCount": "2B",
        "ramRequired": "8-12 GB",
        "downloadSize": "1.2 GB",
        "description": "Fallback model",
        "source": "fallback"
    },
    {
        "id": "llama3.2:1b",
        "name": "Llama 3.2 1B (Fallback)",
        "paramCount": "1B",
        "ramRequired": "4-6 GB",
        "downloadSize": "600 MB",
        "description": "Lightweight fallback",
        "source": "fallback"
    }
]
```

**Acceptance Criteria:**
- [ ] GET `/api/v1/models` returns 200 with normalized schema
- [ ] Works when granite-interview-service is down (returns fallback)
- [ ] Works when ollama is down (returns fallback)
- [ ] Desktop app can render model cards from response
- [ ] Latency <500ms

---

### Step 4: Implement `/api/v1/models/select` endpoint (optional for Phase 0)
**Location:** `app/routes/models.py`

**Request:**
```json
{
  "modelId": "vetta-granite-2b-gguf-v4"
}
```

**Response:**
```json
{
  "selected": "vetta-granite-2b-gguf-v4",
  "timestamp": "2025-12-13T10:30:00Z"
}
```

**Implementation:**
- Store in memory (dict per session) or skip for Phase 0
- Validate modelId exists in available models
- Return confirmation

**Acceptance Criteria:**
- [ ] POST accepts modelId
- [ ] Validates against available models
- [ ] Returns confirmation
- [ ] Can be skipped if desktop app handles selection locally

---

## Phase 0C: Interview Orchestration (3 hours)

### Step 5: Implement `/api/v1/interviews/start` endpoint
**Location:** `app/routes/interviews.py`

**Request:**
```json
{
  "role": "Software Engineer|Product Manager|Data Analyst",
  "model": "vetta-granite-2b-gguf-v4",
  "totalQuestions": 5
}
```

**Response:** `InterviewSession` (must match desktop app type)
```json
{
  "config": {
    "role": "Software Engineer",
    "model": "vetta-granite-2b-gguf-v4",
    "totalQuestions": 5
  },
  "messages": [
    {
      "role": "system",
      "content": "[System prompt for this role]"
    },
    {
      "role": "user",
      "content": "Please start the interview."
    },
    {
      "role": "assistant",
      "content": "Hello, I'm OpenTalent Interviewer. Question 1: [first question]"
    }
  ],
  "currentQuestion": 1,
  "isComplete": false
}
```

**Implementation Strategy:**

**Option A: Route to Granite Interview Service** (preferred)
- Call `GRANITE_INTERVIEW_URL/api/v1/interviews/start` with same payload
- On success: return response as-is
- On error: use fallback template

**Option B: Simple local template** (fallback)
```python
def generate_fallback_question(role: str, question_num: int) -> str:
    prompts = {
        "Software Engineer": [
            "Tell me about a challenging technical problem you solved recently.",
            "How do you approach debugging a complex issue?",
            # ... more questions
        ],
        # ...
    }
    return prompts[role][question_num - 1]
```

**Implementation Details:**
1. Validate role and totalQuestions
2. Try to call granite-interview-service (3s timeout)
3. On success: return response
4. On failure:
   - Use role-based prompt templates
   - Generate minimal InterviewSession with first question
   - Ensure shape matches desktop expectations
5. Log errors but don't expose to client (return valid response anyway)

**Acceptance Criteria:**
- [ ] POST `/api/v1/interviews/start` returns valid `InterviewSession`
- [ ] Works when granite-interview-service is healthy
- [ ] Works when granite-interview-service is down (fallback prompts)
- [ ] All 3 roles (Software Engineer, Product Manager, Data Analyst) supported
- [ ] Response latency <5 seconds
- [ ] Desktop app can parse and display first question

---

### Step 6: Implement `/api/v1/interviews/respond` endpoint
**Location:** `app/routes/interviews.py`

**Request:**
```json
{
  "session": {
    "config": { ... },
    "messages": [ ... ],
    "currentQuestion": 1,
    "isComplete": false
  },
  "message": "Your response text here"
}
```

**Response:** Updated `InterviewSession`

**Implementation:**
1. Validate incoming session shape
2. Append user message to messages array
3. Try to call granite-interview-service (or conversation-service) with full message history
4. On success: add assistant response, detect completion, return updated session
5. On failure: 
   - Return minimal response ("Thank you for your answer. Moving to next question.")
   - Increment currentQuestion
   - Mark isComplete if currentQuestion >= totalQuestions

**Completion Detection:**
- If currentQuestion >= totalQuestions
- If assistant message contains "thank you", "conclude", "end of interview"
- Timeout after 15 questions (safety)

**Acceptance Criteria:**
- [ ] POST `/api/v1/interviews/respond` updates session correctly
- [ ] Works when backend is healthy
- [ ] Works when backend is down (minimal fallback responses)
- [ ] Correctly increments currentQuestion
- [ ] Detects completion after N questions
- [ ] Response latency <5 seconds
- [ ] Desktop app can append new messages and continue flow

---

### Step 7: Implement `/api/v1/interviews/summary` endpoint
**Location:** `app/routes/interviews.py`

**Request:**
```json
{
  "session": { ... }
}
```

**Response:**
```json
{
  "summary": "Interview Complete!\n\nRole: Software Engineer\nQuestions: 5\nResponses: 5\n\nThank you for your participation."
}
```

**Implementation:**
1. Accept session in request body
2. Count responses (user messages excluding system)
3. Try to call granite-interview-service for AI-generated summary
4. On failure: return template summary

**Acceptance Criteria:**
- [ ] POST `/api/v1/interviews/summary` returns summary string
- [ ] Works when backend is healthy
- [ ] Works when backend is down (template summary)
- [ ] Desktop app can display in summary screen

---

## Phase 0D: Integration & Testing (2 hours)

### Step 8: Wire gateway into desktop app
**Location:** `desktop-app/src/renderer/InterviewApp.tsx`

**Changes:**
1. Create/update `integration-service-client.ts`:
   - `fetchHealth()` → GET `/health`
   - `fetchModels()` → GET `/api/v1/models`
   - `startInterview()` → POST `/api/v1/interviews/start`
   - `sendResponse()` → POST `/api/v1/interviews/respond`
   - `getSummary()` → POST `/api/v1/interviews/summary`

2. Update `InterviewApp.tsx`:
   - Replace direct Ollama calls with gateway client
   - Remove hardcoded model list, fetch from `/api/v1/models`
   - Pass full session objects to gateway endpoints

3. Update `.env` for desktop:
   ```
   INTEGRATION_BASE_URL=http://localhost:8009
   ```

**Acceptance Criteria:**
- [ ] Desktop app compiles with no errors
- [ ] Status bar shows gateway health (green/yellow/red dots)
- [ ] Model selection dropdown populated from `/api/v1/models`
- [ ] Setup → Interview → Summary flow works end-to-end
- [ ] Can complete a full interview using gateway

---

### Step 9: Docker Compose & Local Testing
**Location:** `docker-compose.yml` or `docker-compose.test.yml`

**Add gateway service:**
```yaml
services:
  desktop-integration-service:
    build:
      context: ./microservices/desktop-integration-service
    container_name: talent-desktop-gateway
    ports:
      - "8009:8009"
    env_file:
      - ./microservices/desktop-integration-service/.env
    depends_on:
      - ollama
      - granite-interview-service
      - conversation-service
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8009/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped
```

**Test commands:**
```bash
# Start gateway only
docker-compose up desktop-integration-service

# Start gateway + all microservices
docker-compose up

# Test health
curl http://localhost:8009/health

# Test models
curl http://localhost:8009/api/v1/models

# Test interview start
curl -X POST http://localhost:8009/api/v1/interviews/start \
  -H "Content-Type: application/json" \
  -d '{"role":"Software Engineer","model":"vetta-granite-2b-gguf-v4","totalQuestions":5}'
```

**Acceptance Criteria:**
- [ ] Gateway starts successfully on port 8009
- [ ] Gateway is healthy (curl `/health` returns 200)
- [ ] All endpoints return expected schema
- [ ] Works with Docker Compose
- [ ] Desktop app can connect and run interviews

---

### Step 10: Smoke Tests
**Location:** `microservices/desktop-integration-service/tests/test_endpoints.py`

**Test cases:**
```python
def test_health_endpoint():
    """GET /health returns valid structure"""
    
def test_models_endpoint():
    """GET /api/v1/models returns model list"""
    
def test_interview_start():
    """POST /api/v1/interviews/start returns InterviewSession"""
    
def test_interview_start_missing_service():
    """POST /api/v1/interviews/start works when granite-interview is down"""
    
def test_interview_respond():
    """POST /api/v1/interviews/respond updates session"""
    
def test_interview_summary():
    """POST /api/v1/interviews/summary returns string"""
```

**Run:**
```bash
cd microservices/desktop-integration-service
pytest tests/ -v
```

**Acceptance Criteria:**
- [ ] 6+ tests passing
- [ ] Coverage >80% for main endpoints
- [ ] Failures caught before demo

---

## Implementation Checklist

### Phase 0A: Setup (2 hours)
- [ ] Gateway project structure created
- [ ] `settings.py` loads all env vars
- [ ] Dockerfile builds successfully
- [ ] `.env.example` populated

### Phase 0B: Health Aggregation (1.5 hours)
- [ ] `/health` endpoint implemented
- [ ] Probes all 7 services
- [ ] Returns valid schema
- [ ] Caches results for 5 seconds

### Phase 0B: Models (0.5 hours)
- [ ] `/api/v1/models` endpoint implemented
- [ ] Merges granite-interview and ollama models
- [ ] Returns fallback if services down
- [ ] Caches for 30 seconds

### Phase 0C: Interview Orchestration (3 hours)
- [ ] `/api/v1/interviews/start` implemented
- [ ] Routes to granite-interview-service or uses fallback
- [ ] All 3 roles supported
- [ ] `/api/v1/interviews/respond` implemented
- [ ] Updates session correctly
- [ ] Detects completion
- [ ] `/api/v1/interviews/summary` implemented
- [ ] Works with/without backend

### Phase 0D: Integration & Testing (2 hours)
- [ ] Desktop app wired to gateway client
- [ ] Status bar displays health
- [ ] Model selector fetches from `/api/v1/models`
- [ ] Full interview flow works end-to-end
- [ ] Docker Compose updated
- [ ] Smoke tests passing
- [ ] Tested manually with SelectUSA demo scenario

---

## Success Criteria

- ✅ Gateway runs on port 8009
- ✅ Desktop app connects and completes interviews via gateway
- ✅ All endpoints return valid JSON matching desktop app expectations
- ✅ Graceful degradation when services unavailable (fallback prompts)
- ✅ Response latency <5 seconds per request
- ✅ Status bar shows gateway and service health
- ✅ SelectUSA demo scenario: setup → interview → summary works reliably
- ✅ All code documented and tested

---

## Timeline Estimate

| Phase | Task | Est. Time | Cumulative |
|-------|------|-----------|-----------|
| 0A | Project setup, settings, health endpoint | 2 hours | 2h |
| 0B | Models endpoint | 1.5 hours | 3.5h |
| 0C | Interview endpoints (start/respond/summary) | 3 hours | 6.5h |
| 0D | Desktop integration, testing, docker-compose | 2 hours | 8.5h |
| Buffer | Debugging, edge cases | 1.5 hours | 10h |

**Total: ~8-10 hours (fits Days 5-6 timeline)**

---

## Next Steps (After Phase 0)

- Use this lean gateway for SelectUSA demo
- After demo: refactor into full enterprise gateway (Phase 1) with:
  - Circuit breaker pattern
  - Redis caching
  - Correlation IDs
  - Request tracing
  - Admin endpoints
  - Metrics collection
  - Rate limiting
  - JWT authentication

---

**Ready to implement? Start with Step 1 (Project Structure).**
