# Phase 5 Specification: Desktop App Setup

> **Status**: Ready for Implementation  
> **Phase**: 5 of 10  
> **Last Updated**: December 6, 2025  
> **Owner**: OpenTalent Core Team

## Executive Summary

Phase 5 establishes the foundational Electron desktop application structure that will serve as the runtime container for OpenTalent's local AI services. This phase focuses on project scaffolding, build infrastructure, and the first-time setup wizard that enables users to configure their environment based on hardware capabilities.

**Acceptance Criteria:**
- Electron app launches successfully on Windows, macOS, and Linux
- First-time setup wizard guides users through 4-step configuration
- Hardware detection automatically recommends appropriate model size
- Model download manager UI provides progress feedback
- All bundled binaries (Ollama, Piper) execute correctly on target platforms
- App packages successfully for all three platforms

## Business Objectives

1. **Enable Local-First Architecture** - Move from cloud-dependent to completely offline-capable platform
2. **Hardware Flexibility** - Support users across a 5-year hardware range (4GB-32GB+ RAM)
3. **Privacy Compliance** - Eliminate any cloud data transmission by design
4. **User Onboarding** - Reduce friction in first-time setup through intelligent recommendations

## Architecture Overview

```
Phase 5: Desktop App Setup
├── Project Structure
│   ├── Electron main process (Node.js)
│   ├── React renderer process (UI)
│   ├── Preload scripts (IPC security)
│   └── Build infrastructure (Windows/macOS/Linux)
│
├── Hardware Detection System
│   ├── RAM detection (psutil equivalent)
│   ├── CPU detection (core count, speed)
│   ├── GPU detection (NVIDIA, AMD, Apple Metal)
│   └── Model recommendation engine
│
├── First-Time Setup Wizard
│   ├── Step 1: Hardware analysis & display
│   ├── Step 2: Model recommendation with options
│   ├── Step 3: Model download with progress
│   └── Step 4: Voice selection & completion
│
└── Configuration Management
    ├── Config file structure (~/.config/opentalent/config.json)
    ├── Model directory structure (~/.cache/opentalent/models/)
    └── Preference persistence
```

## Requirements

### Functional Requirements

#### FR1: Electron Application Structure
- **Requirement**: Application shall follow standard Electron architecture with separate main and renderer processes
- **Details**:
  - Main process: Handles system integration, file I/O, process management, hardware detection
  - Renderer process: Implements React-based UI
  - Preload scripts: Provide secure IPC bridge between renderer and main
  - TypeScript support for type safety across codebase
- **Rationale**: Establishes secure, maintainable architecture for desktop application

#### FR2: Hardware Detection Module
- **Requirement**: System shall automatically detect hardware capabilities and recommend optimal model
- **Details**:
  - Detect total system RAM
  - Detect CPU core count and base frequency
  - Attempt GPU detection (NVIDIA CUDA, AMD ROCm, Apple Metal)
  - Generate recommendation: Granite-350M | Granite-2B | Granite-8B
  - Allow user override of recommendation
- **Rationale**: Removes burden from users to understand their hardware; prevents OOM failures

#### FR3: First-Time Setup Wizard
- **Requirement**: Application shall guide new users through 4-step configuration process
- **Steps**:
  1. **Hardware Analysis**: Display detected RAM/CPU/GPU, show memory breakdown
  2. **Model Selection**: Show recommendation with alternative options, explain trade-offs
  3. **Model Download**: Download selected model with progress bar, cancel option, error recovery
  4. **Voice Selection**: Choose TTS voice quality (small/medium/large), save preferences
- **Rationale**: Ensures users make informed decisions before downloading large models

#### FR4: Configuration Management
- **Requirement**: System shall persist user preferences and configuration across sessions
- **Details**:
  - Store in `~/.config/opentalent/config.json` (Linux), `~/Library/Application Support/opentalent/config.json` (macOS), `%APPDATA%/opentalent/config.json` (Windows)
  - Configuration schema: `{ selectedModel: string, selectedVoice: string, hardwareProfile: object, preferences: object }`
  - Allow settings UI to modify configuration later
  - Validate configuration on app startup
- **Rationale**: Enables preferences persistence and provides foundation for settings UI

