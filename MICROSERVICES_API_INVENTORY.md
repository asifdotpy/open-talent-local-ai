# Microservices API Inventory
## Complete Service Discovery and Endpoint Documentation

**Date:** December 13, 2025  
**Purpose:** Comprehensive scan of all microservices endpoints for integration service

---

## 📊 Service Overview

| Service | Port | Status | Endpoints Count | Used by Integration Service |
|---------|------|--------|-----------------|----------------------------|
| **Granite Interview Service** | 8005 | ✅ Built | 12 | ⚠️ **Wrong Port** (using 8000) |
| **Conversation Service** | 8003 | ✅ Built | 4 | ✅ Configured |
| **Voice Service** | 8002 | ✅ Built | 15 | ✅ Configured |
| **Avatar Service** | 8001 | ✅ Built | 5 | ✅ Configured |
| **Interview Service** | 8004 | ✅ Built | 20+ | ✅ Configured |
| **Analytics Service** | 8007 | ✅ Built | 8 | ✅ Configured |
| **Scout Service** | 8005 | ✅ Built | ? | ❌ Not configured |
| **Candidate Service** | 8008 | ✅ Built | ? | ❌ Not configured |
| **User Service** | ? | ✅ Built | 3+ | ❌ Not configured |
| **Ollama** | 11434 | ✅ Built | - | ✅ Configured |

---

## 🔴 CRITICAL ISSUES FOUND

### 1. ❌ Granite Interview Service Port Mismatch

**Problem:**
- **Actual Port:** 8005 (from granite-interview-service/app/main.py)
- **Integration Service Config:** 8000 (from desktop-integration-service/app/config/settings.py)

**Impact:** Integration service cannot connect to granite-interview-service

**Fix Required:**
```python
# desktop-integration-service/app/config/settings.py
granite_interview_url: str = "http://localhost:8005"  # Change from 8000 to 8005
```

### 2. ⚠️ Port Conflicts

**Scout Service and Granite Interview Service both use port 8005!**
- Granite Interview Service: Port 8005 (standalone docker-compose.yml)
- Scout Service: Port 8005 (main microservices docker-compose.yml)

**Recommendation:** Change Scout Service to 8010 or use Granite on 8000 when running together

---

## 📋 Detailed Service Endpoints

### 1. Granite Interview Service (Port 8005)

**Base URL:** `http://localhost:8005`

**Core Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/models` - List all available models
- `POST /api/v1/models/load` - Load a specific model
- `DELETE /api/v1/models/{model_name}` - Unload a model
- `GET /api/v1/models/{model_name}/status` - Get model status

**Interview Intelligence:**
- `POST /api/v1/interview/generate-question` - Generate interview question
  - Body: `{model_name, context, candidate_profile, temperature, max_tokens}`
- `POST /api/v1/interview/analyze-response` - Analyze candidate response
  - Body: `{model_name, question, response, context}`

**Training:**
- `POST /api/v1/training/fine-tune` - Fine-tune a model
- `GET /api/v1/training/jobs/{job_id}` - Get training job status
- `DELETE /api/v1/training/jobs/{job_id}` - Cancel training job

**System:**
- `GET /api/v1/system/gpu` - Get GPU information

**What We're Using:**
- ✅ `/api/v1/models` - List models
- ✅ `/api/v1/interview/generate-question` - Generate questions
- ✅ `/api/v1/interview/analyze-response` - Analyze responses

**What We're Missing:**
- ❌ Model loading/unloading
- ❌ Training endpoints
- ❌ GPU info endpoint

---

### 2. Conversation Service (Port 8003)

**Base URL:** `http://localhost:8003`

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /doc` - Documentation redirect
- `GET /api-docs` - API documentation

**Notes:**
- Appears to be a basic service without many exposed endpoints
- May have additional routers not in main.py
- Used as orchestrator for other services

**What We're Using:**
- ✅ `/health` - Health check only

**What We're Missing:**
- Need to scan for additional routers/routes

---

### 3. Voice Service (Port 8002)

**Base URL:** `http://localhost:8002`

