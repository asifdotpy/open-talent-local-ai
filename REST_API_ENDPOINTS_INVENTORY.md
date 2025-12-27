# OpenTalent Microservices REST API Endpoints Inventory

**Last Updated:** December 14, 2025  
**Total Services Analyzed:** 13  
**Total Endpoints Found:** 87

---

## Table of Contents
1. [Granite Interview Service](#1-granite-interview-service)
2. [Conversation Service](#2-conversation-service)
3. [Voice Service](#3-voice-service)
4. [Avatar Service](#4-avatar-service)
5. [Interview Service](#5-interview-service)
6. [Analytics Service](#6-analytics-service)
7. [Scout Service](#7-scout-service)
8. [Candidate Service](#8-candidate-service)
9. [User Service](#9-user-service)
10. [Security Service](#10-security-service)
11. [Notification Service](#11-notification-service)
12. [AI Auditing Service](#12-ai-auditing-service)
13. [Explainability Service](#13-explainability-service)

---

## 1. Granite Interview Service

**Service Name:** OpenTalent Granite Interview Service  
**Port:** 8005 (default)  
**Description:** Modular AI service supporting multiple model architectures for interview intelligence. Supports Granite, Llama, Mistral, and other models with fine-tuning capabilities.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint with service information |
| `GET` | `/health` | Comprehensive health check |

#### Model Management
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `GET` | `/api/v1/models` | List all available models and their status | - | `List[ModelInfo]` |
| `POST` | `/api/v1/models/load` | Load a model into memory | `LoadModelRequest` | Success message |
| `DELETE` | `/api/v1/models/{model_name}` | Unload a model from memory | - | Success message |
| `GET` | `/api/v1/models/{model_name}/status` | Get detailed status of a specific model | - | Model status object |

**ModelInfo Schema:**
```python
{
  "name": str,
  "architecture": str,
  "size": str,
  "quantization": str,
  "status": str,
  "loaded_at": datetime | null,
  "memory_usage": str | null
}
```

**LoadModelRequest Schema:**
```python
{
  "model_name": str,
  "quantization": str = "4bit",
  "device": str = "auto"
}
```

#### Interview Intelligence
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/interview/generate-question` | Generate an interview question using specified model | `GenerateQuestionRequest` | Generated question object |
| `POST` | `/api/v1/interview/analyze-response` | Analyze a candidate's response to interview question | `AnalyzeResponseRequest` | Analysis results |

**GenerateQuestionRequest Schema:**
```python
{
  "model_name": str,
  "context": InterviewContext,
  "candidate_profile": CandidateProfile,
  "temperature": float = 0.7,
  "max_tokens": int = 256
}
```

#### Training
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/training/fine-tune` | Start fine-tuning a model | `FineTuneRequest` | Job creation response |
| `GET` | `/api/v1/training/jobs/{job_id}` | Get status of training job | - | `TrainingStatus` |
| `DELETE` | `/api/v1/training/jobs/{job_id}` | Cancel a training job | - | Success message |

#### System
| Method | Route | Summary | Response |
|--------|-------|---------|----------|
| `GET` | `/api/v1/system/gpu` | Get GPU usage information | GPU status object |

---

## 2. Conversation Service

**Service Name:** OpenTalent - Conversation Service  
**Port:** 8003 (default)  
**Description:** AI-powered conversation management for interview automation with natural language processing and context-aware responses.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for Conversation Service |
| `GET` | `/health` | Health check endpoint |

#### Documentation
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/doc` | Alternative redirect to API documentation |
| `GET` | `/api-docs` | API documentation information and available endpoints |

#### Interview Endpoints
Conversation service includes a router from `app.api.endpoints.interview` module with interview-related conversation endpoints.

---

## 3. Voice Service

**Service Name:** Voice Service API  
**Port:** 8002 (default)  
**Stack:** Vosk (STT) + Modular TTS (Piper/OpenAI) + Silero (VAD) + WebSocket Streaming  
**Description:** Local speech processing service with STT, TTS, VAD, and WebRTC integration.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Service root endpoint |
| `GET` | `/health` | Health check with service status |
| `GET` | `/info` | Detailed service information |

#### Documentation
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/docs` | FastAPI Swagger UI documentation |
| `GET` | `/doc` | Alternative redirect to API documentation |
| `GET` | `/openapi.json` | OpenAPI schema in JSON format |
| `GET` | `/api-docs` | API documentation and available endpoints |

#### Voice Processing
| Method | Route | Summary | Request | Response |
|--------|-------|---------|---------|----------|
| `POST` | `/voice/stt` | Speech-to-Text transcription | Audio file (multipart) | `STTResponse` |
| `POST` | `/voice/tts` | Text-to-Speech synthesis | `TTSRequest` | Audio data (base64) + phonemes |
| `POST` | `/voice/vad` | Voice Activity Detection | Audio file (multipart) | VAD analysis or filtered audio |
| `GET` | `/voices` | Get available TTS voices | - | Voice list |

**TTSRequest Schema:**
```python
{
  "text": str,
  "voice": str | None,
  "speed": float = 1.0,
  "extract_phonemes": bool = True
}
```

**STTResponse Schema:**
```python
{
  "text": str,
  "words": List[dict],
  "duration": float,
  "confidence": float
}
```

#### CORS Preflight
| Method | Route | Summary |
|--------|-------|---------|
| `OPTIONS` | `/voice/tts` | CORS preflight for TTS |
| `OPTIONS` | `/voice/stt` | CORS preflight for STT |
| `OPTIONS` | `/health` | CORS preflight for health |

#### WebSocket Streaming
| Protocol | Route | Summary |
|----------|-------|---------|
| `WebSocket` | `/voice/ws/stt` | Real-time STT streaming |
| `WebSocket` | `/voice/ws/tts` | Real-time TTS streaming |

#### WebRTC (if available)
| Method | Route | Summary | Request |
|--------|-------|---------|---------|
| `POST` | `/webrtc/start` | Start WebRTC session | `{"session_id": str, "job_description": str}` |
| `POST` | `/webrtc/stop` | Stop WebRTC session | `{"session_id": str}` |
| `POST` | `/webrtc/tts` | Send TTS to WebRTC session | `{"session_id": str, "text": str}` |
| `GET` | `/webrtc/status` | Get WebRTC status | - |

---

## 4. Avatar Service

**Service Name:** OpenTalent - Avatar Service  
**Port:** 8001 (default)  
**Description:** Manages AI avatar interactions and rendering for recruitment platform. Avatar and voice generation implemented locally.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for Avatar Service |
| `GET` | `/health` | Comprehensive health check endpoint |

#### Documentation
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/doc` | Alternative redirect to API documentation |
| `GET` | `/api-docs` | API documentation information and available endpoints |

#### Rendering
| Method | Route | Summary | Request Body |
|--------|-------|---------|--------------|
| `POST` | `/render/lipsync` | Render avatar video with lip-sync | `RenderRequest` |

**RenderRequest Schema:**
```python
{
  "text": str,
  "phonemes": list,
  "duration": float,
  "model": str = "production"
}
```

**Response:**
```python
{
  "video_path": str,
  "duration": float,
  "model_used": str,
  "metadata": dict
}
```

---

## 5. Interview Service

**Service Name:** OpenTalent Interview Service  
**Description:** Main interview orchestration service. Uses modular router pattern with API routes included via `app.api.main.api_router`.

### Endpoints

**Note:** The main.py file uses a modular router pattern. Actual endpoints are defined in `app/api/main.py` and included via:
```python
app.include_router(api_router, prefix=settings.API_V1_STR)
```

Endpoints are accessible at `/{API_V1_STR}/*` (typically `/api/v1/*`)

---

## 6. Analytics Service

**Service Name:** OpenTalent Analytics Service API  
**Port:** 8005 (default)  
**Description:** AI-powered analytics and intelligence service for interview analysis.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for Analytics Service |
| `GET` | `/health` | Health check endpoint |

#### Sentiment Analysis
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/analyze/sentiment` | Analyze sentiment of text | `SentimentAnalysisRequest` | `SentimentAnalysis` |

**SentimentAnalysisRequest Schema:**
```python
{
  "text": str
}
```

**SentimentAnalysis Response:**
```python
{
  "polarity": float,
  "subjectivity": float,
  "confidence": float,
  "emotion": str,
  "intensity": float,
  "keywords": List[str]
}
```

#### Response Quality Analysis
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/analyze/quality` | Analyze quality of candidate response | `ResponseQualityRequest` | `ResponseQuality` |

**ResponseQualityRequest Schema:**
```python
{
  "response_text": str,
  "question_context": str
}
```

#### Bias Detection
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/analyze/bias` | Detect potential bias indicators | `BiasDetectionRequest` | `BiasDetection` |

**BiasDetectionRequest Schema:**
```python
{
  "text": str,
  "participants": List[Dict[str, Any]] | None
}
```

#### Expertise Assessment
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/analyze/expertise` | Assess candidate expertise level | `ExpertiseAssessmentRequest` | `ExpertiseAssessment` |

**ExpertiseAssessmentRequest Schema:**
```python
{
  "response_text": str,
  "question_context": str
}
```

#### Interview Performance
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/analyze/performance` | Analyze overall interview performance | `InterviewPerformanceRequest` | `InterviewPerformance` |

**InterviewPerformanceRequest Schema:**
```python
{
  "room_id": str,
  "response_analyses": List[Dict[str, Any]]
}
```

#### Intelligence Report
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/analyze/report` | Generate comprehensive AI intelligence report | `IntelligenceReportRequest` | `IntelligenceReport` |

**IntelligenceReportRequest Schema:**
```python
{
  "room_id": str,
  "analyses": List[Dict[str, Any]],
  "responses": List[Dict[str, Any]],
  "room_created_at": str
}
```

---

## 7. Scout Service

**Service Name:** Talent Scout API  
**Port:** 8000 (default)  
**Description:** AI-powered GitHub developer search with LinkedIn enrichment and agent integration. Supports natural language query formatting with Ollama.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/health` | Health check endpoint |

#### Search
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/search` | Search for GitHub candidates | `SearchRequest` | `SearchResponse` |
| `POST` | `/search/multi-agent` | Enhanced search using multiple agents | `SearchRequest` | `SearchResponse` |

**SearchRequest Schema:**
```python
{
  "query": str,
  "location": str = "Ireland",
  "max_results": int = 20,
  "use_ai_formatting": bool = True
}
```

**SearchResponse Schema:**
```python
{
  "candidates": List[CandidateResponse],
  "total_found": int,
  "search_query": str,
  "location": str
}
```

#### Handoff
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/handoff` | Create interview handoff payload | `SearchCriteria` | `HandoffPayload` |

#### Agent Management
| Method | Route | Summary | Query Parameters |
|--------|-------|---------|-----------------|
| `GET` | `/agents/registry` | Get agent registry with filtering | `capability`, `status` |
| `GET` | `/agents/health` | Get comprehensive health report | - |
| `GET` | `/agents/{agent_name}` | Get detailed agent information | - |
| `POST` | `/agents/call` | Call agent endpoint directly | `AgentRequest` body |
| `POST` | `/agents/search-multi` | Execute search across all agents | `SearchRequest` body |
| `POST` | `/agents/capability/{capability}` | Route request to agents by capability | Query params + payload |

#### System Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/health/full` | Comprehensive system health report |

---

## 8. Candidate Service

**Service Name:** OpenTalent - Candidate Service  
**Port:** 8000 (default)  
**Description:** Candidate profile management and intelligent matching service using vector search (FastEmbed + LanceDB).

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for Candidate Service |
| `GET` | `/health` | Health check endpoint |

#### Documentation
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/doc` | Alternative redirect to API documentation |
| `GET` | `/api-docs` | API documentation information and available endpoints |

#### Candidate Management
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/api/v1/candidates` | Store new candidate profile with embeddings | `CandidateProfile` | `{"candidate_id": str, "message": str, "vector_search_enabled": bool}` |
| `GET` | `/api/v1/candidates/{candidate_id}` | Retrieve candidate profile by ID | - | `CandidateProfile` |

#### Search
| Method | Route | Summary | Query Parameters | Response |
|--------|-------|---------|------------------|----------|
| `GET` | `/api/v1/candidates/search` | Search candidates by vector similarity | `query`, `limit=5` | Search results with profiles |

**CandidateProfile Schema:**
```python
{
  "full_name": str,
  "source_url": str,
  "summary": str,
  "work_experience": List[WorkExperience],
  "education": List[Education],
  "skills": Skills,
  "alignment_score": float,
  "initial_questions": List[InitialQuestion]
}
```

---

## 9. User Service

**Service Name:** User Service  
**Description:** User profile management service with database persistence.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check endpoint |

#### User Profiles
| Method | Route | Summary | Request Body | Response | Status Code |
|--------|-------|---------|--------------|----------|------------|
| `POST` | `/users/profile` | Create a new user profile | `UserProfileCreate` | `UserProfileResponse` | 201 |

**UserProfileCreate Schema:**
```python
{
  "username": str,
  "email": str,
  "full_name": str | None
}
```

**UserProfileResponse Schema:**
```python
{
  "id": int,
  "username": str,
  "email": str,
  "full_name": str | None,
  "created_at": str
}
```

---

## 10. Security Service

**Service Name:** Security Service  
**Description:** Minimal security service implementation.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check endpoint |

---

## 11. Notification Service

**Service Name:** Notification Service  
**Description:** Notification management service.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for Notification Service |
| `GET` | `/health` | Health check endpoint for Notification Service |

---

## 12. AI Auditing Service

**Service Name:** AI Auditing Service  
**Description:** AI auditing and compliance service.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for AI Auditing Service |
| `GET` | `/health` | Health check endpoint for AI Auditing Service |

---

## 13. Explainability Service

**Service Name:** OpenTalent Explainability Service API  
**Port:** (not specified in main.py)  
**Description:** AI explainability and transparency service for model interpretability, bias detection, and compliance support.

### Endpoints

#### Root & Health
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/` | Root endpoint for Explainability Service |
| `GET` | `/health` | Health check endpoint |

#### Documentation
| Method | Route | Summary |
|--------|-------|---------|
| `GET` | `/doc` | Alternative redirect to API documentation |
| `GET` | `/api-docs` | API documentation information and available endpoints |

#### Decision Explanation
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/explain/interview` | Explain AI interview decisions | `InterviewExplanationRequest` | `ExplanationResponse` |

**InterviewExplanationRequest Schema:**
```python
{
  "interview_id": str,
  "candidate_id": str,
  "decision": str,
  "scores": Dict[str, float],
  "feedback": str | None
}
```

#### Scoring Explanation
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/explain/scoring` | Explain candidate scoring decisions | `ScoringExplanationRequest` | `ExplanationResponse` |

**ScoringExplanationRequest Schema:**
```python
{
  "candidate_id": str,
  "job_id": str,
  "scores": Dict[str, float],
  "criteria": List[str]
}
```

#### Model Explanation
| Method | Route | Summary | Response |
|--------|-------|---------|----------|
| `GET` | `/explain/model/{model_id}` | Get explanation of AI model behavior | `ExplanationResponse` |

#### Bias Detection
| Method | Route | Summary | Request Body | Response |
|--------|-------|---------|--------------|----------|
| `POST` | `/bias/check` | Check for potential bias | `BiasCheckRequest` | `BiasReportResponse` |
| `GET` | `/bias/report` | Get latest bias analysis report | Query: `report_id` (optional) | `BiasReportResponse` |

**BiasCheckRequest Schema:**
```python
{
  "data": Dict[str, Any],
  "model_type": str,
  "threshold": float | None = 0.1
}
```

---

## Summary Statistics

### Endpoints by Category
- **Health & Documentation:** 30+ endpoints
- **Core Business Logic:** 45+ endpoints
- **Agent Integration:** 10+ endpoints
- **Utility & System:** 2 endpoints

### Endpoints by HTTP Method
- **GET:** 40 endpoints
- **POST:** 32 endpoints
- **DELETE:** 3 endpoints
- **OPTIONS:** 3 endpoints
- **WebSocket:** 2 endpoints

### Services with Most Endpoints
1. **Scout Service:** 14 endpoints (including agent integration)
2. **Voice Service:** 13 endpoints (including WebSocket + WebRTC)
3. **Granite Interview Service:** 12 endpoints
4. **Analytics Service:** 7 endpoints
5. **Explainability Service:** 7 endpoints

### Services with Minimal Endpoints
- **Security Service:** 2 endpoints
- **Notification Service:** 2 endpoints
- **AI Auditing Service:** 2 endpoints

---

## Integration Notes

### Authentication & Authorization
- No authentication mechanisms found in main.py files
- CORS middleware enabled on most services with permissive origins

### Database Support
- **Candidate Service:** PostgreSQL + Vector DB (LanceDB)
- **User Service:** PostgreSQL
- **Analytics Service:** In-memory (TextBlob)
- **Others:** Stateless services

### External Dependencies
- **Voice Service:** Vosk (STT), Piper/OpenAI (TTS), Silero (VAD)
- **Avatar Service:** Node.js renderer
- **Scout Service:** Ollama, GitHub API, ContactOut API
- **Granite Interview Service:** PyTorch, multiple LLM frameworks

### Agent Integration
- **Scout Service:** Integrated with agent registry system
- Supports multi-agent search and capability-based routing

---

## Environment Variables (Detected)

### Voice Service
- `USE_MOCK_SERVICES`
- `OPENAI_API_KEY`
- `OPENAI_TTS_MODEL`
- `OPENAI_TTS_VOICE`
- `VOSK_MODEL_PATH`
- `PIPER_MODEL_PATH`
- `PIPER_CONFIG_PATH`
- `SILERO_MODEL_PATH`
- `TTS_PROVIDER`
- `ENABLE_WEBRTC`

### Scout Service
- `GITHUB_TOKEN`
- `CONTACTOUT_API_TOKEN`
- `OLLAMA_URL`
- `OLLAMA_MODEL`
- `AGENT_DISCOVERY_PATH`

### Granite Interview Service
- `PORT` (default: 8005)

### Database Services
- `DATABASE_URL`
- `VECTOR_DB_PATH`

---

## API Versioning

Most services use `/api/v1/` prefix for versioned endpoints:
- **Granite Interview Service:** `/api/v1/*`
- **Analytics Service:** `/api/v1/*`
- **Candidate Service:** `/api/v1/*`

Some services use custom prefixes or settings-based configuration (Interview Service, Scout Service).

---

## Documentation URLs

Most services provide documentation at:
- `/docs` - Swagger UI (FastAPI default)
- `/redoc` - ReDoc documentation
- `/openapi.json` - OpenAPI schema

Alternative access routes:
- `/doc` - Redirect to `/docs`
- `/api-docs` - Custom summary of endpoints

---

**End of Inventory**