#### FR5: Bundled Binary Management
- **Requirement**: Application shall bundle and execute platform-specific binaries for Ollama and Piper
- **Details**:
  - Bundle Ollama binaries for Windows (x64), macOS (arm64/x64 universal), Linux (x64)
  - Bundle Piper TTS binaries for all platforms
  - Verify binaries execute in `resources/binaries/` directory
  - Auto-detect binary availability for feature enabling
- **Rationale**: Enables true offline-first operation without requiring separate installations

### Non-Functional Requirements

#### NFR1: Performance
- **Requirement**: App startup shall complete in <5 seconds on target configurations
- **Details**:
  - Hardware detection: <500ms
  - UI rendering: <2s
  - Config loading: <100ms
- **Measurement**: Profile startup time, log results to `app.log`

#### NFR2: Memory Efficiency
- **Requirement**: Desktop app shall not exceed 400MB resident memory before model loading
- **Details**:
  - Electron overhead: <150MB
  - React UI + services: <250MB
  - Headroom for system operations
- **Rationale**: Preserves memory for model loading on 4GB systems

#### NFR3: Cross-Platform Compatibility
- **Requirement**: App shall function identically on Windows 10+, macOS 11+, Ubuntu 20.04+
- **Details**:
  - Test on Windows 10 (x64), Windows 11
  - Test on macOS 11+, macOS 12+ (Intel & Apple Silicon)
  - Test on Ubuntu 20.04 LTS, Ubuntu 22.04 LTS
  - Verify bundled binaries work on all tested platforms
- **Rationale**: Ensures feature parity across user base

#### NFR4: Security
- **Requirement**: IPC communication between renderer and main process shall be restricted to necessary operations
- **Details**:
  - Use preload scripts for selective API exposure
  - Validate all IPC messages
  - Disable nodeIntegration in renderer
  - Use contextIsolation: true
- **Rationale**: Prevents renderer compromise from accessing sensitive system operations

#### NFR5: Reliability
- **Requirement**: App shall not crash during setup wizard; errors shall be recoverable
- **Details**:
  - Catch and log all exceptions
  - Display user-friendly error messages
  - Allow restart of failed steps
  - Provide detailed logs for debugging
- **Rationale**: Establishes trust through stable user experience

## Task Decomposition

### Task Group A: Project Scaffolding (4 hours)

#### Task A1: Initialize Electron + React Project [1.5 hours]
- **Description**: Create base Electron + React project structure with TypeScript
- **Files Created**:
  - `desktop-app/package.json` - Dependencies: electron@^28.0.0, react@^18.0.0, typescript@^5.0
  - `desktop-app/tsconfig.json` - Strict TypeScript configuration
  - `desktop-app/src/main/main.ts` - Minimal Electron main process
  - `desktop-app/src/renderer/App.tsx` - Minimal React app
- **Acceptance Criteria**:
  - `npm start` launches Electron window with React app
  - No TypeScript errors
  - Dev tools open without errors
- **Dependencies**: None
- **Story Point Estimate**: 3 (beginner-friendly)

#### Task A2: Configure Build Infrastructure [1.5 hours]
- **Description**: Set up build scripts for Windows/macOS/Linux using electron-builder
- **Files Created**:
  - `desktop-app/electron-builder.yml` - Build configuration for all platforms
  - `desktop-app/scripts/build-win.sh` - Windows build script
  - `desktop-app/scripts/build-mac.sh` - macOS build script
  - `desktop-app/scripts/build-linux.sh` - Linux build script
  - `desktop-app/.github/workflows/build.yml` - CI/CD workflow (optional for Phase 5)
- **Acceptance Criteria**:
  - Each build script completes without errors
  - Output artifacts generated (`.exe` for Windows, `.dmg` for macOS, `.AppImage` for Linux)
  - Artifacts are executable
- **Dependencies**: Task A1
- **Story Point Estimate**: 3

#### Task A3: Implement TypeScript + ESLint Configuration [1 hour]
- **Description**: Configure TypeScript strict mode and linting for code quality
- **Files Created**:
  - `.eslintrc.json` - ESLint configuration
  - `desktop-app/tsconfig.json` updates - Strict mode enabled
  - `desktop-app/.prettierrc` - Code formatting
- **Acceptance Criteria**:
  - `npm run lint` passes with zero errors
  - `npm run format` fixes formatting issues
  - All existing code passes linting
- **Dependencies**: Task A1
- **Story Point Estimate**: 2

### Task Group B: Hardware Detection (5 hours)

