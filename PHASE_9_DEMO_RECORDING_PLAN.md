# Phase 9 - Demo Recording Plan

**Phase:** 9 - Demo Recording  
**Start Date:** December 12, 2025  
**Target Completion:** December 16, 2025 (4 days)  
**Duration Target:** 5-7 minute demo video  
**Status:** IN PROGRESS

---

## 🎬 Demo Overview

OpenTalent is a desktop-first AI interview platform that runs 100% locally with:
- **Local AI Models:** Granite 4 (350M/2B/8B parameters)
- **Offline-First:** No cloud dependencies, works completely offline
- **Professional UI:** Polished error handling, loading states, and responsive design
- **Production Ready:** 96/96 tests passing, comprehensive error recovery

---

## Demo Script (5-7 minutes)

### Scene 1: Application Launch (30 seconds)

**Narrative:** "OpenTalent is a desktop AI interview platform that runs entirely on your machine. No cloud, no API keys, complete privacy."

**Actions:**
1. Launch application from desktop
2. Show setup screen with role selector
3. Highlight model selection dropdown
4. Show system specs (RAM, CPU) if visible

**Key Points:**
- Application starts within 3 seconds
- Clean, modern UI
- Role options: Software Engineer, Product Manager, Data Analyst
- Available models displayed

**Recording Tips:**
- Start from desktop view
- Slow down mouse movements for clarity
- Pause 2 seconds on each screen

---

### Scene 2: Setup & Configuration (1 minute)

**Narrative:** "Setting up an interview is simple. Select your role, choose an AI model, and decide how many questions you want."

**Actions:**
1. Select role: "Software Engineer"
2. Show model selector dropdown
   - Highlight Granite-2B (recommended)
   - Show size/parameter info
3. Select number of questions: 5
4. Click "Start Interview"
5. Show "Starting interview..." loading spinner

**Key Points:**
- Role selection is intuitive
- Model information is clear (parameters, RAM requirement)
- Questions slider 1-20 range
- Loading spinner shows progress

**Recording Tips:**
- Pause 1 second on dropdown to show options
- Highlight the help text under each field
- Show the loading animation complete cycle

---

### Scene 3: Interview Session (2-3 minutes)

**Narrative:** "During the interview, OpenTalent presents questions one at a time. You can read them on screen or listen with text-to-speech."

**Actions:**

**Question 1:**
1. Show question display
2. Read question aloud or show it on screen
3. Speak answer into microphone or type response
4. Submit response
5. Show AI feedback and score

**Question 2-3:**
1. Show rapid-fire through 2-3 more questions
2. Demonstrate different types of questions
3. Show varying response lengths
4. Highlight score progression

**Key Points:**
- Questions are clear and professional
- Feedback is immediate and constructive
- Scores are displayed (0-100)
- Avatar animates to questions (if implemented)
- Loading spinner shows AI is thinking

**Recording Tips:**
- Use pre-recorded responses for consistency
- Pause after "Show AI feedback" to let it display
- Show score incrementing
- Highlight progress indicator (Question 2 of 5)

---

### Scene 4: Error Recovery (1 minute) - OPTIONAL BUT RECOMMENDED

**Narrative:** "OpenTalent handles errors gracefully. If the service goes offline, it automatically retries. If there's invalid input, it guides you."

**Actions:**

**Scenario 1: Service Unavailable (then recover)**
1. If Ollama is running, temporarily stop it
2. Show "Service offline" error message
3. Show error message with recovery button
4. Restart Ollama
5. Click "Try Again"
6. Show successful recovery

**Scenario 2: Invalid Input**
1. Try submitting empty response
2. Show validation error: "Response must be at least 10 characters"
3. Provide valid response
4. Show successful submission

**Key Points:**
- Error messages are clear and actionable
- Automatic retry happens (no user action needed)
- User can manually retry if needed
- Validation prevents bad data

**Recording Tips:**
- This demo scene requires service manipulation
- If too complex, can skip and just mention "Error handling"
- Show the error message clearly
- Show the recovery button

---

### Scene 5: Interview Summary (1 minute)

**Narrative:** "After completing the interview, you get a comprehensive summary with detailed feedback and recommendations."

**Actions:**
1. Complete the interview (or show pre-recorded summary)
2. Show summary screen with:
   - Total questions: 5
   - Average score: 75/100
   - Performance breakdown
3. Show detailed feedback for each question
4. Show "Save Interview" button
5. Optionally show "Start New Interview" to restart

**Key Points:**
- Summary is comprehensive
- Feedback is constructive
- Scores show performance progression
- Data is saved locally (no cloud)
- Option to start new interview

