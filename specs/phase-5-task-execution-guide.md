# Phase 5 Task Execution Guide

> **Format**: Machine-Readable Task Breakdown  
> **Purpose**: AI Agent Implementation Reference  
> **Last Updated**: December 6, 2025

## Quick Reference

**Total Effort**: 28 hours  
**Parallel Workstreams**: 7 task groups  
**Critical Path**: Task Groups A → C/D/E → F/G  
**Expected Completion**: 1-2 weeks (depending on team size)

## Task Execution Format

Each task follows this structure for AI agent implementation:

```
[Task ID]: [Title]
├─ Duration: X hours
├─ Depends On: [Task IDs]
├─ Acceptance Criteria: [AC1, AC2, ...]
├─ Implementation Guide:
│  ├─ Files to Create: [list]
│  ├─ Files to Modify: [list]
│  └─ Code Patterns: [patterns to follow]
└─ Validation: [How to verify completion]
```

---

## Task Group A: Project Scaffolding

### A1: Initialize Electron + React Project
**Duration**: 1.5 hours  
**Depends On**: None  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Electron window launches with React app
- [ ] App window shows React component
- [ ] No TypeScript errors reported
- [ ] DevTools open successfully
- [ ] Hot reload works (modify .tsx file, app updates)

**Implementation Checklist**:
```bash
# Create project directory
mkdir -p desktop-app/src/{main,renderer,types,preload}

# Initialize npm and install dependencies
npm init -y
npm install --save electron react react-dom
npm install --save-dev typescript @types/react @types/react-dom @types/node electron-dev-loader esbuild
```

**Files to Create**:
1. `desktop-app/package.json` - Project dependencies and scripts
2. `desktop-app/tsconfig.json` - TypeScript configuration
3. `desktop-app/src/main/main.ts` - Electron main process
4. `desktop-app/src/renderer/App.tsx` - React root component
5. `desktop-app/src/renderer/index.tsx` - React entry point
6. `desktop-app/src/preload/preload.ts` - IPC bridge

**Code Patterns**:
- Use `createWindow()` pattern in main.ts
- Implement IPC with `ipcMain` on main, `ipcRenderer` on renderer
- Use Context API for state management
- Follow ES modules (import/export)

**Validation**:
```bash
npm start              # Should launch app without errors
npm run build         # Should build successfully
```

---

### A2: Configure Build Infrastructure
**Duration**: 1.5 hours  
**Depends On**: A1  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] `electron-builder` generates `.exe` for Windows
- [ ] `electron-builder` generates `.dmg` for macOS (universal binary)
- [ ] `electron-builder` generates `.AppImage` for Linux
- [ ] All artifacts are executable
- [ ] No build errors on any platform

**Implementation Checklist**:
```bash
npm install --save-dev electron-builder
```

**Files to Create**:
1. `electron-builder.yml` - Build configuration (all platforms)
2. `scripts/build-win.sh` - Windows build script
3. `scripts/build-mac.sh` - macOS build script
4. `scripts/build-linux.sh` - Linux build script

**electron-builder.yml Template**:
```yaml
appId: com.opentalent.app
productName: OpenTalent

directories:
  buildResources: resources
  output: dist

files:
  - from: .
    to: .
    filter:
      - package.json
      - dist/**/*
      - node_modules/**/*

nsis:
  oneClick: false
  installerIcon: resources/icon.ico
  uninstallerIcon: resources/icon.ico

mac:
  target:
    - dmg
    - zip
  universal: true
  
linux:
  target:
    - AppImage
```

**Validation**:
```bash
./scripts/build-win.sh      # Generate Windows .exe
./scripts/build-mac.sh      # Generate macOS .dmg
./scripts/build-linux.sh    # Generate Linux .AppImage
```

---

### A3: Implement TypeScript + ESLint Configuration
**Duration**: 1 hour  
**Depends On**: A1  
**Story Points**: 2