#### Task B1: Create Hardware Detection Module [2 hours]
- **Description**: Implement system resource detection (RAM, CPU, GPU)
- **Files Created**:
  - `desktop-app/src/main/hardware-detector.ts` - Hardware detection logic
  - `desktop-app/src/main/hardware-detector.test.ts` - Unit tests
- **Requirements Addressed**: FR2
- **Acceptance Criteria**:
  - Detects RAM accurately (±5% tolerance)
  - Detects CPU core count correctly
  - Attempts GPU detection without crashing on systems without GPU
  - Returns hardware profile object
  - 95%+ test coverage
  - Returns results in <500ms
- **Dependencies**: Task A1
- **Story Point Estimate**: 5

#### Task B2: Implement Model Recommendation Engine [1.5 hours]
- **Description**: Create logic to recommend Granite model size based on hardware
- **Files Created**:
  - `desktop-app/src/main/model-recommender.ts` - Recommendation logic
  - `desktop-app/src/main/model-recommender.test.ts` - Unit tests
- **Requirements Addressed**: FR2
- **Recommendation Rules**:
  - `< 6GB RAM` → Granite-350M
  - `6-14GB RAM` → Granite-2B
  - `14GB+ RAM` → Granite-8B
- **Acceptance Criteria**:
  - Recommendations match requirements
  - All edge cases tested (exactly 6GB, 14GB boundaries)
  - 100% test coverage
- **Dependencies**: Task B1
- **Story Point Estimate**: 3

#### Task B3: Create Hardware Detection UI Component [1.5 hours]
- **Description**: Build React component to display hardware info and recommendations
- **Files Created**:
  - `desktop-app/src/renderer/components/HardwareDisplay.tsx` - UI component
  - `desktop-app/src/renderer/components/HardwareDisplay.test.tsx` - Component tests
- **Requirements Addressed**: FR3 (Step 1)
- **Acceptance Criteria**:
  - Displays RAM, CPU cores, GPU info
  - Shows memory breakdown (model + services + OS)
  - Shows recommended model with explanation
  - Component renders without errors
- **Dependencies**: Task B1, Task B2
- **Story Point Estimate**: 3

### Task Group C: First-Time Setup Wizard (8 hours)

#### Task C1: Implement Setup Wizard State Management [1.5 hours]
- **Description**: Create state management for 4-step wizard process
- **Files Created**:
  - `desktop-app/src/renderer/hooks/useSetupWizard.ts` - Wizard state hook
  - `desktop-app/src/renderer/context/SetupContext.tsx` - Context provider
  - `desktop-app/src/renderer/hooks/useSetupWizard.test.ts` - Tests
- **Requirements Addressed**: FR3
- **Acceptance Criteria**:
  - State tracks current step (1-4)
  - Can navigate forward/backward between steps
  - Persists selections across step changes
  - Validates step completion before allowing next step
  - 100% test coverage
- **Dependencies**: None
- **Story Point Estimate**: 3

#### Task C2: Build Model Selection UI [2 hours]
- **Description**: Create React component for model selection with options
- **Files Created**:
  - `desktop-app/src/renderer/components/ModelSelector.tsx` - Model selection UI
  - `desktop-app/src/renderer/components/ModelSelector.test.tsx` - Tests
  - `desktop-app/src/renderer/assets/model-descriptions.json` - Model info
- **Requirements Addressed**: FR3 (Step 2)
- **Model Info Displayed**:
  - Recommended model highlighted
  - Alternative models with trade-offs (speed vs quality)
  - RAM requirements
  - Download size
  - Use cases
- **Acceptance Criteria**:
  - All 3 models displayed with descriptions
  - Recommended model pre-selected
  - Can select alternative models
  - Component renders correctly
- **Dependencies**: Task C1, Task B2
- **Story Point Estimate**: 4

#### Task C3: Implement Model Download Manager [2 hours]
- **Description**: Create progress UI and download logic for models
- **Files Created**:
  - `desktop-app/src/main/model-downloader.ts` - Download logic
  - `desktop-app/src/renderer/components/ModelDownloadProgress.tsx` - Progress UI
  - `desktop-app/src/main/model-downloader.test.ts` - Tests
- **Requirements Addressed**: FR3 (Step 3)
- **Acceptance Criteria**:
  - Progress bar updates (0-100%)
  - Download speed displayed
  - Time remaining calculated
  - Cancel button works
  - Error recovery (retry on failure)
  - 95%+ test coverage
