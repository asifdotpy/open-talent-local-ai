# Integration Service Architecture
## Middleware Layer Between Desktop App and Microservices

**Date:** December 13, 2025  
**Status:** ✅ Implemented & Tested (Phase 0A Complete)

---

## 🎯 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     DESKTOP APPLICATION                          │
│  (Electron + React + TypeScript)                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ UI Components:                                             │  │
│  │ - Setup Wizard (role selection, model picker)             │  │
│  │ - Interview Screen (questions, responses)                 │  │
│  │ - StatusBar (shows service health)                        │  │
│  │ - Summary Screen                                          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Integration Service Client (TypeScript)                   │  │
│  │ - fetchIntegrationHealth()                                │  │
│  │ - listModels()                                            │  │
│  │ - startInterview()                                        │  │
│  │ - respondToInterview()                                    │  │
│  │ - getInterviewSummary()                                   │  │
│  │ - getDashboard()                                          │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │ http://localhost:8009
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│           🔥 DESKTOP INTEGRATION SERVICE (MIDDLEWARE)            │
│  Location: microservices/desktop-integration-service/           │
│  Port: 8009                                                      │
│  Technology: FastAPI + Python 3.11+ + httpx                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ API Endpoints:                                             │ │
│  │ GET  /health                - Aggregate health status      │ │
│  │ GET  /api/v1/system/status  - Detailed system info        │ │
│  │ GET  /api/v1/models         - List all models             │ │
│  │ POST /api/v1/models/select  - Select model                │ │
│  │ POST /api/v1/interviews/start    - Start interview        │ │
│  │ POST /api/v1/interviews/respond  - Submit response        │ │
│  │ POST /api/v1/interviews/summary  - Get summary            │ │
│  │ GET  /api/v1/dashboard      - Complete dashboard data     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Core Components:                                           │ │
│  │ - Service Discovery: Probes 7 services concurrently       │ │
│  │ - Health Caching: 5-second TTL to prevent hammering       │ │
│  │ - Graceful Fallback: Templates when services unavailable  │ │
│  │ - Error Handling: Proper HTTP codes + JSON responses      │ │
│  │ - CORS Support: Configured for Electron app               │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            │   Fan-out to Microservices      │
            │                │                │
┌───────────▼────┐  ┌────────▼─────┐  ┌──────▼───────┐
│ Granite         │  │ Conversation │  │ Voice        │
│ Interview       │  │ Service      │  │ Service      │
│ Service         │  │              │  │              │
│ localhost:8000  │  │ :8003        │  │ :8002        │
│                 │  │              │  │              │
│ Trained AI for  │  │ Orchestrates │  │ STT/TTS      │
│ job interviews  │  │ conversation │  │ processing   │
└─────────────────┘  └──────────────┘  └──────────────┘

┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Avatar          │  │ Interview    │  │ Analytics    │
│ Service         │  │ Service      │  │ Service      │
│                 │  │              │  │              │
│ localhost:8001  │  │ :8004        │  │ :8007        │
│                 │  │              │  │              │
│ 3D rendering &  │  │ Interview    │  │ Metrics &    │
│ lip-sync        │  │ orchestrator │  │ reporting    │
└─────────────────┘  └──────────────┘  └──────────────┘

                     ┌──────────────┐
                     │ Ollama       │
                     │ Service      │
                     │              │
                     │ :11434       │
                     │              │
                     │ Local AI     │
                     │ inference    │
                     └──────────────┘
```

---

## 🔑 Key Design Principles

### 1. **Single Entry Point for Desktop App**
- Desktop app **ONLY** talks to `localhost:8009`
- Never directly connects to individual microservices
- Simplifies desktop app code (one HTTP client)
- Easy to mock/test during development

### 2. **Microservices-First Architecture**
- Integration service is a microservice itself
- Lives in `/microservices/` directory alongside others
- Can be deployed independently
- Can be scaled horizontally if needed

### 3. **Graceful Degradation**
- Returns fallback responses when services unavailable
- Hardcoded model list (granite-2b, llama-1b)
- Template-based interview prompts (3 roles)
- Health status shows which services are down

### 4. **Health Monitoring with Caching**
- Probes 7 services every 5 seconds
- Caches results to prevent probe storms
- Aggregates status: online (6+), degraded (3-5), offline (<3)
- Desktop StatusBar displays real-time service status

### 5. **Contract Matching**
- Pydantic models exactly match TypeScript interfaces
- `InterviewSession` structure identical on both sides
- JSON responses match desktop app expectations
- Type safety on both ends

---

## 📦 What We Built (Phase 0A)

### Files Created: 12 files, ~939 lines of code

**Core Application:**
1. `app/config/settings.py` (60 lines) - Environment configuration
2. `app/core/service_discovery.py` (160 lines) - Health monitoring
3. `app/models/schemas.py` (120 lines) - Pydantic models
4. `app/main.py` (599 lines) - FastAPI application
5. `app/__init__.py`, `app/config/__init__.py`, `app/core/__init__.py`, `app/models/__init__.py`

**Developer Tools:**
6. `start.sh` - Quick start script
7. `test_endpoints.py` - Automated endpoint tests
8. `QUICK_START.md` - Developer guide
9. `PHASE_0A_COMPLETE.md` - Completion report
10. `requirements.txt` - Updated with pydantic-settings

**Desktop Integration:**
11. `desktop-app/src/services/integration-service-client.ts` - **Expanded with all gateway endpoints**

---

## ✅ Test Results (All Passed)

```
🧪 Testing Desktop Integration Service Endpoints
============================================================
✅ Root                    - GET  /
✅ Health Check            - GET  /health
✅ System Status           - GET  /api/v1/system/status
✅ List Models             - GET  /api/v1/models
✅ Dashboard               - GET  /api/v1/dashboard
✅ Start Interview         - POST /api/v1/interviews/start