**Recording Tips:**
- Pause on summary screen for 3-5 seconds
- Read some feedback aloud for emphasis
- Highlight the local data storage message

---

### Scene 6: Application Features (30 seconds)

**Narrative:** "OpenTalent works offline, supports multiple hardware configurations, and gives you complete control over your data."

**Actions:**
1. Open settings/about screen
2. Show model information
3. Show system requirements
4. Highlight "100% offline" messaging

**Key Points:**
- Works without internet
- No data sent to cloud
- Supports Windows, macOS, Linux
- Models available: 350M (2GB), 2B (8GB), 8B (16GB)
- Can switch models anytime

**Recording Tips:**
- Keep this scene brief
- Focus on the "offline" and "privacy" messaging
- Show system specs if relevant

---

## 📋 Pre-Recording Checklist

### Environment Setup
- [ ] Ollama installed and running (`ollama serve`)
- [ ] Granite-2B model downloaded (`ollama pull granite2b`)
- [ ] Application built (`npm run build` if needed)
- [ ] Application tested (launch and verify all screens work)
- [ ] Microphone working or audio responses prepared
- [ ] Screen recording software installed (OBS, ScreenFlow, etc.)

### Test Data Preparation
- [ ] Interview responses written in advance (for consistency)
- [ ] Expected scores known (~70-80 range)
- [ ] Summary data prepared (can use real or synthetic data)
- [ ] Error scenarios scripted (what to demonstrate)

### Recording Setup
- [ ] Screen resolution: 1920x1080 recommended
- [ ] Font size: Readable at 1080p (not too small)
- [ ] Mouse cursor: Visible and clearly shown
- [ ] Audio: Quiet environment, good microphone
- [ ] Lighting: Well-lit for any webcam shots

---

## 🎥 Recording Technical Specifications

### Video Quality
- **Resolution:** 1920x1080 (1080p) or 1440p
- **Frame Rate:** 30fps minimum, 60fps recommended
- **Codec:** H.264 (mp4) or WebM
- **Bitrate:** 5-8 Mbps for clear screen recording

### Audio Quality
- **Sample Rate:** 44.1 kHz or 48 kHz
- **Bitrate:** 128-192 kbps
- **Channels:** Stereo (2 channels)
- **Microphone:** Headset microphone for voice-over

### File Format
- **Container:** MP4 (H.264 video + AAC audio)
- **Duration:** 5-7 minutes
- **File Size:** ~300-500 MB

---

## 🎤 Voice-Over Script

**Total Duration:** ~5-6 minutes

```
[Scene 1: 30 seconds]
"OpenTalent is a desktop AI interview platform that brings professional AI 
interviews directly to your computer. Everything runs locally—no cloud, no API 
keys, no data sent anywhere. Your interviews stay private, on your machine."

[Scene 2: 60 seconds]
"Getting started is simple. Select your interview role—Software Engineer, Product 
Manager, or Data Analyst. Then choose your preferred AI model. OpenTalent supports 
three model sizes optimized for different hardware: the lightweight 350M model for 
computers with limited RAM, the balanced 2B model for most laptops, and the 
high-performance 8B model for workstations."

"Next, select how many interview questions you'd like to answer, from 1 to 20. 
Then click Start Interview. OpenTalent loads your selected model and begins the 
interview session."

[Scene 3: 180 seconds]
"During the interview, OpenTalent presents professional interview questions one 
at a time. Each question is clearly displayed and can be read or listened to. 
You have time to think and provide a thoughtful response."

"OpenTalent evaluates your response using advanced AI, providing immediate feedback 
and a score from 0 to 100. It considers the depth of your answer, technical accuracy, 
and communication clarity. After each question, you get detailed feedback highlighting 
your strengths and areas for improvement."

"The interview progresses through all your selected questions, with OpenTalent 
adapting follow-up questions based on your responses. The entire process is 
smooth, professional, and designed to showcase your best skills."

[Scene 4: 60 seconds - Optional, can skip]
"OpenTalent is built for reliability. If your internet connection drops or Ollama 
goes offline, the system detects this and automatically retries. You'll see clear 
error messages if something goes wrong, with a recovery button to try again. 
Input validation ensures that all your responses are properly formatted before 
being evaluated."

[Scene 5: 60 seconds]
"After completing the interview, you get a comprehensive summary. You'll see your 
overall performance score, a breakdown of how you performed on each question, and 
detailed feedback with actionable recommendations. All of this data stays on your 
computer—nothing is stored in the cloud."

[Scene 6: 30 seconds]
"OpenTalent works completely offline after the initial setup. You can use it 
anywhere, anytime—at home, on a plane, in a coffee shop. Supported on Windows, 
macOS, and Linux, with models optimized for your specific hardware."

"Ready to ace your interviews? Let's get started with OpenTalent."
```