**Core Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /info` - Detailed service information
- `GET /voices` - Get available TTS voices

**Voice Processing:**
- `POST /voice/stt` - Speech-to-Text transcription
  - Accepts audio file upload
  - Returns transcription
- `POST /voice/tts` - Text-to-Speech synthesis
  - Body: `{text, voice_id, speed, pitch}`
  - Returns audio file
- `POST /voice/vad` - Voice Activity Detection
  - Analyzes audio for voice activity

**WebRTC (Real-time):**
- `POST /webrtc/start` - Start WebRTC session
- `POST /webrtc/stop` - Stop WebRTC session
- `POST /webrtc/tts` - Send TTS to WebRTC session
- `GET /webrtc/status` - Get WebRTC status

**What We're Using:**
- ✅ `/health` - Health check only

**What We're Missing:**
- ❌ STT (Speech-to-Text) for voice interviews
- ❌ TTS (Text-to-Speech) for avatar voice
- ❌ Voice list for UI selection
- ❌ WebRTC for real-time communication

---

### 4. Avatar Service (Port 8001)

**Base URL:** `http://localhost:8001`

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /doc` - Documentation redirect
- `GET /api-docs` - API documentation
- `POST /render/lipsync` - Render avatar with lip-sync
  - Body: `{audio, animation_data}`
  - Returns rendered video/animation

**What We're Using:**
- ✅ `/health` - Health check only

**What We're Missing:**
- ❌ Lip-sync rendering for avatar interviews
- ❌ Animation endpoints

---

### 5. Interview Service (Port 8004)

**Base URL:** `http://localhost:8004`

**Core Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check

**Room Management:**
- `POST /api/v1/rooms/create` - Create interview room
- `POST /api/v1/rooms/{room_id}/join` - Join interview room
- `DELETE /api/v1/rooms/{room_id}/end` - End interview room
- `GET /api/v1/rooms/{room_id}/status` - Get room status
- `GET /api/v1/rooms` - List all rooms
- `GET /api/v1/rooms/{room_id}/participants` - Get participants

**Interview Management:**
- `POST /api/v1/interviews/start` - Start interview (orchestrator)
  - High-level interview start with room creation

**WebRTC:**
- `POST /api/v1/rooms/{room_id}/webrtc/start` - Start WebRTC
- `POST /api/v1/rooms/{room_id}/webrtc/signal` - WebRTC signaling
- `GET /api/v1/rooms/{room_id}/webrtc/status` - WebRTC status
- `DELETE /api/v1/rooms/{room_id}/webrtc/stop` - Stop WebRTC

**Transcription:**
- `POST /api/v1/rooms/{room_id}/transcription` - Start transcription
- `GET /api/v1/rooms/{room_id}/transcription` - Get transcription
- `DELETE /api/v1/rooms/{room_id}/transcription` - Stop transcription
- `GET /api/v1/transcription/status` - Transcription status

**AI Intelligence:**
- `POST /api/v1/rooms/{room_id}/next-question` - Get next AI question

**What We're Using:**
- ✅ `/health` - Health check only

**What We're Missing:**
- ❌ Room-based interview orchestration
- ❌ WebRTC signaling for real-time interviews
- ❌ Transcription services
- ❌ AI question generation through orchestrator

---

### 6. Analytics Service (Port 8007)

**Base URL:** `http://localhost:8007`

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check

**Analysis Endpoints:**
- `POST /api/v1/analyze/sentiment` - Sentiment analysis
  - Body: `{text, context}`
  - Returns sentiment scores
- `POST /api/v1/analyze/quality` - Response quality analysis
  - Body: `{question, response}`
  - Returns quality metrics
- `POST /api/v1/analyze/bias` - Bias detection
  - Body: `{text, context}`
  - Returns bias indicators
- `POST /api/v1/analyze/expertise` - Expertise assessment
  - Body: `{role, response, skills}`
  - Returns expertise level
- `POST /api/v1/analyze/performance` - Interview performance
  - Body: `{interview_data}`
  - Returns performance scores
- `POST /api/v1/analyze/report` - Generate intelligence report
  - Body: `{interview_id, data}`
  - Returns comprehensive report

**What We're Using:**
- ✅ `/health` - Health check only

**What We're Missing:**
- ❌ Sentiment analysis for responses
- ❌ Quality assessment
- ❌ Bias detection
- ❌ Expertise evaluation
- ❌ Performance metrics
- ❌ Intelligence reports

---

### 7. Scout Service (Port 8005 ⚠️ Conflict)

**Base URL:** `http://localhost:8005` (conflicts with Granite)

**Purpose:** Appears to be a candidate scouting/matching service

**What We're Using:**
- ❌ Not configured in integration service

---

### 8. Candidate Service (Port 8008)

**Base URL:** `http://localhost:8008`

**Purpose:** Candidate profile management

**What We're Using:**
- ❌ Not configured in integration service

---

### 9. User Service (Port TBD)

**Base URL:** Unknown

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /...` - User management endpoints

**What We're Using:**
- ❌ Not configured in integration service

---

### 10. Ollama (Port 11434)

**Base URL:** `http://localhost:11434`