**Acceptance Criteria**:
- [ ] `npm run lint` runs without errors
- [ ] `npm run format` formats code consistently
- [ ] TypeScript strict mode enabled
- [ ] All existing code passes linting

**Implementation Checklist**:
```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier
npx eslint --init
```

**Files to Create**:
1. `.eslintrc.json` - ESLint rules
2. `desktop-app/.prettierrc` - Code formatting
3. `.eslintignore` - Files to skip linting

**.eslintrc.json Template**:
```json
{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2021,
    "sourceType": "module"
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-types": "warn"
  }
}
```

**Validation**:
```bash
npm run lint    # Should report zero errors
npm run format  # Should format code
```

---

## Task Group B: Hardware Detection

### B1: Create Hardware Detection Module
**Duration**: 2 hours  
**Depends On**: A1  
**Story Points**: 5

**Acceptance Criteria**:
- [ ] Detects RAM accurately (±5% tolerance)
- [ ] Detects CPU core count
- [ ] Attempts GPU detection without crashing
- [ ] Returns hardwareProfile object
- [ ] All tests pass (95%+ coverage)
- [ ] Execution completes in <500ms

**Implementation Checklist**:
```bash
npm install os systeminformation
npm install --save-dev @types/node
```

**Files to Create**:
1. `src/main/hardware-detector.ts` - Detection logic
2. `src/main/hardware-detector.test.ts` - Unit tests

**HardwareProfile Interface**:
```typescript
interface HardwareProfile {
  ramGb: number;           // Total system RAM in GB
  ramAvailable: number;    // Available RAM in GB
  cpuCores: number;        // Logical CPU cores
  cpuModel: string;        // CPU model name
  gpuAvailable: boolean;
  gpuType: 'nvidia' | 'amd' | 'apple-metal' | 'unknown';
  platform: 'windows' | 'darwin' | 'linux';
  arch: 'x64' | 'arm64' | 'ia32';
  timestamp: number;       // Detection timestamp
}
```

**Code Pattern**:
```typescript
export class HardwareDetector {
  static async detect(): Promise<HardwareProfile> {
    const osModule = require('os');
    const ramGb = osModule.totalmem() / (1024 ** 3);
    const cpuCores = osModule.cpus().length;
    // ... GPU detection logic
    return hardwareProfile;
  }
}
```

**GPU Detection Logic**:
- Windows/Linux: Try `nvidia-smi` command
- macOS: Check for Metal support (always available)
- Fallback: Mark as 'unknown'

**Validation**:
```bash
npm test -- hardware-detector.test.ts
```

---

### B2: Implement Model Recommendation Engine
**Duration**: 1.5 hours  
**Depends On**: B1  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Granite-350M recommended for <6GB RAM
- [ ] Granite-2B recommended for 6-14GB RAM
- [ ] Granite-8B recommended for 14GB+ RAM
- [ ] All boundary cases tested
- [ ] 100% test coverage

**Files to Create**:
1. `src/main/model-recommender.ts` - Recommendation logic
2. `src/main/model-recommender.test.ts` - Tests

**Recommendation Algorithm**:
```typescript
export class ModelRecommender {
  static recommend(hardwareProfile: HardwareProfile): string {
    const ramGb = hardwareProfile.ramGb;
    
    if (ramGb < 6) return 'granite-350m';
    if (ramGb < 14) return 'granite-2b';
    return 'granite-8b';
  }
}
```

**Test Cases**:
- RAM = 4GB → Granite-350M
- RAM = 6GB → Granite-2B (boundary)
- RAM = 14GB → Granite-8B (boundary)
- RAM = 32GB → Granite-8B

**Validation**:
```bash
npm test -- model-recommender.test.ts
```

---

### B3: Create Hardware Detection UI Component
**Duration**: 1.5 hours  
**Depends On**: B1, B2  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Displays RAM, CPU cores, GPU info
- [ ] Shows memory breakdown visualization
- [ ] Shows recommended model
- [ ] Component renders without errors
- [ ] Responsive layout (mobile-friendly)

