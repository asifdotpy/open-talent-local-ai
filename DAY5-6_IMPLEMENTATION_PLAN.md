# 📋 Day 5-6 Implementation Plan (Dec 14-15, 2025)

**Status:** 🚀 Ready to Start  
**Estimated Hours:** 32 hours (2 full days)  
**Expected Completion:** Dec 15, 11:00 PM UTC  
**Blocking Factor:** Day 3-4 testing must be complete ✅ (VERIFIED)

---

## 🎯 OBJECTIVE

Build a production-ready Voice + Avatar + Testimonial system that allows users to:
1. Record audio testimonials via microphone
2. Transcribe speech to text in real-time
3. Visualize a 3D avatar that lip-syncs to the recorded audio
4. Submit testimonials with structured privacy controls
5. Process testimonials through LLM pipeline (Day 14)

**Dual-Purpose Architecture:**
- Interview Prep System (Days 1-4, refined)
- Testimonial Collection System (Days 5-6, NEW)

---

## 📦 PHASE 0: DEPENDENCIES & SETUP (30 minutes)

### Install New Packages

```bash
cd /home/asif1/open-talent/desktop-app

# Voice/Audio Libraries
npm install wavesurfer.js              # Waveform visualization
npm install @ricky0123/vad-web         # Voice Activity Detection (VAD)
npm install recordrtc                   # Audio recording polyfill

# Avatar/3D Graphics
npm install three @types/three          # 3D rendering engine
npm install gsap                        # Animation library (for lip-sync timing)

# LLM Integration (for local transcription)
npm install @xenova/transformers        # Hugging Face models (Whisper, etc.)

# Storage & Database
npm install better-sqlite3              # Local SQLite for encrypted storage
npm install crypto-js                   # Encryption utilities

# UI Enhancements (optional, nice-to-have)
npm install react-toastify              # Toast notifications
npm install framer-motion               # Smooth animations

# Types
npm install --save-dev @types/recordrtc
```

**Total new packages:** 10  
**Installation time:** ~3 minutes  
**Disk space:** ~150MB

### Verify Ollama Setup

```bash
# Ensure Ollama is running with granite4:350m-h
ollama list | grep granite4:350m-h

# Test API is accessible
curl http://localhost:11434/api/tags
```

---

## 🏗️ PHASE 1: VOICE INPUT SYSTEM (3 hours)

### File: `src/services/voice-input.ts` (~150 lines)

**Responsibilities:**
- Microphone access & permission handling
- Audio capture & recording
- Voice Activity Detection (VAD) - stop recording when user stops speaking
- Local audio file storage (encrypted)
- Waveform data extraction for visualization

**Key Interfaces:**
```typescript
interface VoiceSession {
  sessionId: string;
  isRecording: boolean;
  recordedAudio: Blob;
  waveformData: number[];
  duration: number;
  timestamp: Date;
  encrypted: boolean;
}

interface VoiceInputConfig {
  sampleRate: number;        // 16000 Hz for Whisper
  channelCount: number;      // 1 (mono)
  vadThreshold: number;      // 0-1, when to stop recording
  maxDuration: number;       // 5 minutes max
  autoStopSilence: number;   // ms of silence before auto-stop
}
```

**Key Methods:**
```typescript
class VoiceInputService {
  // Initialize microphone access
  async requestMicrophoneAccess(): Promise<boolean>
  
  // Start recording with VAD
  async startRecording(config: VoiceInputConfig): Promise<VoiceSession>
  
  // Stop recording and return audio blob
  async stopRecording(): Promise<Blob>
  
  // Get real-time waveform data
  getWaveformData(): number[]
  
  // Encrypt and save audio locally
  async saveAudioEncrypted(audio: Blob, sessionId: string): Promise<string>
  
  // Check microphone status
  async checkMicrophoneAccess(): Promise<{ available: boolean; permitted: boolean }>
  
  // Get audio level (0-100) for real-time visualization
  getAudioLevel(): number
}
```

**Implementation Details:**
- Use `MediaRecorder` API for audio capture
- Use `@ricky0123/vad-web` for voice activity detection
- Store encrypted audio in app data directory: `~/.config/opentalent/voice/`
- Use `crypto-js` for AES-256 encryption
- Extract waveform peaks for visual feedback

---

## 🎨 PHASE 2: AVATAR SYSTEM (4 hours)

### File: `src/services/avatar-renderer.ts` (~250 lines)