---

## 📹 Recording Workflow

### Step 1: Prepare (30 minutes)
1. Test application end-to-end
2. Prepare interview responses
3. Set up recording environment
4. Test microphone and audio levels
5. Check screen resolution and scaling

### Step 2: Record Full Demo (20-30 minutes)
- Do one full run-through (dry run)
- Record actual demo
- Record voice-over separately or together
- Have backup takes ready

### Step 3: Edit (1-2 hours)
1. Trim intro/outro
2. Remove any long pauses or mistakes
3. Add captions/subtitles (optional)
4. Adjust audio levels
5. Add opening/closing slides
6. Export in target format (MP4, 1080p)

### Step 4: Review (15 minutes)
1. Watch full video
2. Check for clarity
3. Verify audio is clear
4. Confirm all features are visible
5. Check timing (target 5-7 minutes)

---

## 🎯 Demo Goals & Key Messages

### Primary Goals
1. **Show it works offline** - Demo the app without internet
2. **Demonstrate AI quality** - Show thoughtful feedback and scoring
3. **Highlight error recovery** - Show resilience and user guidance
4. **Emphasize privacy** - Mention data stays local throughout

### Key Messages
- ✅ "100% offline—no cloud dependencies"
- ✅ "Professional AI interviews on your computer"
- ✅ "Works on Windows, macOS, and Linux"
- ✅ "Immediate feedback and comprehensive scoring"
- ✅ "Complete privacy—your data never leaves your device"
- ✅ "Optimized for different hardware configurations"
- ✅ "Built-in error recovery and validation"

### Success Criteria
- [x] Application launches cleanly
- [x] All 3 screens render correctly
- [x] Interview workflow completes successfully
- [x] Scores are displayed with feedback
- [x] Error handling is demonstrated (optional)
- [x] Voice-over is clear and engaging
- [x] Video is properly formatted and edited
- [x] Total duration is 5-7 minutes

---

## 🛠️ Tools & Software Needed

### Recording Tools
- **OBS Studio** (free, cross-platform) - Recommended
- **ScreenFlow** (macOS)
- **Camtasia** (Windows/macOS)
- **ShareX** (Windows)

### Editing Tools
- **DaVinci Resolve** (free)
- **Adobe Premiere Pro**
- **Final Cut Pro**
- **iMovie** (macOS, basic)
- **Windows Media Editor** (Windows, basic)

### Voice Recording
- **Audacity** (free)
- **GarageBand** (macOS)
- **Adobe Audition**

---

## 📊 Timeline

| Phase | Task | Duration | Date |
|-------|------|----------|------|
| **Prep** | Environment setup, test application | 30 min | Dec 12-13 |
| **Record** | Record demo video (full scenes) | 30 min | Dec 13-14 |
| **Voiceover** | Record or add voice-over track | 30 min | Dec 14 |
| **Edit** | Edit video, add captions, adjust audio | 2 hours | Dec 14-15 |
| **Review** | Final review and quality check | 30 min | Dec 15 |
| **Finalize** | Export final version and backup | 15 min | Dec 16 |

---

## 📁 Deliverables

### Final Demo Video
- **File:** `opentalent-demo.mp4`
- **Duration:** 5-7 minutes
- **Resolution:** 1920x1080 or higher
- **Format:** H.264 MP4
- **Location:** `/demo/` directory

### Supporting Materials
- **Voice-over script:** `demo-script.md`
- **Recording checklist:** `recording-checklist.md`
- **Editing notes:** `editing-notes.md`

### Backup Assets
- **Raw footage:** Uncut recording
- **Audio track:** Voice-over separately
- **Screenshots:** Key frames from demo

---

## Next Steps

1. ✅ **Prepare environment** (verify Ollama, test app)
2. **Create demo recording checklist** (detailed steps)
3. **Record full demo** (5-7 minute video)
4. **Record voice-over** (narration track)
5. **Edit demo video** (trim, add captions, finalize)
6. **Final review** (quality check, timing)
7. **Export and backup** (save final version)

---

**Phase 9 Status:** 📝 Planning Complete → Ready for Recording  
**Target Completion:** December 16, 2025  
**Estimated Effort:** 5-7 hours total (prep, record, edit, review)

---

For more details, see [PHASE_8_COMPLETION_SUMMARY.md](./PHASE_8_COMPLETION_SUMMARY.md) and [PROGRESS.md](./PROGRESS.md).