**Files to Create**:
1. `src/renderer/components/HardwareDisplay.tsx` - React component
2. `src/renderer/components/HardwareDisplay.test.tsx` - Tests
3. `src/renderer/styles/HardwareDisplay.css` - Styling

**Component Props**:
```typescript
interface HardwareDisplayProps {
  hardwareProfile: HardwareProfile;
  recommendedModel: string;
}
```

**Display Information**:
- Total RAM (GB)
- Available RAM (GB)
- CPU cores and model
- GPU availability
- Memory breakdown (model + services + OS + headroom)
- Recommended model with rationale

**Validation**:
```bash
npm test -- HardwareDisplay.test.tsx
```

---

## Task Group C: First-Time Setup Wizard

### C1: Implement Setup Wizard State Management
**Duration**: 1.5 hours  
**Depends On**: None  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] State tracks current step (1-4)
- [ ] Can navigate forward/backward
- [ ] Selections persist across steps
- [ ] Step completion validated before advancing
- [ ] 100% test coverage

**Files to Create**:
1. `src/renderer/hooks/useSetupWizard.ts` - Custom hook
2. `src/renderer/context/SetupContext.tsx` - Context provider
3. `src/renderer/hooks/useSetupWizard.test.ts` - Tests

**SetupContext Interface**:
```typescript
interface SetupState {
  currentStep: 1 | 2 | 3 | 4;
  selectedModel: string | null;
  selectedVoice: string | null;
  isComplete: boolean;
  hardwareProfile: HardwareProfile | null;
}

interface SetupContextValue extends SetupState {
  nextStep: () => void;
  prevStep: () => void;
  selectModel: (model: string) => void;
  selectVoice: (voice: string) => void;
  completeSetup: () => void;
}
```

**Validation**:
```bash
npm test -- useSetupWizard.test.ts
```

---

### C2: Build Model Selection UI
**Duration**: 2 hours  
**Depends On**: C1, B2  
**Story Points**: 4

**Acceptance Criteria**:
- [ ] All 3 models displayed (350M, 2B, 8B)
- [ ] Recommended model pre-selected
- [ ] Can select alternative models
- [ ] Trade-offs explained (speed vs quality)
- [ ] Component renders correctly
- [ ] Mobile-responsive

**Files to Create**:
1. `src/renderer/components/ModelSelector.tsx` - Component
2. `src/renderer/components/ModelSelector.test.tsx` - Tests
3. `src/renderer/assets/model-descriptions.json` - Model info

**model-descriptions.json**:
```json
{
  "granite-350m": {
    "name": "Granite 350M",
    "ramGb": 2,
    "downloadSizeMb": 400,
    "speedRating": "⚡ Very Fast",
    "qualityRating": "⭐⭐⭐",
    "useCase": "Low-end laptops (2015+)",
    "description": "Compact model for resource-constrained devices"
  },
  "granite-2b": {
    "name": "Granite 2B",
    "ramGb": 8,
    "downloadSizeMb": 1200,
    "speedRating": "⚡ Fast",
    "qualityRating": "⭐⭐⭐⭐",
    "useCase": "Mid-range laptops (2018+)",
    "description": "Balanced performance and quality"
  },
  "granite-8b": {
    "name": "Granite 8B",
    "ramGb": 16,
    "downloadSizeMb": 4500,
    "speedRating": "⚡ Moderate",
    "qualityRating": "⭐⭐⭐⭐⭐",
    "useCase": "High-end workstations",
    "description": "Maximum quality for powerful machines"
  }
}
```

**Validation**:
```bash
npm test -- ModelSelector.test.tsx
```

---

### C3: Implement Model Download Manager
**Duration**: 2 hours  
**Depends On**: A1, C1  
**Story Points**: 5

**Acceptance Criteria**:
- [ ] Progress bar updates (0-100%)
- [ ] Download speed displayed
- [ ] Time remaining calculated
- [ ] Cancel button works
- [ ] Error recovery (retry on failure)
- [ ] 95%+ test coverage