- **Dependencies**: Task A1, Task C1
- **Story Point Estimate**: 5

#### Task C4: Build Voice Selection UI [1 hour]
- **Description**: Create component for TTS voice quality selection
- **Files Created**:
  - `desktop-app/src/renderer/components/VoiceSelector.tsx` - Voice selection UI
  - `desktop-app/src/renderer/components/VoiceSelector.test.tsx` - Tests
- **Requirements Addressed**: FR3 (Step 4)
- **Voice Options**:
  - Small: 50MB, 100MB RAM, Good quality
  - Medium: 200MB, 200MB RAM, Very Good quality
  - Large: 500MB, 500MB RAM, Excellent quality
- **Acceptance Criteria**:
  - All 3 voices displayed with specifications
  - Can select voice
  - Selection persists
  - Component renders correctly
- **Dependencies**: Task C1
- **Story Point Estimate**: 2

#### Task C5: Integrate Setup Wizard into App [1.5 hours]
- **Description**: Wire all wizard components together in main app flow
- **Files Modified**:
  - `desktop-app/src/renderer/App.tsx` - Add wizard routing
  - `desktop-app/src/main/main.ts` - Add wizard completion logic
- **Requirements Addressed**: FR3
- **Acceptance Criteria**:
  - Wizard displays on first launch
  - Wizard skipped on subsequent launches
  - All 4 steps flow correctly
  - Selections saved to config
  - Completion navigates to main app
- **Dependencies**: Task C1, Task C2, Task C3, Task C4
- **Story Point Estimate**: 3

### Task Group D: Configuration Management (3 hours)

#### Task D1: Implement Config Manager [1.5 hours]
- **Description**: Create configuration file management system
- **Files Created**:
  - `desktop-app/src/main/config-manager.ts` - Config read/write logic
  - `desktop-app/src/main/config-manager.test.ts` - Tests
  - `desktop-app/src/types/config.ts` - Config TypeScript types
- **Requirements Addressed**: FR4
- **Config Schema**:
  ```json
  {
    "selectedModel": "granite-2b",
    "selectedVoice": "medium",
    "hardwareProfile": {
      "ramGb": 16,
      "cpuCores": 8,
      "gpuAvailable": true,
      "gpuType": "nvidia"
    },
    "preferences": {
      "autoUpdate": true,
      "analyticsEnabled": false,
      "theme": "dark"
    }
  }
  ```
- **Acceptance Criteria**:
  - Config created on first launch
  - Config loaded correctly on subsequent launches
  - Config validation catches corrupted files
  - Defaults applied for missing fields
  - 100% test coverage
- **Dependencies**: Task B1
- **Story Point Estimate**: 3

#### Task D2: Create Platform-Specific Config Paths [1 hour]
- **Description**: Implement platform-specific config directory detection
- **Files Modified**:
  - `desktop-app/src/main/config-manager.ts`
- **Requirements Addressed**: FR4
- **Path Logic**:
  - Linux: `~/.config/opentalent/`
  - macOS: `~/Library/Application Support/opentalent/`
  - Windows: `%APPDATA%/opentalent/`
- **Acceptance Criteria**:
  - Correct paths used on each platform
  - Directories created if missing
  - Works on all 3 platforms
- **Dependencies**: Task D1
- **Story Point Estimate**: 2

#### Task D3: Add Settings UI [1 hour]
- **Description**: Create settings page to modify configuration
- **Files Created**:
  - `desktop-app/src/renderer/pages/Settings.tsx` - Settings page
  - `desktop-app/src/renderer/pages/Settings.test.tsx` - Tests
- **Requirements Addressed**: FR4
- **Settings Available**:
  - Change model (restart required)
  - Change voice
  - Toggle auto-update
  - Toggle analytics
  - Theme selection
- **Acceptance Criteria**:
  - Settings load from config
  - Changes save to config
  - Validation applied before saving
  - Component renders correctly
- **Dependencies**: Task D1, Task D2
- **Story Point Estimate**: 2

### Task Group E: Binary Management (4 hours)

#### Task E1: Create Binary Resource Structure [1.5 hours]
- **Description**: Set up directory structure and scripts for bundled binaries
- **Files Created**:
  - `desktop-app/resources/binaries/README.md` - Binary documentation
  - `desktop-app/scripts/download-binaries.sh` - Binary download script
  - `desktop-app/src/main/binary-manager.ts` - Binary execution manager
