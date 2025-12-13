# TalentAI Integration Gateway Design Plan

> Date: December 13, 2025
> Scope: Desktop → Integration Gateway → Microservices
> Audience: Implementing agent(s) designing the Integration Service and adapting the desktop app

## Executive Summary
OpenTalent has pivoted to a microservices-first architecture with a desktop Electron app. To reduce complexity and improve resilience, we will introduce a unified Integration Service (FastAPI) that the desktop app talks to instead of calling individual services directly. This gateway aggregates health and models, orchestrates interviews, and provides graceful degradation when backends are unavailable.

This plan consolidates repo context and UI expectations into concrete endpoints, contracts, config, and deliverables for rapid implementation.

## Current Context & Key Files
- Desktop UI and flow:
  - Setup, Interview, Summary screens in [desktop-app/src/renderer/InterviewApp.tsx](../../desktop-app/src/renderer/InterviewApp.tsx)
  - Styles in [desktop-app/src/renderer/InterviewApp.css](../../desktop-app/src/renderer/InterviewApp.css)
  - Provider-driven interview logic in [desktop-app/src/services/interview-service.ts](../../desktop-app/src/services/interview-service.ts)
  - Integration client scaffold in [desktop-app/src/services/integration-service-client.ts](../../desktop-app/src/services/integration-service-client.ts)
  - Status bar component in [desktop-app/src/renderer/ui/StatusBar.tsx](../../desktop-app/src/renderer/ui/StatusBar.tsx)

- Integration Service (skeleton present):
  - [microservices/desktop-integration-service/README.md](../../microservices/desktop-integration-service/README.md)
  - [microservices/desktop-integration-service/app/main.py](../../microservices/desktop-integration-service/app/main.py)
  - Dockerfile, requirements, and .env example under the same directory

- Architecture & constraints:
  - Local-only, privacy-first per [AGENTS.md](../../AGENTS.md)
  - Services include conversation, voice, avatar, interview, analytics, granite-interview, ollama
  - Docker compose orchestrates existing services; integration service to be added

## Desktop App Expectations
The desktop app expects the following capabilities:
- Health: Overall and per-service status to render a status bar
- Models: List and selection of models for interviews
- Interview orchestration: Start, respond, summary with `InterviewSession` compatibility
- Consistent error messaging and graceful degradation

### Contracts (align with existing types)
- `Message`: `{ role: 'system' | 'user' | 'assistant', content: string }`
- `InterviewConfig`: `{ role: string, model: string, totalQuestions: number }`
- `InterviewSession`: `{ config: InterviewConfig, messages: Message[], currentQuestion: number, isComplete: boolean }`

## Gateway Endpoints
- `GET /health`
  - Returns: `{ status: 'online'|'degraded'|'offline', services: Array<{ name, status, latencyMs? }> }`
  - Purpose: Drive `StatusBar` component

- `GET /api/v1/models`
  - Returns normalized models: `[{ id, name, paramCount, ramRequired, downloadSize, description, dataset? }]`
  - Sources: granite-interview-service, ollama; fallback to static list

- `POST /api/v1/models/select`
  - Body: `{ modelId: string }`
  - Returns: `{ selected: modelId }`

- `POST /api/v1/interviews/start`
  - Body: `{ role: string, model: string, totalQuestions: number }`
  - Returns: `InterviewSession` with first assistant question

- `POST /api/v1/interviews/respond`
  - Body: `{ sessionId?: string, message: string, session?: InterviewSession }`
  - Returns: updated `InterviewSession`

- `GET /api/v1/interviews/summary`
  - Query: `{ sessionId?: string }` or accept `InterviewSession` in body
  - Returns: summary string compatible with current UI display

- `GET /api/v1/system/status`
  - Returns aggregate metrics, versions, uptime for dashboard expansion

- `GET /api/v1/dashboard`
  - Returns curated, UI-ready status across services for future use

## Design Responsibilities
- Service discovery: Probe known service URLs; maintain registry with periodic health checks
- Health aggregation: Normalize statuses to `online|degraded|offline` with latency
- Model management: Merge model sources; expose unified schema
- Interview orchestration: Route to the healthiest capable backend; attach retries/backoff
- Graceful degradation: Provide minimal viable interview start/respond when backends fail
- Error strategy: Consistent messages for the desktop app; avoid leaking stack traces
- CORS: Allow Electron origins for local development

## Config & Environment
- Required URLs:
  - `GRANITE_INTERVIEW_URL`, `CONVERSATION_URL`, `VOICE_URL`, `AVATAR_URL`, `ANALYTICS_URL`, `OLLAMA_URL`
- Feature flags: `ENABLE_VOICE`, `ENABLE_AVATAR`, `ENABLE_ANALYTICS`
- Optional: `REDIS_URL` (caching), `PROMETHEUS_ENABLE`
- Desktop: `INTEGRATION_BASE_URL` for client; default `http://localhost:8009`

## Graceful Degradation
- Health down → mark `offline`; continue rendering in UI
- Models unavailable → present fallback static list
- Interview start/respond failures → synthesize minimal prompts using onboard templates to keep flow usable
- Maintain `InterviewSession` shape so the UI remains stable

## Testing Plan
- Gateway endpoint smoke tests (`curl`/Postman)
- Failure scenarios: One or more services down; verify fallback behavior
- Desktop integration validation: Swap provider to gateway endpoints, run setup→interview→summary
- Latency sampling on `/health`; verify status transitions

## Implementation Steps & Deliverables
1. Finalize endpoint contracts and error shapes in gateway README
2. Implement health aggregation and discovery with retry/backoff in `app/main.py`
3. Implement models endpoints with merging and fallback
4. Implement interview endpoints; route to granite/conversation; add fallback
5. Add CORS for desktop; expose consistent JSON
6. Update desktop app:
   - Use `/api/v1/models` for model selection in [InterviewApp.tsx](../../desktop-app/src/renderer/InterviewApp.tsx)
   - Replace direct Ollama calls by gateway in [interview-service.ts](../../desktop-app/src/services/interview-service.ts)
7. Add gateway to `docker-compose.yml` with healthcheck
8. Write a short developer guide in the gateway README including try-it commands

## Alignment & Refinements (Provided Spec)
- Port conflicts: Resolve `user-service` sharing `8001` with `avatar-service` by moving `user-service` to `8011`
- Gateway port: Use `8009` (desktop-friendly) or `8000`; ensure consistency across docs and env
- Circuit breaker & rate limiting: Plan hooks for future; start with pragmatic retry/backoff
- Request tracing: Generate correlation IDs at gateway; pass through headers
- Auth: Keep local-only by default; prepare JWT header validation middleware for future multi-user setups

## Open Questions / Help Needed
- Confirm canonical gateway port (`8009` vs `8000`) for consistency
- Decide model routing policy: user-selected vs gateway auto-choice on health/latency
- Confirm minimum viable fallback prompts for roles beyond the three currently supported
- Approve service registry source of truth (env vs yaml) for discovery

## Quick Start (Dev)
- Start gateway:
  1) Configure `.env` under `microservices/desktop-integration-service`
  2) `pip install -r requirements.txt`
  3) `python app/main.py`
- Test:
  - `GET /health`, `GET /api/v1/models`, `POST /api/v1/interviews/start`
- Desktop run:
  - `INTEGRATION_BASE_URL=http://localhost:8009 npm run dev` under `desktop-app`

---
This plan is ready for implementation. It aligns the desktop UI with a robust Integration Service and provides clear endpoints, contracts, and testing guidance for rapid delivery.
