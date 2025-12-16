## Verification Table (Code Scan)

| Service | Endpoints (scan) | Ports |
|---------|-------------------|-------|
| ai-auditing-service | 4 |  |
| analytics-service | 16 |  |
| audio-service | 0 |  |
| avatar-service | 36 | 8001 |
| candidate-service | 76 | 8008 |
| conversation-service | 8 | 8003 |
| desktop-integration-service | 26 |  |
| explainability-service | 18 |  |
| granite-interview-service | 24 |  |
| interview-service | 49 |  |
| notification-service | 14 |  |
| project-service | 6 |  |
| scout-service | 22 | 8000 |
| security-service | 42 |  |
| user-service | 28 | 8001,8007 |
| voice-service | 60 | 8015 |

Notes:
- Decorator-based scan may undercount router-included endpoints (e.g., conversation-service routes included from routers).
- WebSocket endpoints are included only if declared via decorators in scanned files.

# API Endpoints Quick Reference
> Delta Summary (December 15, 2025 - Scanner Uplift)
- Security-Service: 42 endpoints
- User-Service: 28 endpoints
- Voice-Service: 60 endpoints
- Avatar-Service: 36 endpoints
- Candidate-Service: 76 endpoints
- Interview-Service: 49 endpoints
- Desktop-Integration: 26 endpoints
- Analytics-Service: 16 endpoints
- Notification-Service: 14 endpoints
- Scout-Service: 22 endpoints
- Conversation-Service: 8 endpoints
- Granite-Interview: 24 endpoints
- Explainability-Service: 18 endpoints
- Project-Service: 6 endpoints
Counts now reflect router and add_api_route detection.
**Date:** December 15, 2025  
**Format:** Service-by-service endpoint listing  

---

## 📋 Complete API Endpoint Inventory

### 1. AI-AUDITING-SERVICE (4 endpoints)
```
GET      /
GET      /health
```

### 2. ANALYTICS-SERVICE (16 endpoints)
```
GET      /
GET      /health
POST     /api/v1/analyze/sentiment
POST     /api/v1/analyze/quality
POST     /api/v1/analyze/bias
POST     /api/v1/analyze/expertise
POST     /api/v1/analyze/performance
POST     /api/v1/analyze/report
```

### 3. AVATAR-SERVICE (5 endpoints)
```
GET      /
GET      /doc
GET      /api-docs
GET      /health
POST     /render/lipsync
```

### 4. CANDIDATE-SERVICE (76 endpoints)
```
GET      /
GET      /health
GET      /doc
GET      /api-docs
POST     /api/v1/candidates
GET      /api/v1/candidates/search
GET      /api/v1/candidates/{candidate_id}
GET      /api/v1/candidates
GET      /api/v1/candidates/bulk/export
PUT      /api/v1/candidates/{candidate_id}
PATCH    /api/v1/candidates/{candidate_id}/status
DELETE   /api/v1/candidates/{candidate_id}
POST     /api/v1/candidate-profiles
GET      /api/v1/candidate-profiles/{candidate_id}
POST     /api/v1/candidates/bulk
GET      /api/v1/applications
POST     /api/v1/applications
PATCH    /api/v1/applications/{app_id}
POST     /api/v1/candidates/{candidate_id}/assessments
GET      /api/v1/candidates/{candidate_id}/assessments
GET      /api/v1/candidates/{candidate_id}/assessments/{assessment_id}
PUT      /api/v1/candidates/{candidate_id}/assessments/{assessment_id}
DELETE   /api/v1/candidates/{candidate_id}/assessments/{assessment_id}
POST     /api/v1/candidates/{candidate_id}/availability
GET      /api/v1/candidates/{candidate_id}/availability
GET      /api/v1/candidates/{candidate_id}/availability/{availability_id}
PUT      /api/v1/candidates/{candidate_id}/availability/{availability_id}
DELETE   /api/v1/candidates/{candidate_id}/availability/{availability_id}
POST     /api/v1/candidates/{candidate_id}/interviews
GET      /api/v1/candidates/{candidate_id}/interviews
GET      /api/v1/candidates/{candidate_id}/interviews/{interview_id}
PUT      /api/v1/candidates/{candidate_id}/interviews/{interview_id}
DELETE   /api/v1/candidates/{candidate_id}/interviews/{interview_id}
POST     /api/v1/candidates/{candidate_id}/skills
GET      /api/v1/candidates/{candidate_id}/skills
POST     /api/v1/candidates/{candidate_id}/resume
GET      /api/v1/candidates/{candidate_id}/resume
```