- **Requirements Addressed**: FR5
- **Acceptance Criteria**:
  - Resource directories created correctly
  - Binary paths documented
  - Scripts executable
  - No binaries committed to git (use .gitignore)
- **Dependencies**: Task A1
- **Story Point Estimate**: 2

#### Task E2: Implement Binary Verification [1.5 hours]
- **Description**: Create checksum verification for downloaded binaries
- **Files Created**:
  - `desktop-app/src/main/binary-verifier.ts` - Binary verification logic
  - `desktop-app/src/main/binary-verifier.test.ts` - Tests
  - `desktop-app/resources/binaries/checksums.json` - Binary checksums
- **Requirements Addressed**: FR5
- **Acceptance Criteria**:
  - Checksums verified on app startup
  - Corrupted binaries detected
  - User warned of verification failures
  - 95%+ test coverage
- **Dependencies**: Task E1
- **Story Point Estimate**: 3

#### Task E3: Test Binary Execution [1 hour]
- **Description**: Verify bundled binaries execute correctly
- **Files Created**:
  - `desktop-app/src/main/__tests__/binary-execution.test.ts` - Integration tests
- **Requirements Addressed**: FR5
- **Acceptance Criteria**:
  - Ollama binary executes on all platforms
  - Piper binary executes on all platforms
  - Error handling works for missing binaries
  - 90%+ test coverage
- **Dependencies**: Task E2
- **Story Point Estimate**: 2

### Task Group F: Integration & Testing (5 hours)

#### Task F1: Create End-to-End Setup Test [2 hours]
- **Description**: Build E2E test for complete setup wizard flow
- **Files Created**:
  - `desktop-app/src/e2e/setup-wizard.e2e.test.ts` - E2E tests
- **Requirements Addressed**: FR3
- **Test Scenarios**:
  1. First launch → complete setup with Granite-2B
  2. First launch → select alternative model (Granite-350M)
  3. First launch → select large voice (Medium)
  4. Second launch → skip wizard, load config
  5. Error during download → retry successfully
- **Acceptance Criteria**:
  - All 5 scenarios pass
  - Setup time measured
  - No memory leaks detected
- **Dependencies**: Task C5, Task D1
- **Story Point Estimate**: 5

#### Task F2: Performance Profiling [1.5 hours]
- **Description**: Profile and optimize app startup and memory usage
- **Files Created**:
  - `desktop-app/scripts/profile-startup.js` - Startup profiling script
  - `desktop-app/src/main/__tests__/performance.test.ts` - Performance tests
- **Requirements Addressed**: NFR1, NFR2
- **Acceptance Criteria**:
  - Startup time <5s (target achieved)
  - Memory <400MB before model load
  - Results logged to `profiling-results.json`
  - Performance tested on target configs
- **Dependencies**: Task F1
- **Story Point Estimate**: 3

#### Task F3: Cross-Platform Testing [1.5 hours]
- **Description**: Test app on Windows, macOS, Linux
- **Manual Testing**:
  - Windows 10+ (x64)
  - macOS 11+ (Intel + Apple Silicon)
  - Ubuntu 20.04/22.04 LTS
- **Test Plan**:
  - App launches successfully
  - Setup wizard completes
  - Hardware detection works
  - Config saves/loads correctly
  - Binary execution verified
- **Requirements Addressed**: NFR3
- **Acceptance Criteria**:
  - App functions identically on all platforms
  - No platform-specific bugs
  - Binary compatibility verified
- **Dependencies**: Task A2, Task F1
- **Story Point Estimate**: 3

### Task Group G: Documentation (2 hours)

#### Task G1: Create Development Guide [1 hour]
- **Description**: Document setup, build, and development workflow
- **Files Created**:
  - `desktop-app/DEVELOPMENT.md` - Dev guide
  - `desktop-app/ARCHITECTURE.md` - Architecture overview
- **Acceptance Criteria**:
  - New developers can set up environment in <30 minutes
  - Build process documented
  - Debug workflow explained
- **Dependencies**: All tasks
- **Story Point Estimate**: 2

#### Task G2: Create User Documentation [1 hour]
- **Description**: Document first-time setup and model selection
- **Files Created**:
  - `docs/user-guides/getting-started.md` - Getting started guide
  - `docs/user-guides/model-selection.md` - Model selection guide
