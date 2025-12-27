# OpenTalent Local AI Interview Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Security-Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)
![Security-Semgrep](https://img.shields.io/badge/security-semgrep-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Code Quality](https://img.shields.io/badge/code%20quality-ruff-blue.svg)

Privacy-first, desktop-first interview platform that runs 100% locally. No cloud calls, no API keys, no data leaves the user's device.

---

## 🚀 Demo Environment (Ready Now!)

**Experience OpenTalent's enhanced interview analytics today!**

### Quick Start

```bash
# Start the complete demo environment
./start-demo.sh

# Access the application
open http://localhost:3000

# Stop when done
./stop-demo.sh
```

### What You'll See

- **Enhanced Interview Results**: Sentiment analysis, quality scoring, and AI recommendations
- **Real-time Analytics**: Live processing during interviews with visual feedback
- **Privacy-First**: Everything runs locally - no cloud dependencies
- **Rich Insights**: Comprehensive candidate assessment with detailed metrics

### Demo Flow

1. **Start**: `./start-demo.sh` (2-3 minutes setup)
2. **Interview**: Enter "test-001" → Select "Frontend" → Start Interview
3. **Results**: View enhanced analytics dashboard with charts and recommendations
4. **Stop**: `./stop-demo.sh`

### Documentation

- **[DEMO_ENVIRONMENT_GUIDE.md](DEMO_ENVIRONMENT_GUIDE.md)**: Complete setup and troubleshooting guide
- **[DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)**: Quick commands and demo script
- **[INTERVIEW_RESULTS_ENHANCEMENT_PLAN.md](INTERVIEW_RESULTS_ENHANCEMENT_PLAN.md)**: Technical implementation details

---

## What this repo is

- Source of truth for OpenTalent's offline AI interview stack (Electron desktop app, local AI services, docs).
- Implements the December 2025 pivot to local AI (Ollama + Granite 4 models, Piper TTS, WebGL avatar) as defined in [AGENTS.md](AGENTS.md) and [LOCAL_AI_ARCHITECTURE.md](LOCAL_AI_ARCHITECTURE.md).
- Not affiliated with the UK-based "Open Talent" HR services company on LinkedIn; this is an open-source, local-AI interview project.

## Core capabilities

- Local LLM conversation via Ollama using Granite 4 models (350M / 2B / 8B; 4-bit/8-bit).
- Local TTS with Piper (small/medium/large voice models) and audio caching.
- WebGL/Three.js avatar with phoneme-driven lip-sync.
- Hardware-aware model selection (RAM-based recommendations with user override).
- Offline-first packaging: Electron bundles Ollama and Piper binaries for Windows/macOS/Linux.

## Architecture (current plan)

- Desktop app (Electron + React) with setup wizard, settings, and avatar UI.
- Local services orchestrated by the Electron main process: Ollama server, Piper TTS, hardware detection, model download manager.
- Model store under `~/OpenTalent/models/` with Granite and Piper artifacts; caches for conversations, audio, and avatars.
- Security posture: zero cloud dependencies, no key storage, local logs only (see [SECURITY_AND_CODE_QUALITY_CHECKLIST.md](SECURITY_AND_CODE_QUALITY_CHECKLIST.md)).

## Repo layout (high level)

- [AGENTS.md](AGENTS.md): Architecture overview and current phase plan.
- [LOCAL_AI_ARCHITECTURE.md](LOCAL_AI_ARCHITECTURE.md): Detailed local AI spec.
- [CONTRIBUTING.md](CONTRIBUTING.md): Dev standards and workflow.
- [specs/](specs): Architectural specs, API contracts, requirements.
- [services/](services): Conversation, voice, avatar, and interview services (offline-focused).
- [desktop-app/](desktop-app): Electron app scaffolding (planned/under construction).

## Avatar Service — Finalized (December 17, 2025)

- **Status:** Duplicates resolved, `avatar_v1` exposed under `/api/v1/avatars`, OpenAPI verified.
- **Core endpoints:** `/`, `/ping`, `/health`, `/api/v1/voices` (GET), `/api/v1/generate-voice` (POST), `/render/lipsync` (POST).
- **Avatar V1 suite:** Rendering, lipsync, presets, config, performance, state/emotions, assets/models, sessions, voice attach/detach.
- **Docs:**
  - [services/avatar-service/ENDPOINT_SPECIFICATION.md](services/avatar-service/ENDPOINT_SPECIFICATION.md)
  - [services/avatar-service/API_ENDPOINTS_STATUS.md](services/avatar-service/API_ENDPOINTS_STATUS.md)
  - [services/avatar-service/API_COMPLETE_SUMMARY.md](services/avatar-service/API_COMPLETE_SUMMARY.md)

Quick verify:

```bash
curl -s http://127.0.0.1:8001/openapi.json | jq -r '.paths | keys[]'
curl -s http://127.0.0.1:8001/openapi.json | jq -r '.paths | keys[] | select(startswith("/api/v1/avatars"))'
```

## Hardware guidance

- Granite-350M: 2-4GB RAM (minimal), ~400MB download, fastest.
- Granite-2B: 8-12GB RAM (balanced), ~1.2GB download.
- Granite-8B: 16-32GB RAM (maximum quality), ~4.5GB download.

## Getting started (dev)

### Demo Environment (Recommended)

For the best experience, use the automated demo environment:

```bash
./start-demo.sh  # Start all services
# Access: http://localhost:3000
./stop-demo.sh   # Stop all services
```

### Manual Development Setup

1) Prereqs: Node 20+, Python 3.12+, Git, `ollama` (optional for local testing), `piper` binary (optional).
2) Install deps:

```bash
npm install
pip install -r requirements.txt
```

3) Run dev environment (placeholder commands; desktop app wiring in progress):

```bash
npm run dev
```

## Roadmap (abridged)

- Phase 5: Electron desktop app setup, bundle Ollama/Piper binaries, setup wizard and hardware detection.
- Phase 6: Ollama integration with Granite 4 model selection and GPU acceleration paths.
- Phase 7: Piper TTS integration with quality tiers and caching.
- Phase 8: Avatar rendering with lip-sync and caching.
- Phase 9: Benchmarks on low-end/high-end hardware; optimization and testing.

## Security and privacy

- 100% offline operation after initial model download.
- No cloud telemetry or external API calls.
- Local logs and caches under `~/OpenTalent/` with optional purge/export.
- Automated security checks documented in [SECURITY_AND_CODE_QUALITY_CHECKLIST.md](SECURITY_AND_CODE_QUALITY_CHECKLIST.md) and [SECURITY_QUICK_START.md](SECURITY_QUICK_START.md).

## Contact / support

- Issues and discussions: use the GitHub repo once created (private for now).
- Branding note: unrelated to the HR firm "Open Talent" on LinkedIn; this project focuses on an offline AI interview desktop app.
