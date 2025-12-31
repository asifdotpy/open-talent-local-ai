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

---

## ⚠️ Current Project Status: Week 4 Development

The project is currently in **Week 4** of the desktop application development, focusing on **Outreach Automation, Enrichment, and Progress Tracking**.

| Feature Set | Status | Notes |
| :--- | :--- | :--- |
| **Local AI Core** | **Complete** | Ollama, Granite 4, Piper TTS architecture is defined and services are being integrated. |
| **Desktop App UI** | **In Progress** | Core UI components for Week 4 features (Outreach, Enrichment, Progress Panel) are implemented in the `desktop-app/src/renderer` directory. |
| **Integration** | **Blocked** | The desktop application is currently blocked by several TypeScript compilation and test failures (see **SETUP_GUIDE.md** for details). |

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

## 🛠️ Getting Started (Developer Setup)

For a complete, step-by-step guide on setting up the development environment, installing dependencies, and running tests on a fresh machine, please refer to the dedicated setup guide:

➡️ **[SETUP_GUIDE.md](SETUP_GUIDE.md)**

### Quick Manual Setup

1.  **Clone:** `git clone https://github.com/asifdotpy/open-talent-local-ai.git open-talent`
2.  **Install Node Deps:** `cd open-talent/desktop-app && npm install --legacy-peer-deps`
3.  **Install Python Deps:** `cd .. && source .venv/bin/activate && pip install -r requirements.txt`
4.  **Run:** `./start-demo.sh`

---

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