- **Acceptance Criteria**:
  - New users understand all options
  - Hardware recommendations explained
  - Troubleshooting guide provided
- **Dependencies**: All tasks
- **Story Point Estimate**: 2

## Lessons Learned (Template)

This section captures insights and decisions made during implementation. Update after each completed task:

```markdown
### Task: [Task ID]
**Decision**: [Key decision made]
**Rationale**: [Why this decision]
**Alternative Considered**: [Other option evaluated]
**Impact**: [Effect on timeline/quality]
**Applies To**: [Related tasks/future phases]
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Build Success Rate** | 100% | All 3 platform builds succeed |
| **Setup Wizard Completion** | 100% | Users complete wizard without errors |
| **App Startup Time** | <5s | Profiling results on target configs |
| **Memory Footprint** | <400MB | Peak memory before model load |
| **Cross-Platform Parity** | 100% | Feature parity on all 3 platforms |
| **Test Coverage** | 90%+ | Code coverage metrics |
| **Binary Execution** | 100% | Bundled binaries work on all platforms |

## Dependencies & Sequencing

```
Phase 5 Timeline (28 hours total)
├─ Task Group A: Scaffolding (4h) ████
│  ├─ A1: Electron + React (1.5h)
│  ├─ A2: Build Infrastructure (1.5h) [depends: A1]
│  └─ A3: TypeScript + ESLint (1h) [depends: A1]
│
├─ Task Group B: Hardware (5h) █████
│  ├─ B1: Hardware Detection (2h) [depends: A1]
│  ├─ B2: Model Recommendation (1.5h) [depends: B1]
│  └─ B3: Hardware UI (1.5h) [depends: B1, B2]
│
├─ Task Group C: Setup Wizard (8h) ████████
│  ├─ C1: State Management (1.5h)
│  ├─ C2: Model Selection UI (2h) [depends: C1, B2]
│  ├─ C3: Download Manager (2h) [depends: A1, C1]
│  ├─ C4: Voice Selection UI (1h) [depends: C1]
│  └─ C5: Wizard Integration (1.5h) [depends: C1-C4]
│
├─ Task Group D: Configuration (3h) ███
│  ├─ D1: Config Manager (1.5h) [depends: B1]
│  ├─ D2: Platform Paths (1h) [depends: D1]
│  └─ D3: Settings UI (1h) [depends: D1, D2]
│
├─ Task Group E: Binaries (4h) ████
│  ├─ E1: Binary Structure (1.5h) [depends: A1]
│  ├─ E2: Binary Verification (1.5h) [depends: E1]
│  └─ E3: Binary Execution Test (1h) [depends: E2]
│
└─ Task Group F-G: Testing & Docs (7h) [depends: All above]
   ├─ F1: E2E Setup Test (2h)
   ├─ F2: Performance Profiling (1.5h)
   ├─ F3: Cross-Platform Testing (1.5h)
   ├─ G1: Development Guide (1h)
   └─ G2: User Documentation (1h)
```

## Implementation Notes

### Technology Stack Rationale

**Electron** chosen over Tauri because:
- Mature ecosystem with extensive support
- Easier cross-platform binary bundling
- Better compatibility with existing Node.js services

**React** chosen for UI because:
- Aligns with existing frontend expertise
- Rich component ecosystem
- Strong TypeScript support

**TypeScript** required for:
- Type safety across codebase
- Better IDE support
- Fewer runtime errors

### Known Constraints

1. **Binary Size**: Combined Ollama + Piper binaries may exceed 1GB; consider compression
2. **Platform Specifics**: macOS universal binary requires special build handling
3. **GPU Detection**: GPU detection is platform-specific (nvidia-smi on Linux/Windows, Metal on macOS)
4. **Config Migration**: Future phases may require config schema migration logic

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Binary size too large | Implement delta/incremental downloads in Phase 6 |
| GPU detection fails | Graceful degradation; allow manual configuration |
| Setup wizard complexity | Extensive user testing; simplify if needed |
| Cross-platform issues | Test on VMs for all platforms before release |

## Next Phase Preview

Phase 6 (Ollama Integration) will:
- Integrate Ollama API with conversation service
- Add model download and management
- Implement 4-bit/8-bit quantization selection
- Add GPU acceleration support

**Phase 5 must complete before Phase 6 begins** because:
- Ollama execution depends on binary management (Task E)
- Model download UI foundation needed (Task C3)
- Configuration system required (Task D)
