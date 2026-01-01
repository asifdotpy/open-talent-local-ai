# OpenTalent: Verified API Functionality Catalog

This catalog provides a comprehensive overview of the OpenTalent platform's capabilities, grouped by product module. All endpoints listed have been verified against the stabilized production-ready microservices.

## 🚀 1. Talent Sourcing & Discovery
*Empowering recruiters to find the best talent across global platforms.*

| Service | Capability | Key Endpoints |
| :--- | :--- | :--- |
| **Scout Service** | AI-Powered GitHub Search | `POST /api/v1/search`, `GET /api/v1/agents` |
| **Candidate Service** | Vectorized Profiles & LanceDB | `GET /api/v1/candidates/{id}`, `POST /api/v1/enrich` |
| **Project Service** | Real-time Job Management | `GET /jobs`, `POST /jobs`, `GET /jobs/{id}` |

## 🎙️ 2. Conversational AI & Interview Intelligence
*Autonomous interviewing with multi-modal feedback.*

| Service | Capability | Key Endpoints |
| :--- | :--- | :--- |
| **Conversation Service** | Multi-Agent Orchestration | `POST /chat`, `GET /history` |
| **Voice Service** | Low-latency TTS & STT | `POST /synthesize`, `POST /transcribe` |
| **Avatar Service** | AI Humanoid Rendering | `POST /render`, `GET /assets` |
| **Granite Interview** | Fine-tuned Technical Auditing | `POST /audit/code`, `POST /evaluate/soft-skills` |
| **Interview Service** | Session & Feedback Lifecycle | `POST /sessions`, `GET /reports/{id}` |

## 🧠 3. AI Insights & Explainability
*Transparent, data-backed decision making.*

| Service | Capability | Key Endpoints |
| :--- | :--- | :--- |
| **Analytics Service** | Recruiter ROI & Funnel Data | `GET /kpi/summary`, `GET /funnel/{service}` |
| **AI Auditing** | Bias & Fairness Verification | `POST /audit/fairness`, `GET /compliance/log` |
| **Explainability** | Logic Traceability | `GET /explain/{decision_id}`, `GET /trace` |

## 🛡️ 4. Platform Infrastructure
*Secure, scalable, and integrated foundations.*

| Service | Capability | Key Endpoints |
| :--- | :--- | :--- |
| **User Service** | RBAC & Profile Management | `GET /me`, `PUT /settings` |
| **Security Service** | JWT & Endpoint Protection | `POST /login`, `GET /verify-token` |
| **Notification** | Multi-channel Alerts | `POST /notify`, `GET /preferences` |
| **Desktop Integration** | Service Mesh Gateway | `GET /health/summary`, `POST /proxy/{service}` |

---
> [!NOTE]
> All endpoints are discoverable via the unified [Swagger UI](http://localhost:8009/docs) hosted on the Desktop Integration Service.