**Responsibilities:**
- Load & initialize 3D avatar model (Three.js)
- Handle lip-sync animation based on audio phonemes
- Support avatar customization (gender, appearance)
- Render at 30+ FPS with GPU acceleration
- Handle camera/lighting setup

**Key Interfaces:**
```typescript
enum AvatarGender {
  MALE = 'male',
  FEMALE = 'female',
  NEUTRAL = 'neutral'
}

enum AvatarSkinTone {
  LIGHT = 'light',
  MEDIUM = 'medium',
  DARK = 'dark',
  VERY_DARK = 'very_dark'
}

interface AvatarConfig {
  gender: AvatarGender;
  skinTone: AvatarSkinTone;
  name?: string;
  hideIdentity?: boolean; // For privacy - use generic avatar
}

interface AvatarState {
  isInitialized: boolean;
  isAnimating: boolean;
  currentExpression: 'neutral' | 'speaking' | 'listening';
  mouthOpen: number; // 0-1, for lip-sync
}

interface PhonemeFrame {
  time: number;        // ms timestamp
  phoneme: string;     // 'a', 'e', 'i', 'o', 'u', etc.
  intensity: number;   // 0-1, how much mouth should be open
}
```

**Key Methods:**
```typescript
class AvatarRenderer {
  // Initialize Three.js scene with avatar
  async initialize(config: AvatarConfig): Promise<void>
  
  // Load avatar model (could be simple geometric shapes or GLTF model)
  async loadAvatarModel(gender: AvatarGender): Promise<void>
  
  // Play lip-sync animation based on audio
  async playLipSyncAnimation(phonemeFrames: PhonemeFrame[]): Promise<void>
  
  // Update avatar appearance
  updateAppearance(config: AvatarConfig): void
  
  // Change expression (for natural interaction)
  setExpression(expression: 'neutral' | 'speaking' | 'listening'): void
  
  // Render loop
  render(): void
  
  // Cleanup & destroy scene
  dispose(): void
  
  // Get canvas element for React mounting
  getCanvas(): HTMLCanvasElement
  
  // Record avatar animation as video
  async recordAnimation(duration: number): Promise<Blob>
}
```

**Implementation Notes:**
- **Avatar Model:** Start simple with geometric shapes (head, jaw, eyes) for MVP
  - Head: sphere
  - Jaw: box that rotates based on mouth openness
  - Eyes: simple quads with texture
  - Customization: Change sphere color based on skin tone
- **Lip-Sync Phoneme Mapping:**
  - Extract phonemes from audio using Whisper model
  - Map phonemes to mouth shapes (viseme)
  - Animate jaw rotation from 0° (closed) to ~30° (open)
- **Performance:** Target 30 FPS minimum, use requestAnimationFrame
- **Lighting:** Simple 3-point lighting (key light, fill light, back light)
- **Camera:** Fixed angle looking at avatar face

**Phoneme-to-Viseme Mapping:**
```
a, ə, ɑ → 'A' (mouth wide open, jaw down)
e, ɪ → 'E' (mouth slightly open, smile)
i, iː → 'I' (mouth narrow, smile)
o, ɔ → 'O' (mouth round, open)
u, uː → 'U' (mouth round, closed)
```

---

## 📝 PHASE 3: TESTIMONIAL FORM & UI (4 hours)

### File: `src/components/TestimonialForm.tsx` (~280 lines)

**Responsibilities:**
- Multi-step form for testimonial submission
- Privacy controls (anonymity, data sharing)
- Incident type selection (16 violation categories)
- Witness information optional collection
- Form validation & error messages
- Integration with voice input & avatar

**Form Structure (4 Steps):**

**Step 1: Recording (2-3 min)**
- Display audio waveform in real-time
- Show microphone access permission request
- Record button (start/stop)
- Playback of recorded audio
- Option to re-record

**Step 2: Privacy Settings (1 min)**
- Anonymity checkbox ("Record as Anonymous")
- Data sharing opt-in ("Agree to share encrypted with researchers")
- Location precision ("Exact location" vs "City/Region" vs "Country only")
- Witness protection ("Keep witness names private")

**Step 3: Incident Details (2 min)**
- Incident type selector (dropdown with 16 categories)
- Date picker (when did this happen)
- Location field (text input)
- Witness names (optional, text area)
- Additional context (free text, 500 char max)