**Files to Create**:
1. `src/main/model-downloader.ts` - Download logic
2. `src/renderer/components/ModelDownloadProgress.tsx` - Progress UI
3. `src/main/model-downloader.test.ts` - Tests

**ModelDownloader Class**:
```typescript
export class ModelDownloader {
  async download(modelId: string, onProgress?: (progress: DownloadProgress) => void): Promise<void> {
    // Fetch model from remote source
    // Report progress via callback
    // Save to ~/.cache/opentalent/models/
  }
}

interface DownloadProgress {
  percent: number;        // 0-100
  bytesDownloaded: number;
  bytesTotal: number;
  speedMbps: number;
  estimatedSecondsRemaining: number;
}
```

**Error Handling**:
- Network errors → Retry logic (3 retries)
- Disk full → Clear error message
- Corrupted download → Delete and retry

**Validation**:
```bash
npm test -- model-downloader.test.ts
```

---

### C4: Build Voice Selection UI
**Duration**: 1 hour  
**Depends On**: C1  
**Story Points**: 2

**Acceptance Criteria**:
- [ ] All 3 voices displayed (small/medium/large)
- [ ] Specifications shown for each voice
- [ ] Can select voice
- [ ] Selection persists
- [ ] Component renders correctly

**Files to Create**:
1. `src/renderer/components/VoiceSelector.tsx` - Component
2. `src/renderer/components/VoiceSelector.test.tsx` - Tests

**Voice Options**:
```typescript
{
  small: { size: '50MB', ram: '100MB', quality: 'Good' },
  medium: { size: '200MB', ram: '200MB', quality: 'Very Good' },
  large: { size: '500MB', ram: '500MB', quality: 'Excellent' }
}
```

**Validation**:
```bash
npm test -- VoiceSelector.test.tsx
```

---

### C5: Integrate Setup Wizard into App
**Duration**: 1.5 hours  
**Depends On**: C1, C2, C3, C4  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Wizard displays on first launch
- [ ] Wizard skipped on subsequent launches
- [ ] All 4 steps flow correctly
- [ ] Selections saved to config
- [ ] Completion navigates to main app

**Files to Modify**:
1. `src/renderer/App.tsx` - Add wizard routing
2. `src/main/main.ts` - Add wizard completion logic

**Implementation Logic**:
```typescript
// App.tsx
if (setupState.isComplete) {
  return <MainApp />;
} else {
  return <SetupWizard />;
}

// main.ts
const isFirstLaunch = !fs.existsSync(configPath);
if (isFirstLaunch) {
  showSetupWizard();
}
```

**Validation**:
```bash
npm run dev
# Should show setup wizard on first run
# Should skip setup wizard on second run
```

---

## Task Group D: Configuration Management

### D1: Implement Config Manager
**Duration**: 1.5 hours  
**Depends On**: B1  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Config created on first launch
- [ ] Config loaded on subsequent launches
- [ ] Config validation catches corruption
- [ ] Defaults applied for missing fields
- [ ] 100% test coverage

**Files to Create**:
1. `src/main/config-manager.ts` - Config logic
2. `src/main/config-manager.test.ts` - Tests
3. `src/types/config.ts` - TypeScript types

**ConfigManager Class**:
```typescript
export class ConfigManager {
  static load(): Config;
  static save(config: Config): void;
  static getDefault(): Config;
}

interface Config {
  version: string;
  selectedModel: 'granite-350m' | 'granite-2b' | 'granite-8b';
  selectedVoice: 'small' | 'medium' | 'large';
  hardwareProfile: HardwareProfile;
  preferences: {
    autoUpdate: boolean;
    analyticsEnabled: boolean;
    theme: 'light' | 'dark';
  };
  timestamps: {
    created: number;
    lastModified: number;
  };
}
```

**Validation**:
```bash
npm test -- config-manager.test.ts
```

