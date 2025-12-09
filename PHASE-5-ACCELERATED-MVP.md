# Phase 5: Accelerated MVP Plan (1-2 Weeks)

**Goal**: Working desktop demo showing Granite model selection + setup wizard  
**Timeline**: 7-10 business days  
**Scope**: Minimal viable demo (not full Phase 5)  
**Output**: Executable app for Windows/macOS/Linux

---

## 🎯 MVP Scope (What We're Building)

### Must Have (Demo-Critical)
- ✅ Electron desktop app launches
- ✅ Hardware detection works (shows detected RAM/CPU)
- ✅ Model recommendation engine (recommends 350M/2B/8B)
- ✅ Setup wizard: 3 steps
  1. Hardware display
  2. Model selection
  3. Confirm selection
- ✅ Config saves to disk
- ✅ Working on Windows + macOS (Linux optional for demo)

### Nice to Have (Skip for MVP)
- ❌ Model download (mock the download UI)
- ❌ Voice selection (static choice)
- ❌ TTS integration (audio playback)
- ❌ Binary bundling (reference local binaries)
- ❌ E2E tests (manual testing only)
- ❌ Cross-platform perfect build

---

## 📋 Accelerated Task List (6 Core Tasks)

### Task 1: Electron + React Setup (2 hours)
**Files**:
- `desktop-app/package.json`
- `desktop-app/src/main.ts` (minimal)
- `desktop-app/src/renderer/App.tsx` (hello world)

**Done When**: `npm start` launches app window

---

### Task 2: Hardware Detection (3 hours)
**Files**:
- `desktop-app/src/main/hardware.ts` (detect RAM/CPU)
- `desktop-app/src/renderer/HardwareDisplay.tsx` (show results)

**Done When**: App shows detected RAM + CPU cores

---

### Task 3: Model Recommendation (1.5 hours)
**Files**:
- `desktop-app/src/main/recommender.ts` (simple logic)
- Update HardwareDisplay.tsx to show recommendation

**Done When**: App recommends correct model based on RAM

---

### Task 4: Setup Wizard UI (3 hours)
**Files**:
- `desktop-app/src/renderer/Wizard.tsx` (3-step flow)
- `desktop-app/src/renderer/hooks/useWizard.ts` (state)

**Done When**: Can click through 3 steps, see selection

---

### Task 5: Config Management (1.5 hours)
**Files**:
- `desktop-app/src/main/config.ts` (read/write JSON)

**Done When**: Selection saved to disk, app remembers choice on restart

---

### Task 6: Build for Demo (1 hour)
**Files**:
- `desktop-app/electron-builder.yml` (basic)
- Build scripts (Windows/macOS)

**Done When**: Can create `.exe` and `.dmg` executables

---

## ⏱️ Daily Schedule (Parallel Work)

### Day 1 (2 hours) - Foundation
- Task 1: Electron setup (2h)
- Deliverable: App window launches ✓

### Day 2 (4 hours) - Core Logic
- Task 2: Hardware detection (3h)
- Task 3: Model recommendation (1h)
- Deliverable: App detects RAM and recommends model ✓

### Day 3 (3 hours) - UI Flow
- Task 4: Setup wizard (3h)
- Deliverable: Can select model through UI ✓

### Day 4 (1.5 hours) - Persistence
- Task 5: Config management (1.5h)
- Deliverable: Selection saved between launches ✓

### Day 5 (1 hour) - Packaging
- Task 6: Build executables (1h)
- Deliverable: `.exe` and `.dmg` files ✓

**Total**: 11.5 hours → Spread over 5 days = comfortable pace

---

## 🔧 Simplified Implementation

### Hardware Detection (Task 2)
```typescript
// Simple version (no fancy libraries)
import os from 'os';

function detectHardware() {
  return {
    ramGb: Math.round(os.totalmem() / (1024 ** 3)),
    cpuCores: os.cpus().length,
    platform: process.platform
  };
}
```

### Model Recommendation (Task 3)
```typescript
function recommend(ramGb: number): string {
  if (ramGb < 6) return 'granite-350m';
  if (ramGb < 14) return 'granite-2b';
  return 'granite-8b';
}
```

### Setup Wizard (Task 4)
```typescript
// 3-step React component
// Step 1: Show hardware
// Step 2: Show recommendation + allow override
// Step 3: Confirm selection
// → Save to config.json
```

### Config Management (Task 5)
```typescript
// Read: ~/AppData/opentalent/config.json
// Write: JSON file with { selectedModel: string }
// On startup: Load config, skip wizard if exists
```

---

## 📦 Demo Checklist

When ready to show:

- [ ] App launches in <5 seconds
- [ ] Hardware detection shows correct values
- [ ] Model recommendation is sensible
- [ ] Can click through wizard
- [ ] Selection persists (restart app, selection remembered)
- [ ] Works on Windows AND macOS
- [ ] Executable can be sent to others (self-contained)

---

## 🚀 What This Demo Proves

1. **Technology Stack Works** - Electron + React + local detection
2. **Core Logic Works** - Hardware detection and model selection
3. **UX Flow Works** - Setup wizard is intuitive
4. **Persistence Works** - Data survives restart
5. **Cross-Platform** - Runs on multiple OSs

**For Investors/Employers**: "We have a working desktop app that auto-detects hardware and recommends AI models. This is the foundation for phase 2."

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Build time | 11.5 hours |
| Buildable on | Windows + macOS |
| Hardware detection accuracy | 100% |
| Model recommendation accuracy | 100% |
| Wizard completion rate | 100% (manual test) |
| Config persistence | 100% |
| Demo-ready | Day 5 end |

---

## 🎬 Demo Script (5 minutes)

1. **Launch app** (30 sec)
   - "App launches in under 5 seconds"

2. **Show hardware detection** (60 sec)
   - "Automatically detects RAM and CPU"
   - Point out detected values

3. **Step through wizard** (2 min)
   - "3-step setup: hardware, model selection, confirm"
   - Show model recommendation
   - Allow override

4. **Restart app** (30 sec)
   - "Configuration persists between launches"
   - Show it remembered the selection

5. **Show executable** (30 sec)
   - "Single executable for deployment"
   - Mention Windows/macOS support

---

## 🔒 IP/Git Strategy

**Commit everything with clear timeline**:

```bash
# Day 1
git commit -m "feat: init electron + react project"

# Day 2
git commit -m "feat: hardware detection module"
git commit -m "feat: model recommendation engine"

# Day 3
git commit -m "feat: 3-step setup wizard UI"

# Day 4
git commit -m "feat: config persistence"

# Day 5
git commit -m "build: electron-builder setup"
```

**GitHub timestamps prove**: This work started Dec 6, 2025 (documented in specs)

---

## 📸 After MVP (Week 2)

With working demo:

1. **Get feedback** from beta testers
2. **Record video demo** for pitch deck
3. **Take screenshots** for documentation
4. **Prepare pitch**: "Here's what we built in 1 week"
5. **Consider open sourcing** (or stay private while pitching)

---

## 🎯 Next Steps

Ready to start Task 1 (Electron setup)?

- Confirm: proceed with accelerated MVP
- Or: adjust scope (what's less critical)?