**Step 4: Review & Submit (1 min)**
- Summary of all data entered
- Confirmation of privacy settings
- Submit button
- View avatar lip-sync playback of recording

**Key Interfaces:**
```typescript
interface TestimonialFormData {
  recordingBlob: Blob;
  recording: {
    duration: number;
    audioUrl: string;
  };
  privacy: {
    anonymous: boolean;
    shareWithResearchers: boolean;
    locationPrecision: 'exact' | 'city' | 'country';
    protectWitnesses: boolean;
  };
  incident: {
    type: ViolationType; // 16 types
    date: Date;
    location: string;
    witnesses: string[];
    context: string;
  };
  metadata: {
    recordedAt: Date;
    audioLanguage: 'en' | 'bn'; // Bengali support
    version: string;
  };
}
```

### File: `src/components/AvatarDisplay.tsx` (~150 lines)

**Responsibilities:**
- Display avatar in React component
- Mount Three.js canvas
- Show avatar customization options
- Display lip-sync playback
- Real-time microphone visualization

**Component Structure:**
```tsx
interface AvatarDisplayProps {
  config?: AvatarConfig;
  onConfigChange?: (config: AvatarConfig) => void;
  recordingSession?: VoiceSession;
  isRecording?: boolean;
  audioLevel?: number; // 0-100 for visualization
}

const AvatarDisplay: React.FC<AvatarDisplayProps> = (props) => {
  // Render canvas for Three.js
  // Show avatar customization dropdown
  // Display waveform visualization
  // Show "Recording..." or "Playback" status
}
```

---

## 🎤 PHASE 4: SPEECH-TO-TEXT TRANSCRIPTION (2.5 hours)

### File: `src/services/transcription-service.ts` (~180 lines)

**Responsibilities:**
- Transcribe audio using Whisper model (local, no cloud)
- Extract phonemes for avatar lip-sync
- Return transcript text & phoneme timing data
- Support multiple languages (English, Bengali)

**Key Interfaces:**
```typescript
interface TranscriptionResult {
  text: string;
  confidence: number;     // 0-1
  language: string;       // 'en', 'bn', etc.
  duration: number;       // seconds
  phonemeFrames: PhonemeFrame[];  // For lip-sync
  timestamps: {
    start: number;
    end: number;
  }[];
}

interface WhisperConfig {
  modelSize: 'tiny' | 'base' | 'small';  // tiny = 39MB, fastest
  language: string;
  taskType: 'transcribe' | 'translate'; // translate to English
}
```

**Key Methods:**
```typescript
class TranscriptionService {
  // Initialize Whisper model (loads from Hugging Face)
  async initialize(config: WhisperConfig): Promise<void>
  
  // Transcribe audio blob to text + phonemes
  async transcribe(audioBlob: Blob): Promise<TranscriptionResult>
  
  // Extract phoneme timing for lip-sync
  async extractPhonemes(audioBlob: Blob): Promise<PhonemeFrame[]>
  
  // Get model download progress
  getDownloadProgress(): number // 0-100
  
  // Clear cached model
  clearCache(): void
}
```

**Implementation Notes:**
- Use `@xenova/transformers` to load Whisper model
- Download to disk on first use (~200MB for 'small' model)
- Cache model in `~/.cache/huggingface/` directory
- For phonemes: Use Whisper's internal token→phoneme mapping
- Fallback: If phoneme extraction fails, use simple rule-based approach

---

## 🔐 PHASE 5: ENCRYPTED STORAGE & DATABASE (1.5 hours)

### File: `src/services/testimonial-database.ts` (~140 lines)

**Responsibilities:**
- Create encrypted SQLite database for testimonials
- Store voice recordings (encrypted blobs)
- Store transcriptions & extracted metadata
- Support full-text search
- Cleanup old recordings

**Database Schema:**
```sql
CREATE TABLE testimonials (
  id TEXT PRIMARY KEY,
  recordedAt DATETIME NOT NULL,
  audioBlob BLOB NOT NULL,              -- Encrypted audio
  transcription TEXT NOT NULL,
  incidentType TEXT NOT NULL,
  incidentDate DATETIME,
  location TEXT,
  anonymousRecord BOOLEAN DEFAULT false,
  shareWithResearchers BOOLEAN DEFAULT false,
  witnessNames TEXT,
  context TEXT,
  privacyMaskApplied BOOLEAN DEFAULT false,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'draft'            -- draft, submitted, processed
);

CREATE TABLE voice_sessions (
  sessionId TEXT PRIMARY KEY,
  userAgent TEXT,
  recordingDuration NUMBER,
  audioPath TEXT,                        -- Encrypted file path
  encryptionKey TEXT,                    -- Key stored separately
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Methods:**
```typescript
class TestimonialDatabase {
  // Initialize encrypted database
  async initialize(): Promise<void>
  