### 5. CONVERSATION-SERVICE (8 endpoints)
```
GET      /
GET      /health
GET      /doc
GET      /api-docs
POST     /conversation/generate-questions
POST     /conversation/start
POST     /conversation/message
GET      /conversation/status/{session_id}
POST     /conversation/end/{session_id}
POST     /api/v1/conversation/generate-adaptive-question
POST     /api/v1/conversation/generate-followup
POST     /api/v1/conversation/adapt-interview
POST     /api/v1/persona/switch
GET      /api/v1/persona/current
```

### 6. DESKTOP-INTEGRATION-SERVICE (26 endpoints)
```
GET      /health
GET      /api/v1/system/status
GET      /api/v1/services
GET      /api/v1/models
POST     /api/v1/models/select
POST     /api/v1/voice/synthesize
POST     /api/v1/analytics/sentiment
POST     /api/v1/agents/execute
POST     /api/v1/interviews/start
POST     /api/v1/interviews/respond
POST     /api/v1/interviews/summary
GET      /api/v1/dashboard
GET      /
```

### 7. EXPLAINABILITY-SERVICE (18 endpoints)
```
GET      /
GET      /health
GET      /doc
GET      /api-docs
POST     /explain/interview
POST     /explain/scoring
GET      /explain/model/{model_id}
POST     /bias/check
GET      /bias/report
```

### 8. GRANITE-INTERVIEW-SERVICE (24 endpoints)
```
GET      /
GET      /health
GET      /api/v1/models
POST     /api/v1/models/load
DELETE   /api/v1/models/{model_name}
GET      /api/v1/models/{model_name}/status
POST     /api/v1/interview/generate-question
POST     /api/v1/interview/analyze-response
POST     /api/v1/training/fine-tune
GET      /api/v1/training/jobs/{job_id}
DELETE   /api/v1/training/jobs/{job_id}
GET      /api/v1/system/gpu
```

### 9. INTERVIEW-SERVICE (20+ endpoints)
```
GET      /docs
GET      /doc
GET      /api-docs
GET      /
GET      /health
POST     /api/v1/rooms/create
POST     /api/v1/interviews/start
POST     /api/v1/rooms/{room_id}/join
DELETE   /api/v1/rooms/{room_id}/end
POST     /api/v1/rooms/{room_id}/adapt-interview
POST     /api/v1/rooms/{room_id}/analyze-response
POST     /api/v1/rooms/{room_id}/next-question
POST     /api/v1/rooms/{room_id}/transcription
DELETE   /api/v1/rooms/{room_id}/transcription
GET      /api/v1/rooms
GET      /api/v1/rooms/{room_id}/status
GET      /api/v1/rooms/{room_id}/transcription
GET      /api/v1/rooms/{room_id}/intelligence-report
GET      /api/v1/rooms/{room_id}/participants
GET      /api/v1/transcription/status
POST     /api/v1/rooms/{room_id}/webrtc/start
GET      /api/v1/rooms/{room_id}/webrtc/status
DELETE   /api/v1/rooms/{room_id}/webrtc/stop
POST     /api/v1/rooms/{room_id}/webrtc/signal
WEBSOCKET /ws/transcription/{room_id}
WEBSOCKET /webrtc/signal
GET      /demo-session/{session_id}
POST     /demo-session
POST     /start
GET      /health
GET      /templates
GET      /templates/{template_id}
POST     /templates
POST     /templates/{template_id}/use
POST     /generate
GET      /db-status
GET      /me
GET      /{user_id}
GET      /health
GET      /info
POST     /analyze-sentiment
POST     /assess-candidate
POST     /generate
POST     /generate-outreach
POST     /generate-question
POST     /score-quality
GET      /webrtc/info
```

### 10. NOTIFICATION-SERVICE (14 endpoints)
```
GET      /
GET      /health
GET      /api/v1/provider
POST     /api/v1/notify/email
POST     /api/v1/notify/sms
POST     /api/v1/notify/push
GET      /api/v1/notify/templates
```

