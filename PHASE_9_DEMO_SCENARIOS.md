# Demo Scenarios & Test Cases

**Phase:** 9 - Demo Recording  
**Date:** December 12, 2025  
**Purpose:** Detailed test scenarios for demo recording

---

## Scenario 1: Happy Path (Main Demo Flow)

**Duration:** 4-5 minutes  
**Role:** Software Engineer  
**Model:** Granite-2B  
**Questions:** 5

### Setup Screen
```
Role: Software Engineer
Model: granite4:3b (Granite 4 3B)
Questions: 5
Action: Click "Start Interview"
```

### Expected Behavior
- Loading spinner appears
- Message: "Initializing interview..."
- First question loads within 5 seconds
- No errors in console
- Application remains responsive

---

## Scenario 2: Interview Progression

**Questions to Answer:**

### Question 1: Introduction
```
Prompt: "Tell me about your background as a Software Engineer and your key 
professional experiences."

Sample Response: "I have 7 years of experience as a software engineer, focusing 
on full-stack development with React and Python. I've led teams of 3-5 developers 
and delivered projects serving 100k+ users. My key strengths include problem 
solving, system design, and mentoring junior developers."

Expected Score: 75-85/100
```

### Question 2: Technical Skills
```
Prompt: "Walk me through your experience with distributed systems and handling 
scalability challenges."

Sample Response: "In my last role, I designed a microservices architecture that 
reduced API latency by 40%. We used Docker and Kubernetes for orchestration, 
implemented caching layers with Redis, and optimized database queries. The system 
now handles 10x traffic without issues."

Expected Score: 80-90/100
```

### Question 3: Problem Solving
```
Prompt: "Describe a challenging problem you solved and how you approached it."

Sample Response: "We had a critical memory leak in production affecting 10% of users. 
I used profiling tools to identify the issue was in a third-party library. I 
patched it locally, tested thoroughly, and deployed. This reduced crashes by 95% 
and improved user satisfaction significantly."

Expected Score: 75-85/100
```

### Question 4: Collaboration
```
Prompt: "Tell me about your experience working with cross-functional teams."

Sample Response: "I regularly collaborate with product, design, and QA teams. 
I've found that clear communication is key. I schedule weekly syncs, document 
decisions, and ensure everyone understands the technical roadmap. This has 
improved project delivery time by 20%."

Expected Score: 70-80/100
```

### Question 5: Growth & Learning
```
Prompt: "How do you stay current with technology and continuous improvement?"

Sample Response: "I dedicate time to learning new technologies through online 
courses and reading technical blogs. I also contribute to open-source projects 
to understand different coding patterns. Recently, I learned Rust and applied it 
to optimize our API backend."

Expected Score: 75-85/100
```

### Expected Summary
```
Total Questions: 5
Average Score: 75-85/100
Performance: Good to Excellent
```

---

## Scenario 3: Different Model Demonstration

**For Demo Variation:** Can record multiple models for comparison

### Setup 1: Lightweight Model
```
Role: Product Manager
Model: granite4:350m
Questions: 3
Expected: Faster responses (3-8s), simpler feedback
```

### Setup 2: High-Performance Model
```
Role: Data Analyst
Model: granite4:3b
Questions: 3
Expected: More detailed responses (5-15s), comprehensive feedback
```

---

## Scenario 4: Error Handling Demo (OPTIONAL)

**Use Case:** Show application resilience

### Test 4A: Service Offline Recovery

**Prerequisites:**
- Ollama running
- Application launched
- Mid-interview

**Steps:**
1. Stop Ollama: `killall ollama`
2. User clicks "Submit Response"
3. Observe error message: "OpenTalent service is offline..."
4. Show error with recovery button
5. Start Ollama: `ollama serve`
6. Click "Try Again"
7. Response processes successfully
8. Continue interview

**Expected Outcome:**
- Clear error message appears within 2s
- Error message is user-friendly
- Recovery button is accessible
- Retry succeeds after Ollama restarts

### Test 4B: Invalid Input Handling

**Steps:**
1. At response input field
2. Type minimal response: "OK"
3. Click Submit
4. Observe validation error
5. Update response to be longer (10+ chars)
6. Click Submit
7. Response accepted

**Expected Outcome:**
- Validation error message: "Response should be at least 10 characters"
- Input field highlights error
- User can correct and resubmit
- Valid response processes normally

### Test 4C: Timeout Handling

**Scenario:** Simulate slow response (OPTIONAL, requires network throttling)

**Steps:**
1. Use DevTools to throttle network
2. Submit a response
3. Watch loading spinner
4. Wait for timeout (>60s in DevTools)
5. Observe retry mechanism
6. Remove throttling
7. Retry succeeds

**Expected Outcome:**
- Loading spinner shows progress
- Timeout detected after 60s
- Automatic retry begins
- Success after throttling removed

---

## Scenario 5: UI & Visual Verification

### Screen 1: Setup Screen
- [ ] Title: "Interview Setup" visible
- [ ] Role selector dropdown functional
- [ ] Model selector dropdown with descriptions
- [ ] Questions slider (1-20 range) working
- [ ] "Start Interview" button prominent
- [ ] Responsive layout (no overflow)
- [ ] Colors consistent with design
- [ ] Font sizes readable
- [ ] No console errors

### Screen 2: Interview Screen
- [ ] Question number indicator (e.g., "Question 1 of 5")
- [ ] Question text clearly readable
- [ ] Response input field visible
- [ ] Submit button ready
- [ ] Progress bar showing completion
- [ ] Loading spinner smooth animation
- [ ] Feedback appears with score
- [ ] Next button enabled after submission
- [ ] No layout shifts or jumps