  // Save testimonial with encryption
  async saveTestimonial(data: TestimonialFormData): Promise<string>
  
  // Retrieve testimonial by ID
  async getTestimonial(id: string): Promise<TestimonialFormData>
  
  // List all testimonials (with search)
  async listTestimonials(filter?: SearchFilter): Promise<Testimonial[]>
  
  // Delete testimonial (secure wipe)
  async deleteTestimonial(id: string): Promise<void>
  
  // Export all testimonials (for processing pipeline)
  async exportForProcessing(): Promise<Testimonial[]>
  
  // Get database stats
  getStats(): { totalTestimonials: number; totalSize: number }
}
```

**Encryption Strategy:**
- Use AES-256-GCM for audio blobs
- Keys stored in OS keychain (macOS) / Credential Manager (Windows)
- Each testimonial has unique encryption key
- Database file location: `~/.config/opentalent/db/testimonials.db`

---

## 🔌 PHASE 6: IPC & MAIN PROCESS UPDATES (1 hour)

### Update: `src/main/main.ts`

Add IPC handlers:
```typescript
ipcMain.handle('voice:requestPermission', async () => {
  // Request microphone access
})

ipcMain.handle('voice:startRecording', async (event, config) => {
  // Start voice input service
})

ipcMain.handle('voice:stopRecording', async () => {
  // Stop and return audio blob
})

ipcMain.handle('avatar:initialize', async (event, config) => {
  // Initialize Three.js avatar
})

ipcMain.handle('transcription:transcribe', async (event, audioBlob) => {
  // Transcribe audio
})

ipcMain.handle('testimonial:save', async (event, formData) => {
  // Save to encrypted database
})