### 11. PROJECT-SERVICE (6 endpoints)
```
GET      /
GET      /health
GET      /jobs/{project_id}
```

### 12. SCOUT-SERVICE (22 endpoints)
```
GET      /health
GET      /health/full
POST     /search
POST     /handoff
GET      /agents/registry
GET      /agents/health
GET      /agents/{agent_name}
POST     /agents/call
POST     /agents/search-multi
POST     /agents/capability/{capability}
POST     /search/multi-agent
```

### 13. SECURITY-SERVICE (42 endpoints)
```
GET      /
GET      /health
POST     /api/v1/auth/register
POST     /api/v1/auth/login
POST     /api/v1/auth/logout
POST     /api/v1/auth/verify
POST     /api/v1/auth/refresh
GET      /api/v1/auth/profile
POST     /api/v1/auth/mfa/setup
POST     /api/v1/auth/mfa/verify
DELETE   /api/v1/auth/mfa
GET      /api/v1/auth/permissions
POST     /api/v1/auth/permissions/check
POST     /api/v1/encrypt
POST     /api/v1/decrypt
POST     /api/v1/auth/password/change
POST     /api/v1/auth/password/reset-request
POST     /api/v1/auth/password/reset
GET      /api/v1/roles
POST     /api/v1/roles/assign
DELETE   /api/v1/roles/revoke
```

### 14. SHARED (1 endpoint)
```
POST     /interview/assess
```

### 15. USER-SERVICE (14 endpoints)
```
GET      /api/v1/users/{user_id}/preferences
PUT      /api/v1/users/{user_id}/preferences
GET      /api/v1/users/me/preferences
PUT      /api/v1/users/me/preferences
GET      /api/v1/users/{user_id}/emails
POST     /api/v1/users/{user_id}/emails
DELETE   /api/v1/users/{user_id}/emails/{email}
GET      /api/v1/users/{user_id}/phones
POST     /api/v1/users/{user_id}/phones
DELETE   /api/v1/users/{user_id}/phones/{phone}
GET      /api/v1/users/{user_id}/activity
GET      /api/v1/users/{user_id}/sessions
DELETE   /api/v1/users/{user_id}/sessions/{session_id}
GET      /api/v1/users/{user_id}/statistics
```

### 16. VOICE-SERVICE (60 endpoints)
```
GET      /
GET      /health
GET      /docs
GET      /doc
GET      /openapi.json
GET      /api-docs
GET      /voices
GET      /info
POST     /voice/normalize
POST     /voice/format
POST     /voice/split
POST     /voice/join
POST     /voice/phonemes
POST     /voice/trim
POST     /voice/resample
POST     /voice/metadata
POST     /voice/channels
POST     /voice/latency-test
POST     /voice/batch-tts
POST     /voice/stt
POST     /voice/tts
POST     /voice/vad
POST     /webrtc/start
POST     /webrtc/stop
POST     /webrtc/tts
POST     /webrtc/audio/benchmark
GET      /webrtc/audio/stats
GET      /webrtc/info
GET      /sessions
WEBSOCKET /voice/ws/stt
WEBSOCKET /voice/ws/tts
WEBSOCKET /webrtc/signal
```

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Total Services | 18 |
| Total Endpoints (implemented) | ~120 |
| Coverage (approx) | ~48% |
| Services with Schemas | 14 |
| Services without Schemas | 4 |

---

## 🟢 Services by Status

### ✅ Full Coverage (Excellent)
- analytics-service
- candidate-service
- conversation-service
- interview-service (largest)
- scout-service

### 🟠 Partial Coverage (Good)
- avatar-service
- desktop-integration-service
- explainability-service
- granite-interview-service
- project-service
- user-service
- voice-service

### ⚠️ No Coverage (Missing Schemas)
- ai-auditing-service
- notification-service
- security-service
- shared

---

## 🔴 Critical Services Needing Schemas

1. **security-service** (42 endpoints) - Auth/Auth critical
2. **notification-service** (14 endpoints) - User-facing feature
3. **voice-service** (60 endpoints) - Low schema coverage, new WebSocket

---

**Last Audited:** December 15, 2025