✨ Passed: 6/6 tests
🎉 All tests passed! Gateway is ready.
```

---

## 🔄 Data Flow Example: Starting an Interview

```
1. User clicks "Start Interview" in Desktop UI
   └─> Desktop App (React Component)

2. Call integration service client
   └─> startInterview({ role: "Software Engineer", model: "granite-2b", totalQuestions: 5 })
       └─> POST http://localhost:8009/api/v1/interviews/start

3. Integration Service receives request
   ├─> Validates request (Pydantic)
   ├─> Tries to call granite-interview-service (localhost:8000)
   │   ├─> If available: Use real AI model
   │   └─> If unavailable: Use fallback template
   │
   └─> Returns InterviewSession:
       {
         "config": { "role": "Software Engineer", "model": "granite-2b", "totalQuestions": 5 },
         "messages": [
           { "role": "system", "content": "You are an interviewer..." },
           { "role": "user", "content": "Please start the interview." },
           { "role": "assistant", "content": "Question 1: Tell me about..." }
         ],
         "currentQuestion": 1,
         "isComplete": false
       }

4. Desktop App receives InterviewSession
   └─> Updates UI with first question
   └─> StatusBar shows service health
```

---

## 🚀 Next Steps (Phase 0B)

### Phase 0B: Desktop App Full Integration (2-3 hours)

**Goal:** Wire desktop app to use integration service for **all** operations

#### Task 1: Update InterviewApp.tsx
Replace direct Ollama calls with integration service:
```typescript
// OLD: Direct Ollama provider
const models = await service.listModels();  // Talks to localhost:11434

// NEW: Via integration service
import * as IntegrationService from '../services/integration-service-client';
const models = await IntegrationService.listModels();  // Talks to localhost:8009
```

#### Task 2: Update InterviewService
Add integration service mode:
```typescript
export class InterviewService {
  private mode: 'ollama' | 'integration' = 'integration';  // Default to integration
  
  async startInterview(...) {
    if (this.mode === 'integration') {
      return IntegrationService.startInterview(...);  // Use gateway
    } else {
      // Fallback to direct Ollama (for local dev)
    }
  }
}
```

#### Task 3: Update StatusBar Component
Parse integration health response:
```typescript
const health = await IntegrationService.fetchIntegrationHealth();
// Show: "Services Online: 5/7" or "Status: Degraded (2/7 services down)"
```

#### Task 4: End-to-End Test
1. Start integration service: `./start.sh`
2. Start desktop app: `npm run dev`
3. Complete flow:
   - ✅ Setup screen shows models from gateway
   - ✅ Select model and role
   - ✅ Start interview
   - ✅ Answer questions
   - ✅ See summary
   - ✅ StatusBar shows service health

---

## 📊 Benefits of This Architecture

| Benefit | Description |
|---------|-------------|
| **Separation of Concerns** | Desktop app doesn't know about individual microservices |
| **Easy Testing** | Mock integration service for desktop app tests |
| **Scalability** | Add new microservices without changing desktop app |
| **Monitoring** | Single place to monitor all service health |
| **Graceful Degradation** | App works even when some services down |
| **Future-Proof** | Can add auth, rate limiting, caching at gateway |

---

## 🔧 Running the Stack

### Terminal 1: Start Integration Service
```bash
cd /home/asif1/open-talent/microservices/desktop-integration-service
./start.sh
# Server runs on http://localhost:8009
# API docs: http://localhost:8009/docs
```

### Terminal 2: Start Desktop App
```bash
cd /home/asif1/open-talent/desktop-app
npm run dev
# App connects to http://localhost:8009
```

### Terminal 3: (Optional) Start Microservices
```bash
# Start granite-interview-service, ollama, etc.
# Integration service will detect them and route requests
```

---

## ✅ Architecture Alignment Confirmed

**Your Understanding:** ✅ **100% Correct**

> "There will be an integration service in the microservices that also talks to the Agents. This middleware will be helpful for the desktop-app integration."

**What We Built:**
- ✅ Integration service lives in `microservices/` directory
- ✅ Acts as middleware between desktop app and AI agents/services
- ✅ Provides unified API on port 8009
- ✅ Desktop app talks ONLY to integration service
- ✅ Integration service fans out to 7 microservices
- ✅ Handles health monitoring, fallbacks, error handling

**Status:** Phase 0A Complete (Implementation + Testing)  
**Next:** Phase 0B (Wire desktop app to use integration service)  
**Timeline:** On track for SelectUSA demo (Dec 31, 2025)

---

## 🎯 Success Criteria (Phase 0B)

- [ ] Desktop app connects to `localhost:8009` instead of direct Ollama
- [ ] Model listing works through gateway
- [ ] Interview flow works end-to-end
- [ ] StatusBar displays service health from gateway
- [ ] Graceful fallback when services unavailable
- [ ] Complete demo flow: Setup → Interview → Summary

**Expected Completion:** December 13-14, 2025 (Days 5-6)