ipcMain.handle('testimonial:list', async () => {
  // Retrieve saved testimonials
})
```

---

## 🧪 PHASE 7: INTEGRATION & TESTING (3.5 hours)

### Test Plan

**Unit Tests:**
- Voice input: Check microphone access, recording start/stop
- Avatar: Check initialization, lip-sync animation
- Transcription: Check Whisper model loading & transcription accuracy
- Database: Check encryption/decryption, CRUD operations

**Integration Tests:**
- Record audio → Transcribe → Update avatar lip-sync
- Save testimonial → Retrieve from DB → Verify encryption
- Full form flow: Recording → Privacy → Details → Submit

**UI Tests:**
- Form validation (all fields required)
- Error handling (microphone denied, audio too long, DB save failed)
- Responsiveness (form adapts to different screen sizes)
- Accessibility (keyboard navigation, screen reader support)

**Performance Tests:**
- Avatar renders at 30+ FPS
- Transcription completes within 2x audio duration
- Database queries return in <100ms
- Audio encryption/decryption in <1s

### File: `src/services/__tests__/voice-input.test.ts`
### File: `src/components/__tests__/TestimonialForm.test.tsx`
### File: `src/services/__tests__/transcription.test.ts`

---

## 📝 PHASE 8: DOCUMENTATION & POLISH (1 hour)

### Create:
- **[DAY5-6_IMPLEMENTATION_SUMMARY.md](DAY5-6_IMPLEMENTATION_SUMMARY.md)** - What was built
- **[VOICE_TESTIMONIAL_USER_GUIDE.md](VOICE_TESTIMONIAL_USER_GUIDE.md)** - How to use
- **[DAY5-6_VERIFICATION_REPORT.md](DAY5-6_VERIFICATION_REPORT.md)** - Testing results

### Update:
- `README.md` - Add Voice + Testimonial system section
- `MASTER_TRACKING_DASHBOARD.md` - Mark Day 5-6 complete
- Changelog with new features

---

## 📊 TIMELINE & MILESTONES

| Time | Phase | Task | Duration | Milestone |
|------|-------|------|----------|-----------|
| Dec 14, 9:00 AM | 0 | Install dependencies, verify setup | 30 min | ✅ Ready to code |
| Dec 14, 9:30 AM | 1 | Voice input service | 3 hours | 🎤 Microphone capture working |
| Dec 14, 12:30 PM | 2 | Avatar renderer | 4 hours | 🎨 Avatar rendering on screen |
| Dec 14, 4:30 PM | 3 | Testimonial form + UI | 4 hours | 📝 Form validation working |
| Dec 14, 8:30 PM | 4 | Speech-to-text | 2.5 hours | 📄 Transcription working |
| Dec 15, 12:00 AM | 5 | Encrypted storage | 1.5 hours | 🔐 Database save/load working |
| Dec 15, 1:30 AM | Break | Sleep & recharge | 6 hours | 💤 |
| Dec 15, 7:30 AM | 6 | IPC & main process | 1 hour | 🔌 All services connected |
| Dec 15, 8:30 AM | 7 | Testing & bug fixes | 3.5 hours | 🧪 All tests passing |
| Dec 15, 12:00 PM | 8 | Documentation & polish | 1 hour | 📚 Docs complete |
| Dec 15, 1:00 PM | - | Buffer for issues | 2 hours | 🛡️ Safety margin |
| Dec 15, 3:00 PM | - | Final verification | 1 hour | ✅ Ready for Day 7 demo |
| Dec 15, 11:00 PM | - | **COMPLETION TARGET** | - | 🎉 **SYSTEM READY** |

---

## ✅ SUCCESS CRITERIA

### Functional Requirements
- [ ] Microphone captures audio (16-bit, 16kHz mono)
- [ ] Voice Activity Detection stops recording on silence
- [ ] Avatar renders in 3D and animates smoothly (30+ FPS)
- [ ] Lip-sync matches recorded audio phonemes
- [ ] Speech-to-text transcribes correctly (>90% accuracy for English)
- [ ] Testimonial form validates all required fields
- [ ] Privacy options work (anonymity, data sharing)
- [ ] Encrypted database stores testimonials securely
- [ ] Full form flow works end-to-end

### Non-Functional Requirements
- [ ] No console errors (TypeScript strict mode)
- [ ] Response times acceptable (<2s for transcription)
- [ ] Code follows existing patterns (services, components)
- [ ] All new code has TypeScript types
- [ ] 80%+ test coverage for critical paths
- [ ] Professional UI appearance
- [ ] Responsive design (1080p+ desktop focus)

### Deliverables
- [ ] 5 new service files (voice, avatar, transcription, DB, testimonial)
- [ ] 2 new React components (form, display)
- [ ] 3 test files with unit & integration tests
- [ ] Updated IPC handlers in main process
- [ ] 3 documentation files
- [ ] Zero console errors or warnings
- [ ] Ready for Day 7 demo recording

---

## 🚨 RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Whisper model too large | Medium | High | Use 'tiny' model (39MB) for MVP, upgrade later |
| Avatar rendering slow | Medium | High | Start with geometric shapes, optimize before Day 7 |
| Microphone access denied | Low | Medium | Clear error message, guide user to settings |
| Encryption/decryption bugs | Low | High | Use well-tested libraries (crypto-js), extensive testing |
| Speech recognition inaccurate | Medium | Low | Use larger model (base/small) if tiny doesn't work |
| Database corruption | Low | Medium | Add backup/recovery mechanism, test thoroughly |
| Time overrun | High | High | Prioritize recording+transcription first, avatar second |

---

## 📞 DEPENDENCIES & BLOCKERS

**Requires:**
- ✅ Day 3-4 testing complete (VERIFIED)
- ✅ Ollama running with granite4:350m-h (VERIFIED)
- ✅ Desktop app builds without errors (VERIFIED)

**Blocks:**
- Day 7: Demo video recording (needs working voice+avatar system)
- Day 14: LLM processing pipeline (needs testimonial database)

---

## 🎯 NEXT STEPS (After Day 5-6)

**Immediate (Dec 15 evening):**
1. Record demo video (Day 7, Dec 16)
2. Test all voice+avatar+form features
3. Fix any critical bugs

**Short-term (Week 3):**
1. Build LLM processing pipeline (Day 14)
2. Bihari community outreach (Day 14)
3. Gather actual testimonials (Days 19-20)

**Final push (Week 4):**
1. Complete pitch deck (Days 17-18)
2. Collect community LOIs (Days 19-20)
3. Final submission (Day 21, Dec 31)

---

**Plan Created:** December 12, 2025, 11:45 PM UTC  
**Status:** Ready for implementation 🚀
