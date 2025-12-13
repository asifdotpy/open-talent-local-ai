# Pre-Recording Checklist

**Phase:** 9 - Demo Recording  
**Date:** December 12, 2025  
**Status:** Preparation Phase

---

## ✅ Environment Verification Checklist

### System & Application Setup

- [ ] **Ollama Installation**
  ```bash
  which ollama
  ollama --version
  ```
  Expected: Ollama installed and version displayed

- [ ] **Ollama Service Running**
  ```bash
  curl http://localhost:11434/api/tags
  ```
  Expected: JSON response with available models

- [ ] **Granite-2B Model Available**
  ```bash
  ollama list | grep granite
  ```
  Expected: granite2b listed with ~2.0GB size

- [ ] **Application Build**
  ```bash
  cd /home/asif1/open-talent/desktop-app
  npm run build
  ```
  Expected: Build completes with exit code 0

- [ ] **Application Launch**
  ```bash
  npm start
  # Or directly run the built app
  ```
  Expected: Application window opens within 3 seconds

### Application Testing

- [ ] **Setup Screen Renders**
  - Role dropdown visible
  - Model selector visible
  - Questions slider visible
  - Start Interview button visible

- [ ] **Role Selection**
  - Can select "Software Engineer"
  - Can select "Product Manager"
  - Can select "Data Analyst"

- [ ] **Model Selection**
  - Dropdown shows available models
  - Granite-2B is available
  - Can select each model
  - Model info (size, parameters) displayed

- [ ] **Questions Selection**
  - Slider works (1-20 range)
  - Can select 5 questions
  - Display shows selected count

- [ ] **Interview Start**
  - Click "Start Interview" succeeds
  - Loading spinner appears
  - First question loads within 5 seconds
  - Question text is clear and readable

- [ ] **Interview Screen**
  - Question displayed clearly
  - Question text is readable
  - Response input field visible
  - Submit button ready
  - Question progress indicator (1 of 5) visible

- [ ] **Interview Submission**
  - Can enter response (10+ characters)
  - Can submit response
  - Loading spinner shows during processing
  - Feedback appears after processing
  - Score displayed (0-100)
  - Next question button appears

- [ ] **Question Progression**
  - Can proceed through multiple questions
  - Progress indicator updates (2 of 5, 3 of 5, etc.)
  - Responses are accepted
  - Feedback is generated

- [ ] **Interview Completion**
  - All questions can be answered
  - Final submission succeeds
  - Summary screen appears
  - Summary shows average score
  - Summary shows question breakdown

- [ ] **Summary Screen**
  - Total questions shown
  - Average score displayed
  - Question-by-question feedback visible
  - Scores for each question shown
  - "Start New Interview" button available

---

## 🎤 Audio & Microphone Setup

- [ ] **Microphone Testing**
  - System recognizes microphone
  - Microphone input levels visible
  - Can record test audio

- [ ] **Audio Levels**
  - Input level not too loud (no clipping)
  - Input level not too quiet (audible)
  - Background noise minimal

- [ ] **Microphone Permissions** (if needed)
  - Application has microphone permission
  - No "permission denied" errors
  - Audio input working in application

- [ ] **Audio Output**
  - Speakers/headphones working
  - Volume levels appropriate
  - No audio distortion

---

## 🎥 Screen Recording Setup

### Recording Software
- [ ] **OBS Studio** (recommended)
  - Installed and launched
  - Version 29.0+ recommended
  - Settings configured

- [ ] **Recording Settings**
  - Resolution: 1920x1080 (1080p)
  - Frame rate: 60fps preferred
  - Encoder: H.264
  - Bitrate: 5000-8000 kbps

- [ ] **Audio Settings**
  - Microphone input selected
  - Audio bitrate: 128 kbps
  - Audio sample rate: 48 kHz

- [ ] **Display Scaling**
  - Content readable at 1080p
  - Font sizes appropriate
  - UI elements not too small
  - Mouse cursor visible