**Endpoints:**
- `GET /api/tags` - List models
- `POST /api/generate` - Generate text
- `POST /api/chat` - Chat completion
- `GET /api/health` - Health check (non-standard, returns 404)

**What We're Using:**
- ✅ `/api/tags` - List models
- ⚠️ `/api/health` - Returns 404 (need to use `/api/tags` for health)

**What We're Missing:**
- ❌ Direct chat/generate endpoints (desktop app uses Ollama directly)

---

## 🔧 Required Fixes for Integration Service

### Priority 1: Critical Fixes

1. **Fix Granite Interview Service Port**
   ```python
   # app/config/settings.py (line 17)
   granite_interview_url: str = "http://localhost:8005"  # Change from 8000
   ```

2. **Fix Ollama Health Check**
   ```python
   # app/core/service_discovery.py
   # Change Ollama health endpoint from /api/health to /api/tags
   if service_name == "ollama":
       health_endpoint = f"{url}/api/tags"
   else:
       health_endpoint = f"{url}/health"
   ```

### Priority 2: Add Missing Services

3. **Add Scout Service** (if needed)
   ```python
   scout_service_url: str = "http://localhost:8010"  # Avoid port conflict
   ```

4. **Add Candidate Service**
   ```python
   candidate_service_url: str = "http://localhost:8008"
   ```

5. **Add User Service**
   ```python
   user_service_url: str = "http://localhost:8011"  # TBD
   ```

### Priority 3: Enhance Integration Service Endpoints

6. **Add Voice Endpoints** (for voice interviews)
   - `/api/v1/voice/synthesize` → Forward to voice-service `/voice/tts`
   - `/api/v1/voice/transcribe` → Forward to voice-service `/voice/stt`

7. **Add Analytics Endpoints** (for interview assessment)
   - `/api/v1/analytics/sentiment` → Forward to analytics-service
   - `/api/v1/analytics/performance` → Forward to analytics-service

8. **Add Room Management** (for multi-user interviews)
   - `/api/v1/rooms/create` → Forward to interview-service
   - `/api/v1/rooms/{id}/join` → Forward to interview-service

---

## 📊 Service Usage Matrix

| Service | Configured | Health Check Working | Endpoints Used | Endpoints Available | Usage % |
|---------|-----------|---------------------|----------------|---------------------|---------|
| Granite Interview | ⚠️ Wrong Port | ❌ No (wrong port) | 0 | 12 | 0% |
| Conversation | ✅ Yes | ⚠️ Unknown | 1 | 4+ | 25% |
| Voice | ✅ Yes | ⚠️ Unknown | 1 | 15 | 7% |
| Avatar | ✅ Yes | ⚠️ Unknown | 1 | 5 | 20% |
| Interview | ✅ Yes | ⚠️ Unknown | 1 | 20+ | 5% |
| Analytics | ✅ Yes | ⚠️ Unknown | 1 | 8 | 13% |
| Ollama | ✅ Yes | ❌ No (wrong endpoint) | 1 | 3 | 33% |
| Scout | ❌ No | - | 0 | ? | 0% |
| Candidate | ❌ No | - | 0 | ? | 0% |
| User | ❌ No | - | 0 | ? | 0% |

**Overall Integration:** ~15% of available endpoints utilized

---

## 🎯 Recommended Architecture Update

### Phase 1: Fix Critical Issues (Now)
- ✅ Fix granite-interview-service port (8000 → 8005)
- ✅ Fix Ollama health check (/api/health → /api/tags)
- ✅ Verify all health checks working

### Phase 2: Enhance Core Features (Days 7-8)
- Add voice synthesis endpoint (TTS)
- Add voice transcription endpoint (STT)
- Add sentiment analysis endpoint
- Add performance analytics endpoint

### Phase 3: Add Advanced Features (Days 9-10)
- Add room-based interview orchestration
- Add WebRTC signaling proxy
- Add transcription services
- Add comprehensive analytics reports

### Phase 4: Add User Management (Post-Demo)
- Add candidate service integration
- Add user service integration
- Add scout service integration

---

## ✅ Action Items

**Immediate (Next 30 minutes):**
1. Update granite_interview_url to port 8005
2. Fix Ollama health check logic
3. Test all health checks
4. Verify granite-interview-service connection works

**Short-term (Next 2 hours):**
5. Add voice TTS endpoint
6. Add analytics sentiment endpoint
7. Test full interview flow with voice
8. Document new endpoints

**Medium-term (Days 7-8):**
9. Add room management endpoints
10. Add WebRTC proxy
11. Add transcription services
12. Add comprehensive analytics

---

**Generated:** December 13, 2025  
**Next Update:** After fixing critical issues and testing