---

### D2: Create Platform-Specific Config Paths
**Duration**: 1 hour  
**Depends On**: D1  
**Story Points**: 2

**Acceptance Criteria**:
- [ ] Correct paths used on each platform
- [ ] Directories created if missing
- [ ] Works on Windows/macOS/Linux

**Implementation**:
```typescript
function getConfigDir(): string {
  const platform = process.platform;
  
  if (platform === 'win32') {
    return path.join(process.env.APPDATA || '', 'opentalent');
  } else if (platform === 'darwin') {
    return path.join(process.env.HOME || '', 'Library/Application Support/opentalent');
  } else {
    return path.join(process.env.HOME || '', '.config/opentalent');
  }
}
```

**Validation**:
```bash
npm test -- config-manager.test.ts  # Tests platform logic
```

---

### D3: Add Settings UI
**Duration**: 1 hour  
**Depends On**: D1, D2  
**Story Points**: 2

**Acceptance Criteria**:
- [ ] Settings load from config
- [ ] Changes save to config
- [ ] Validation applied before saving
- [ ] Component renders correctly

**Files to Create**:
1. `src/renderer/pages/Settings.tsx` - Settings page
2. `src/renderer/pages/Settings.test.tsx` - Tests

**Settings Available**:
- Change model (requires restart)
- Change voice
- Toggle auto-update
- Toggle analytics
- Theme selection

**Validation**:
```bash
npm test -- Settings.test.tsx
```

---

## Task Group E: Binary Management

### E1: Create Binary Resource Structure
**Duration**: 1.5 hours  
**Depends On**: A1  
**Story Points**: 2

**Acceptance Criteria**:
- [ ] Resource directories created correctly
- [ ] Binary paths documented
- [ ] Scripts executable
- [ ] .gitignore excludes binaries

**Files to Create**:
1. `resources/binaries/README.md` - Binary documentation
2. `resources/binaries/.gitkeep` - Directory placeholder
3. `scripts/download-binaries.sh` - Binary download script
4. `src/main/binary-manager.ts` - Binary execution manager
5. `.gitignore` - Exclude binaries from git

**Directory Structure**:
```
resources/binaries/
├── README.md
├── .gitkeep
├── windows/
│   ├── ollama/
│   │   └── ollama.exe
│   └── piper/
│       └── piper.exe
├── darwin/
│   ├── ollama/
│   │   └── ollama
│   └── piper/
│       └── piper
└── linux/
    ├── ollama/
    │   └── ollama
    └── piper/
        └── piper
```

**Validation**:
```bash
ls -la resources/binaries/
# Should show platform directories
```

---

### E2: Implement Binary Verification
**Duration**: 1.5 hours  
**Depends On**: E1  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Checksums verified on app startup
- [ ] Corrupted binaries detected
- [ ] User warned of verification failures
- [ ] 95%+ test coverage

**Files to Create**:
1. `src/main/binary-verifier.ts` - Verification logic
2. `src/main/binary-verifier.test.ts` - Tests
3. `resources/binaries/checksums.json` - Binary checksums

**checksums.json Format**:
```json
{
  "windows": {
    "ollama.exe": "sha256-hash-here",
    "piper.exe": "sha256-hash-here"
  },
  "darwin": {
    "ollama": "sha256-hash-here",
    "piper": "sha256-hash-here"
  },
  "linux": {
    "ollama": "sha256-hash-here",
    "piper": "sha256-hash-here"
  }
}
```

**Verification Logic**:
```typescript
export class BinaryVerifier {
  static async verify(): Promise<VerificationResult> {
    const checksums = loadChecksums();
    const platform = getPlatform();
    
    for (const [filename, expectedHash] of Object.entries(checksums[platform])) {
      const actualHash = await computeHash(filename);
      if (actualHash !== expectedHash) {
        return { valid: false, failedBinary: filename };
      }
    }
    
    return { valid: true };
  }
}
```