- [ ] **Test Recording**
  - Record 30-second test
  - Check video quality
  - Check audio quality
  - Verify file saves properly

### Screen Resolution
- [ ] **Application Window**
  - Application scaled to 1920x1080 or larger
  - No blurriness
  - Text readable
  - UI elements clearly visible

- [ ] **Mouse Cursor**
  - Cursor visible during recording
  - Cursor movements smooth
  - Cursor easy to follow

---

## 📝 Script & Content Preparation

- [ ] **Voice-over Script Ready**
  - Script written and reviewed (see PHASE_9_DEMO_RECORDING_PLAN.md)
  - Script duration matches demo (5-7 minutes)
  - Key points included

- [ ] **Interview Responses Prepared**
  - Response 1: Software Engineer question
  - Response 2: Technical follow-up
  - Response 3: Problem-solving
  - Response 4: Communication
  - Response 5: Final question
  - All responses 10+ characters

- [ ] **Expected Results**
  - Question 1: Expected score ~70-80
  - Question 2: Expected score ~75-85
  - Question 3: Expected score ~75-85
  - Question 4: Expected score ~70-80
  - Question 5: Expected score ~75-85
  - Average score: ~75-80

- [ ] **Error Scenarios (Optional)**
  - Know how to stop Ollama (demonstrate service offline)
  - Know how to restart Ollama (demonstrate recovery)
  - Know invalid input examples (demonstrate validation)

---

## 🔧 Technical Testing

### Performance Verification
- [ ] **Application Startup**
  - Launch to interactive: < 3 seconds
  - No errors in console
  - No TypeScript warnings

- [ ] **Model Loading**
  - Granite-2B loads: < 5 seconds
  - No memory errors
  - No timeout errors

- [ ] **Response Processing**
  - Response processing: 5-15 seconds
  - No timeout errors
  - Feedback generated successfully

- [ ] **Memory Usage**
  - Not exceeding 80% of total RAM
  - No memory leaks visible
  - Process stable throughout demo

- [ ] **CPU Usage**
  - Not sustained > 90% CPU
  - Responsive to user input
  - No lag visible

### Network/Connectivity (Offline Test)
- [ ] **Offline Operation**
  - Application works without internet
  - Ollama communicates on localhost
  - No cloud calls made
  - No API errors for offline operation

- [ ] **Offline Mode Verification**
  - Complete interview without internet
  - All features work offline
  - No connectivity required

---

## 📋 File Organization

- [ ] **Demo Directory Created**
  ```bash
  mkdir -p /home/asif1/open-talent/demo
  ```

- [ ] **File Locations**
  - Raw video: `/demo/raw/opentalent-demo-raw.mp4`
  - Voice-over: `/demo/audio/voiceover.wav`
  - Final video: `/demo/opentalent-demo-final.mp4`
  - Script: `/demo/demo-script.md`
  - Checklist: `/demo/recording-checklist.md`

- [ ] **Backup Storage**
  - External drive or cloud backup
  - Backup includes raw footage
  - Backup includes source files
  - Backup location documented

---

## 🎬 Recording Day Preparation

### 1 Hour Before Recording

- [ ] **Fresh Application Start**
  - Kill all processes
  - Start fresh: `npm start`
  - Verify everything loads

- [ ] **Environment Cleanup**
  - Close unnecessary applications
  - Silence notifications
  - Close browser tabs
  - Minimize background processes

- [ ] **Audio Setup**
  - Test microphone one more time
  - Set audio levels
  - Do sound check
  - Record 10-second test

- [ ] **Recording Setup**
  - Start OBS/recording software
  - Load project/settings
  - Do test recording
  - Verify output quality

- [ ] **Mental Preparation**
  - Review script
  - Mentally rehearse demo
  - Have water nearby
  - Stretch and relax

### During Recording

- [ ] **Start Fresh**
  - Restart application
  - Clear any cache
  - Load first scene
  - Take deep breath

