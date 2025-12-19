# How to Start the Desktop Application

**Last Updated:** December 18, 2025  
**Applies To:** OpenTalent desktop app (Electron + React) with Desktop Integration Service (gateway)

---

## Quick Start (Recommended)
1) **Start the Gateway (port 8009)**
```bash
cd microservices/desktop-integration-service
./start.sh
# Docs: http://localhost:8009/docs
# Health: http://localhost:8009/health
```

2) **Start the Desktop App** (Electron dev with hot reload)
```bash
cd desktop-app
npm run dev
```

3) **Use the Demo Helper (optional, fastest demo path)**
```bash
cd desktop-app
npx ts-node src/services/interview-demo-helper.ts
```
This runs interview + (optional) voice synthesis + sentiment analysis via the gateway. Ideal for quick video recordings.

---

## Detailed Steps

### Prerequisites
- Node 20+ installed
- Dependencies installed:
  ```bash
  cd desktop-app
  npm install
  ```
- Python available for gateway (prefers 3.12 → 3.11 → 3.13)

### 1) Start the Gateway
- Command:
  ```bash
  cd microservices/desktop-integration-service
  ./start.sh
  ```
- What it does:
  - Starts Desktop Integration Service on **http://localhost:8009**
  - Exposes OpenAPI at `/docs` and `/openapi.json`
  - Routes to microservices; falls back to **Ollama** if others are offline

### 2) (Optional) Verify Schemas
```bash
curl -s http://localhost:8009/openapi.json | jq '.paths."/api/v1/voice/synthesize".post.requestBody.content'
# Expect $ref to SynthesizeSpeechRequest
```

### 3) Start the Desktop App (Electron)
- Command:
  ```bash
  cd desktop-app
  npm run dev
  ```
- Opens the Electron window with live reload.

### 4) Run the Demo Helper (CLI flow)
- Fastest way to demonstrate full flow without UI clicks:
  ```bash
  cd desktop-app
  npx ts-node src/services/interview-demo-helper.ts
  ```
- Shows: models → start interview → voice synthesis (if enabled) → sentiment → summary.

---

## Troubleshooting
- **Port 8009 in use:** Stop other gateway instances or change port in gateway settings.
- **Voice/analytics offline:** Gateway gracefully falls back; you can still demo interview via Ollama.
- **Type errors in frontend:** Regenerate client: `npm run gen:gateway:all`.
- **Python build issues:** Gateway start script prefers 3.12/3.11; uses wheels for pydantic-core.

---

## Useful Commands
```bash
# Regenerate gateway client & types
cd desktop-app && npm run gen:gateway:all

# Run E2E tests (gateway interview + voice/analytics)
cd desktop-app
npm test -- -t "Gateway Interview Flow"
npm test -- -t "Voice & Analytics"
```

---

## What to Show in a Demo
- Service health in UI header (real-time)
- Start interview → answer → summary
- Voice synthesis of a question (if voice service available)
- Sentiment analysis of a response (if analytics service available)
- Graceful fallback when services are offline (Ollama default)

---

## References
- Gateway OpenAPI: http://localhost:8009/docs
- Typed client summary: TYPED_GATEWAY_CLIENT_COMPLETE.md
- Schema fix details: VOICE_ANALYTICS_SCHEMA_FIX_DEC18.md