### Screen 3: Summary Screen
- [ ] Interview complete message
- [ ] Total questions shown
- [ ] Average score prominent
- [ ] Question breakdown visible
- [ ] Individual scores displayed
- [ ] Feedback for each question
- [ ] "Start New Interview" button available
- [ ] "Export Results" option (if available)
- [ ] Clean, professional layout

---

## Scenario 6: Performance Benchmarks

**Measure these metrics during demo:**

### Startup Performance
- Application launch: **< 3 seconds** ✓
- First screen render: **< 1 second** ✓
- Interview setup: **< 2 seconds** ✓

### Model Performance
- Model loading: **< 5 seconds** ✓
- First question display: **< 1 second** ✓

### Response Processing
- Short response (50 chars): **5-10 seconds** ✓
- Medium response (200 chars): **8-15 seconds** ✓
- Long response (500 chars): **10-20 seconds** ✓

### UI Responsiveness
- Input field typing: **Instant** ✓
- Button clicks: **< 100ms response** ✓
- Screen transitions: **< 500ms** ✓

---

## Scenario 7: Recording Timing

**Total Demo Duration Target: 5-7 minutes**

```
Scene 1: Launch & Intro       0:00 - 0:30 (30 seconds)
Scene 2: Setup & Config       0:30 - 1:30 (60 seconds)
Scene 3: Interview Workflow   1:30 - 4:30 (180 seconds)
Scene 4: Error Recovery       4:30 - 5:30 (60 seconds) [OPTIONAL]
Scene 5: Summary & Results    5:30 - 6:30 (60 seconds)
Scene 6: Features/Info        6:30 - 7:00 (30 seconds)
                              ─────────────────────────
                              Total:      330 seconds (5.5 minutes)
```

---

## Scenario 8: Voice-Over Integration

**Record voice-over separately or during recording:**

### Timing Map
```
0:00-0:30   "OpenTalent is a desktop AI interview platform..."
0:30-1:30   "Getting started is simple. Select your role..."
1:30-4:30   "During the interview, OpenTalent presents questions..."
4:30-5:30   "OpenTalent is built for reliability..."
5:30-6:30   "After completing the interview, you get a summary..."
6:30-7:00   "OpenTalent works completely offline..."
```

---

## Pre-Recording Validation

Before each recording attempt:

- [ ] Ollama running: `curl http://localhost:11434/api/tags`
- [ ] Models available: `ollama list | grep granite`
- [ ] Application launches: `npm start` in desktop-app directory
- [ ] No console errors on startup
- [ ] All screens render correctly
- [ ] Interview flow works end-to-end
- [ ] Responses process without errors
- [ ] Summary displays correctly
- [ ] Performance meets benchmarks
- [ ] Audio/microphone working

---

## Recording Quality Checklist

During recording:

- [ ] Screen resolution: 1920x1080 or higher
- [ ] Frame rate: 30-60 fps
- [ ] No frame drops or stuttering
- [ ] Mouse cursor visible
- [ ] Mouse movements smooth
- [ ] Audio clear and audible
- [ ] Background noise minimal
- [ ] Lighting adequate
- [ ] No glare on screen
- [ ] File saves successfully
- [ ] Video plays back correctly

---

## Post-Recording Steps

After recording raw footage:

1. [ ] Review entire video
2. [ ] Check for any errors or crashes
3. [ ] Verify audio quality
4. [ ] Note any sections needing retakes
5. [ ] Identify best takes
6. [ ] Plan editing approach
7. [ ] Backup raw footage
8. [ ] Begin editing process

---

## Contingency Plans

### If Demo Crashes
- [ ] Restart application
- [ ] Verify Ollama is running
- [ ] Check for logs in console
- [ ] Re-do affected scene
- [ ] Keep backup footage

### If Audio Is Poor
- [ ] Re-record voice-over with better microphone
- [ ] Use existing good audio and trim silence
- [ ] Consider separate audio recording

### If Video Quality Is Low
- [ ] Check display scaling
- [ ] Increase recording bitrate
- [ ] Use external monitor if available
- [ ] Re-record with better settings

### If Response Processing Is Slow
- [ ] Close other applications
- [ ] Verify Ollama has sufficient RAM
- [ ] Accept slower response and edit (add pauses)
- [ ] Note in editing that this is normal first-response latency

### If Interview Won't Complete
- [ ] Kill and restart application
- [ ] Restart Ollama
- [ ] Check system resources
- [ ] Try with fewer questions (3 instead of 5)
- [ ] Use different model if issues persist

---

## Documentation During Recording

Keep notes as you record:

```
Recording Session: [Date, Time]
Model Used: [granite4:3b]
Questions: [5]
Duration: [5:32]
Issues: [None / describe any issues]
Best Take: [Scene 1: Take 3, Scene 2: Take 1, etc.]
Audio Quality: [Excellent / Good / Fair / Poor]
Video Quality: [Excellent / Good / Fair / Poor]
Next Steps: [Continue to editing / Retakes needed / etc.]
```

---

## Success Metrics

**Video Recording Success:**
- ✅ 5-7 minute duration
- ✅ 1920x1080 resolution
- ✅ 30-60 fps frame rate
- ✅ Clear audio (voice-over and system sound)
- ✅ All 6 scenes included
- ✅ Demonstrates all key features
- ✅ Error handling shown (optional but good)
- ✅ Professional appearance

**Content Success:**
- ✅ Key messages conveyed
- ✅ Features clearly demonstrated
- ✅ Workflow easy to follow
- ✅ Benefits explained
- ✅ "Offline" emphasized
- ✅ "Privacy" emphasized
- ✅ "Professional AI" emphasized
- ✅ Engaging and informative

---

**Test Scenarios Ready:** ✅  
**Target Recording Date:** December 14-15, 2025  
**Status:** Ready for execution

