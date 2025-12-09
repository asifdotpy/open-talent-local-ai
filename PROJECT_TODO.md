# OpenTalent — Project Todo (Comprehensive)

**Last Updated:** December 5, 2025

This file captures the current project todo list with detailed descriptions for future reference.

## Completed
- **Project Migration to open-talent** — Migrated from talent-ai-platform with fresh git history and selective file copying (46,111 files migrated).
- **Documentation Organization** — All markdown files organized into `specs/` hierarchy (architectural-specs, api-contracts, protocols, requirements, user-stories, project, development, migration, governance).
- **Development Standards Setup** — Comprehensive dev environment with 50+ packages (pytest, black, ruff, mypy, ggshield, bandit, etc.) and 15+ pre-commit hooks.
- **Security Infrastructure** — Security tools configured (ggshield, bandit, safety) and SECURITY.md created with vulnerability reporting.
- **Git Commit All Infrastructure** — All development standards, security policy, and setup scripts committed (commits: b17226e, 28817a0).
- **LOCAL AI ARCHITECTURE REDESIGN (CRITICAL)** — Architectural shift to local on-device AI: desktop app (no cloud), Granite 4 models (350M/2B/8B), low-RAM optimization, hardware detection/recommendation, all services local-capable.
- **Document local AI architecture** — Created LOCAL_AI_ARCHITECTURE.md (600+ lines) and AGENTS.md overview with Granite models, Ollama integration, Piper TTS, Electron desktop app, hardware detection, and 6-phase plan.

## In Progress / Planned

### Phase 5: Desktop App Setup (SPECS DRIVEN) 📋
**Status**: Specifications complete, ready for implementation  
**Effort**: 28 hours | **Teams**: 7 task groups  
**Specs**: 
- [phase-5-desktop-app-setup.md](specs/phase-5-desktop-app-setup.md) — Complete specification with requirements, acceptance criteria, task decomposition
- [phase-5-task-execution-guide.md](specs/phase-5-task-execution-guide.md) — Machine-readable task breakdown for AI agent implementation
- [phase-5-lessons-learned.md](specs/phase-5-lessons-learned.md) — Living document for capturing implementation insights

**Core Tasks**:
- **Task Group A: Scaffolding (4h)** — Initialize Electron + React, build infrastructure, TypeScript config
- **Task Group B: Hardware Detection (5h)** — RAM/CPU/GPU detection, model recommendation engine, UI display
- **Task Group C: Setup Wizard (8h)** — 4-step wizard: hardware → model selection → download → voice selection
- **Task Group D: Configuration (3h)** — Config file management, platform paths, settings UI
- **Task Group E: Binary Management (4h)** — Bundled binary structure, verification, execution testing
- **Task Group F-G: Testing & Docs (5h)** — E2E tests, performance profiling, cross-platform validation, documentation

**Success Criteria**:
- ✅ Electron app launches on Windows/macOS/Linux
- ✅ Setup wizard completes 4-step configuration
- ✅ Hardware detection recommends correct model size
- ✅ App startup <5s, memory <400MB
- ✅ All 3 platform builds successful

### Phase 6: Ollama Integration (Planned)
- **Integrate Ollama for Granite models** — Use hardware detection from Phase 5 to auto-select model; bundle Ollama binary; implement model download manager; integrate Granite 4 (350M/2B/8B); 4-bit/8-bit quantization support.

### Phase 7: Piper TTS Integration (Planned)
- **Replace OpenAI TTS with Piper TTS** — Use voice selection from Phase 5; bundle Piper binary; download voice models (50MB/200MB/500MB); implement TTS API; audio quality tests.

### Phase 8-9: Avatar & Testing (Planned)
- **Implement local avatar rendering** — WebGL/Three.js renderer; phoneme lip-sync; avatar customization UI; target 30 FPS; avatar state caching.
- **Test on low-end hardware** — Benchmark Granite-350M on 4GB RAM laptop (2015+); target <5s app startup, <2s first response; memory profile (<2.5GB for model+services); optimize as needed.

### Phase 10: Production Release (Planned)
- **Package desktop app for all platforms** — Build Windows installer (.exe), macOS .dmg (universal), Linux AppImage; test on fresh VMs; verify bundled binaries work everywhere.
