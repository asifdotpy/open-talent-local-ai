# API Catalog Updates — December 15, 2025

Update Date: December 15, 2025
Scope: Align API Catalog with latest OpenAPI verification and service code under `services/`. Reflects completion of User, Candidate, Voice, and Interview services; adjusts integration/gateway coverage.

---

## Summary

- Complete: Security (18), Notification (6), Candidate (10), User (9), Voice (10–13), Interview (22)
- Near Complete: Conversation (10+), Avatar (13), Analytics (7–8), Explainability (7–9)
- In Progress: Scout (10+, target 25+), AI Auditing (7, target 15+)
- Desktop Integration Gateway: Add/confirm proxies for voice, candidates, users, interviews

---

## Service Endpoint Snapshots (from OpenAPI/code)

- Candidate Service (Port 8008)
  - Core: `/api/v1/candidates` (POST, GET list), `/api/v1/candidates/{id}` (GET, PUT, DELETE)
  - Applications: `/api/v1/applications` (POST, GET), `/api/v1/candidates/{id}/applications` (GET), `/api/v1/applications/{app_id}` (PATCH)
  - Profile: `/api/v1/candidates/{id}/resume` (GET, POST)
  - Skills: `/api/v1/candidates/{id}/skills` (GET, POST)

- User Service (Port 8007)
  - Preferences: `/api/v1/users/{user_id}/preferences` (GET, PUT), `/api/v1/users/me/preferences` (GET, PUT)
  - Contacts: `/api/v1/users/{user_id}/emails` (GET, POST, DELETE by email), `/api/v1/users/{user_id}/phones` (GET, POST, DELETE by phone)
  - Activity/Sessions: `/api/v1/users/{user_id}/activity` (GET), `/api/v1/users/{user_id}/sessions` (GET), `/api/v1/users/{user_id}/sessions/{session_id}` (DELETE)
  - Stats: `/api/v1/users/{user_id}/statistics` (GET)

- Voice Service (Port 8003)
  - Info: `GET /`, `GET /health`, `GET /info`, `GET /voices`
  - Core: `POST /voice/stt`, `POST /voice/tts`

- Interview Service (Port 8005)
  - Health/DB: `GET /health`, `GET /db-status`
  - Orchestration: `POST /start`, room management endpoints (create/join/end/status/list/participants)

- Security Service (Port 8010)
  - Auth: register/login/logout/verify/refresh/profile/password (change/reset)
  - MFA: setup/verify/disable; Permissions: list/check; Crypto: encrypt/decrypt; Roles: list/assign/revoke

- Notification Service (Port 8011)
  - Provider info, notify email/SMS/push, templates (Novu → Apprise fallback)

---

## Integration Gateway — Required/Confirmed Proxies

- Voice:
  - `POST /api/v1/voice/synthesize` → voice-service `/voice/tts`
  - `POST /api/v1/voice/transcribe` → voice-service `/voice/stt`

- Candidates:
  - `GET/POST /api/v1/candidates`
  - `GET/PUT/DELETE /api/v1/candidates/{id}`
  - `GET /api/v1/candidates/{id}/applications`
  - `POST /api/v1/applications`, `GET /api/v1/applications`, `PATCH /api/v1/applications/{app_id}`
  - `GET/POST /api/v1/candidates/{id}/resume`
  - `GET/POST /api/v1/candidates/{id}/skills`

- Users:
  - `GET/PUT /api/v1/users/me/preferences`
  - `GET/PUT /api/v1/users/{id}/preferences`
  - `GET/POST/DELETE /api/v1/users/{id}/emails`
  - `GET/POST/DELETE /api/v1/users/{id}/phones`
  - `GET /api/v1/users/{id}/activity`
  - `GET /api/v1/users/{id}/sessions`, `DELETE /api/v1/users/{id}/sessions/{session_id}`
  - `GET /api/v1/users/{id}/statistics`

- Interviews:
  - `POST /api/v1/interviews/start` → interview-service `/start`
  - Room routes proxied to interview-service as applicable

---

## Catalog Totals (Updated)

- Implemented Endpoints: ~143+
- Target: ~250+
- Remaining: ~107

---

## Next Actions

- Expand AI Auditing (bias/fairness/compliance/reporting) and Scout (platform search, results ops)
- Confirm all gateway proxies are wired in desktop-integration and listed in its OpenAPI
- Regenerate and archive OpenAPI JSON snapshots for reproducible cataloging