- [ ] **Record Workflow**
  - Record each scene sequentially
  - Pause between scenes
  - Review immediately after
  - Do retakes if needed

- [ ] **Quality Checks**
  - Screen clearly visible
  - Audio clear and audible
  - Movements smooth
  - No errors or crashes
  - Content matches script

- [ ] **Backup Recording**
  - Save raw footage immediately
  - Create second copy
  - Verify file integrity

---

## 🎯 Pre-Recording Day-By-Day Timeline

### Friday, Dec 12 (Today)
- [ ] Create demo plan (DONE)
- [ ] Create this checklist (DONE)
- [ ] Verify Ollama running
- [ ] Test application end-to-end
- [ ] Prepare interview responses

### Saturday, Dec 13
- [ ] Final environment testing
- [ ] Recording software setup
- [ ] Audio equipment testing
- [ ] Test recording (5 min)
- [ ] Review test recording quality

### Sunday, Dec 14 (Recording Day)
- [ ] Final system checks (morning)
- [ ] Record demo (afternoon)
- [ ] Record voice-over (evening)
- [ ] Initial review

### Monday, Dec 15 (Editing Day)
- [ ] Edit raw footage
- [ ] Add voice-over
- [ ] Color correction if needed
- [ ] Add titles/captions (optional)
- [ ] Final review

### Tuesday, Dec 16 (Final Delivery)
- [ ] Export final video
- [ ] Quality verification
- [ ] Create backup copies
- [ ] Documentation complete
- [ ] Ready for presentation

---

## ✨ Success Criteria

### Technical
- [x] All application screens render correctly
- [x] All interactions work smoothly
- [x] No crashes or errors
- [x] Performance meets targets (< 5s first response)
- [x] 96 tests passing

### Recording Quality
- [ ] Video resolution: 1920x1080 or higher
- [ ] Video duration: 5-7 minutes
- [ ] Audio clarity: Excellent (no background noise)
- [ ] Mouse movements: Smooth and visible
- [ ] Video smoothness: 30-60 fps
- [ ] Lighting: Bright, no glare or shadows

### Content Quality
- [ ] All 6 demo scenes included
- [ ] Voice-over clear and engaging
- [ ] Script points covered
- [ ] Key messages emphasized
- [ ] Demo flow logical and smooth
- [ ] Information easy to follow

### Final Deliverables
- [ ] Main demo video (MP4, 1080p, 5-7 min)
- [ ] Backup raw footage
- [ ] Voice-over track (WAV)
- [ ] Demo script
- [ ] Recording notes
- [ ] All files backed up

---

## 📞 Support & Troubleshooting

### Common Issues & Fixes

**Issue: Ollama won't start**
```bash
# Check if running
ps aux | grep ollama

# Start service
ollama serve

# Check status
curl http://localhost:11434/api/tags
```

**Issue: Model not found**
```bash
# List models
ollama list

# Download if needed
ollama pull granite2b

# Verify
ollama list | grep granite2b
```

**Issue: Application won't start**
```bash
cd /home/asif1/open-talent/desktop-app
npm install
npm run build
npm start
```

**Issue: Audio not recording**
- Check microphone permissions
- Test with system audio settings
- Try different input device
- Restart recording software

**Issue: Video quality is poor**
- Check resolution setting (1920x1080)
- Check encoder bitrate (5000+ kbps)
- Ensure good display scaling
- Test on different monitor if possible

---

## 📋 Final Sign-Off

- [ ] All environment checks passed
- [ ] Application tested and working
- [ ] Recording equipment ready
- [ ] Script prepared and reviewed
- [ ] Interview responses ready
- [ ] Timeline understood
- [ ] Success criteria clear
- [ ] Ready to proceed with recording

---

**Date Prepared:** December 12, 2025  
**Status:** ✅ Checklist Complete - Ready for Recording Phase  
**Next Step:** Execute recording (Dec 14-15)