**Validation**:
```bash
npm test -- binary-verifier.test.ts
```

---

### E3: Test Binary Execution
**Duration**: 1 hour  
**Depends On**: E2  
**Story Points**: 2

**Acceptance Criteria**:
- [ ] Ollama binary executes on all platforms
- [ ] Piper binary executes on all platforms
- [ ] Error handling works for missing binaries
- [ ] 90%+ test coverage

**Files to Create**:
1. `src/main/__tests__/binary-execution.test.ts` - Integration tests

**Test Cases**:
```typescript
it('should execute ollama binary', async () => {
  const result = await executeBinary('ollama', ['--version']);
  expect(result.exitCode).toBe(0);
});

it('should execute piper binary', async () => {
  const result = await executeBinary('piper', ['--help']);
  expect(result.exitCode).toBe(0);
});

it('should handle missing binary gracefully', async () => {
  const result = await executeBinary('nonexistent', []);
  expect(result.error).toBeDefined();
});
```

**Validation**:
```bash
npm test -- binary-execution.test.ts
```

---

## Task Group F-G: Integration, Testing & Documentation

### F1: Create End-to-End Setup Test
**Duration**: 2 hours  
**Story Points**: 5

**Acceptance Criteria**:
- [ ] All 5 test scenarios pass
- [ ] Setup time measured
- [ ] No memory leaks detected

**Files to Create**:
1. `src/e2e/setup-wizard.e2e.test.ts` - E2E tests

**Test Scenarios**:
1. First launch → complete setup with Granite-2B
2. First launch → select alternative model (Granite-350M)
3. First launch → select large voice (Medium)
4. Second launch → skip wizard, load config
5. Error during download → retry successfully

---

### F2: Performance Profiling
**Duration**: 1.5 hours  
**Story Points**: 3

**Acceptance Criteria**:
- [ ] Startup time <5s (target achieved)
- [ ] Memory <400MB before model load
- [ ] Results logged to `profiling-results.json`

**Files to Create**:
1. `scripts/profile-startup.js` - Profiling script
2. `src/main/__tests__/performance.test.ts` - Performance tests

---

### F3: Cross-Platform Testing
**Duration**: 1.5 hours  
**Story Points**: 3

**Test Platforms**:
- Windows 10+ (x64)
- macOS 11+ (Intel + Apple Silicon)
- Ubuntu 20.04/22.04 LTS

**Manual Test Plan**:
- [ ] App launches successfully
- [ ] Setup wizard completes
- [ ] Hardware detection works
- [ ] Config saves/loads correctly
- [ ] Binary execution verified

---

### G1-G2: Documentation
**Duration**: 2 hours  
**Story Points**: 2

**Files to Create**:
1. `desktop-app/DEVELOPMENT.md` - Dev guide
2. `desktop-app/ARCHITECTURE.md` - Architecture overview
3. `docs/user-guides/getting-started.md` - User guide
4. `docs/user-guides/model-selection.md` - Model selection guide

---

## Progress Tracking

Use this table to track completion:

| Task | Status | Notes |
|------|--------|-------|
| A1 | ⏳ | - |
| A2 | ⏳ | - |
| A3 | ⏳ | - |
| B1 | ⏳ | - |
| B2 | ⏳ | - |
| B3 | ⏳ | - |
| C1 | ⏳ | - |
| C2 | ⏳ | - |
| C3 | ⏳ | - |
| C4 | ⏳ | - |
| C5 | ⏳ | - |
| D1 | ⏳ | - |
| D2 | ⏳ | - |
| D3 | ⏳ | - |
| E1 | ⏳ | - |
| E2 | ⏳ | - |
| E3 | ⏳ | - |
| F1 | ⏳ | - |
| F2 | ⏳ | - |
| F3 | ⏳ | - |
| G1 | ⏳ | - |
| G2 | ⏳ | - |

Update as: ⏳ (Not Started) → 🔄 (In Progress) → ✅ (Complete) → 🐛 (Bug Found)
