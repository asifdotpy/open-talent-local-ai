# 📋 Day 3-4 Testing Guide - December 12-13, 2025

**Status:** 🔄 In Progress  
**Model:** granite4:350m-h (366MB, fits RAM)  
**Objective:** Test all 3 interview roles, verify no hallucinations, log metrics

---

## Phase 1: Start the App ✅

```bash
cd /home/asif1/open-talent/desktop-app
npm run dev
```

**Checklist:**
- [ ] localhost:3000 opens
- [ ] "Using: granite4:350m-h" appears on setup screen
- [ ] Ollama shows "Online"
- [ ] No console errors

---

## Phase 2: Test Software Engineer Role

### Setup
1. Click **Software Engineer** button
2. Click **Start Interview**

### Questions Sequence
```
Q1: "What data structures should I know?"
Q2: "Explain binary search."
Q3: "Tell me about yourself" (⚠️ Check for hallucinated background)
```

### Observe & Record
| Metric | Q1 | Q2 | Q3 | Notes |
|--------|-----|-----|-----|-------|
| Response Time | ___ s | ___ s | ___ s | |
| Quality (1-10) | ___ | ___ | ___ | |
| Hallucination? | Y/N | Y/N | Y/N | |
| Console Errors? | Y/N | Y/N | Y/N | |

**Key Observations:**
- First response time: ___ seconds (target <5s)
- Subsequent times: ___ seconds (target <2s)
- Response quality: ___ / 10 (acceptable if ≥7)
- Hallucinations detected: YES / NO
- Template issues: YES / NO

---

## Phase 3: Test Product Manager Role

### Setup
1. Click **Product Manager** button
2. Click **Start Interview**

### Questions Sequence
```
Q1: "How do you prioritize features?"
Q2: "Tell me about a product you launched."
Q3: "What's your background?" (⚠️ Check for hallucinated background)
```

### Observe & Record
| Metric | Q1 | Q2 | Q3 | Notes |
|--------|-----|-----|-----|-------|
| Response Time | ___ s | ___ s | ___ s | |
| Quality (1-10) | ___ | ___ | ___ | |
| Hallucination? | Y/N | Y/N | Y/N | |
| Console Errors? | Y/N | Y/N | Y/N | |

**Key Observations:**
- First response time: ___ seconds (target <5s)
- Subsequent times: ___ seconds (target <2s)
- Response quality: ___ / 10 (acceptable if ≥7)
- Hallucinations detected: YES / NO
- Template issues: YES / NO

---

## Phase 4: Test Data Analyst Role

### Setup
1. Click **Data Analyst** button
2. Click **Start Interview**

### Questions Sequence
```
Q1: "What SQL queries should I know?"
Q2: "Explain A/B testing."
Q3: "Tell me about your experience." (⚠️ Check for hallucinated background)
```

### Observe & Record
| Metric | Q1 | Q2 | Q3 | Notes |
|--------|-----|-----|-----|-------|
| Response Time | ___ s | ___ s | ___ s | |
| Quality (1-10) | ___ | ___ | ___ | |
| Hallucination? | Y/N | Y/N | Y/N | |
| Console Errors? | Y/N | Y/N | Y/N | |

**Key Observations:**
- First response time: ___ seconds (target <5s)
- Subsequent times: ___ seconds (target <2s)
- Response quality: ___ / 10 (acceptable if ≥7)
- Hallucinations detected: YES / NO
- Template issues: YES / NO

---

## Phase 5: Log Results

### Create File 1: `model-diagnosis-dec12.txt`

**Location:** `/home/asif1/open-talent/model-diagnosis-dec12.txt`

**Content Template:**
```
=== MODEL DIAGNOSIS - DEC 12, 2025 ===

MODEL: granite4:350m-h (366MB)
DATE: December 12, 2025
TESTER: Asif

TEST 1: SOFTWARE ENGINEER
- First response time: ___ seconds
- Subsequent response times: ___ seconds
- Response quality (1-10): ___
- Hallucinations: YES / NO
- Console errors: YES / NO
- Notes: [Your observations]

TEST 2: PRODUCT MANAGER
- First response time: ___ seconds
- Subsequent response times: ___ seconds
- Response quality (1-10): ___
- Hallucinations: YES / NO
- Console errors: YES / NO
- Notes: [Your observations]

TEST 3: DATA ANALYST
- First response time: ___ seconds
- Subsequent response times: ___ seconds
- Response quality (1-10): ___
- Hallucinations: YES / NO
- Console errors: YES / NO
- Notes: [Your observations]

OVERALL ASSESSMENT:
- Model fits RAM: YES / NO
- Quality acceptable for demo: YES / NO
- Ready for Day 5-6: YES / NO

RECOMMENDATION: 
[Keep 350m-h / Switch to llama1b / Needs improvement]
```

---

### Create File 2: `DAY3-4_VERIFICATION_REPORT.md`

**Location:** `/home/asif1/open-talent/DAY3-4_VERIFICATION_REPORT.md`

**Content Template:**
```markdown
# Day 3-4 Verification Report
**Date:** December 12-13, 2025  
**Status:** ✅ COMPLETE

## Model Decision
- **Final Model:** granite4:350m-h
- **Reason:** Fits RAM, clean responses, no hallucinations
- **Rejected:** vetta-granite-2b (hallucinations), granite4:3b (OOM)

## Test Results

### Software Engineer Role
- Start: ✅ Pass
- Q1 Response Quality: [Score 1-10]
- Q2 Response Quality: [Score 1-10]
- Hallucinations: [None / Minor / Major]
- Avg Response Time: ___ seconds
- Console Errors: ✅ None

### Product Manager Role
- Start: ✅ Pass
- Q1 Response Quality: [Score 1-10]
- Q2 Response Quality: [Score 1-10]
- Hallucinations: [None / Minor / Major]
- Avg Response Time: ___ seconds
- Console Errors: ✅ None

### Data Analyst Role
- Start: ✅ Pass
- Q1 Response Quality: [Score 1-10]
- Q2 Response Quality: [Score 1-10]
- Hallucinations: [None / Minor / Major]
- Avg Response Time: ___ seconds
- Console Errors: ✅ None

## Performance Metrics
- RAM Usage: ~300-400MB (estimated)
- CPU Usage: Moderate
- First Response Time: ___ seconds (target <5s)
- Subsequent Response Time: ___ seconds (target <2s)
- UI Responsiveness: ✅ Good / ⚠️ Acceptable / ❌ Slow

## Success Criteria Checklist
- [x] Model loads without OOM
- [x] All 3 roles work
- [x] No hallucinated backgrounds
- [x] Response quality acceptable (≥7/10)
- [x] No template artifacts
- [x] Performance acceptable
- [x] No console errors

## Recommendations
✅ **APPROVED** granite4:350m-h for production demo.

### Observations
[Key findings, any issues encountered, notes about model behavior]

### Next Steps
- Day 5-6 (Dec 14-15): Begin Voice + Avatar system development
- Verified baseline: Interview system stable on granite4:350m-h
- Ready to proceed with testimonial voice integration
```

---

## Testing Checklist

- [ ] **Phase 1:** App started with npm run dev
- [ ] **Phase 1:** Shows "Using: granite4:350m-h"
- [ ] **Phase 2:** Tested Software Engineer (3 questions + observations)
- [ ] **Phase 2:** Recorded metrics in table
- [ ] **Phase 3:** Tested Product Manager (3 questions + observations)
- [ ] **Phase 3:** Recorded metrics in table
- [ ] **Phase 4:** Tested Data Analyst (3 questions + observations)
- [ ] **Phase 4:** Recorded metrics in table
- [ ] **Phase 5:** Created model-diagnosis-dec12.txt
- [ ] **Phase 5:** Created DAY3-4_VERIFICATION_REPORT.md
- [ ] **Phase 5:** Both files saved to /home/asif1/open-talent/
- [ ] **Final:** Review both files for completeness

---

## Expected Outcomes

**✅ If all tests pass:**
- granite4:350m-h is stable and clean
- Day 3-4 verification complete
- Ready to move to Day 5-6 (Voice + Avatar)

**⚠️ If issues found:**
- Document in verification report
- Consider fallback to llama3.2:1b
- Adjust Day 5-6 start date if needed

---

## Time Estimate

- **Phase 1:** 2 minutes (start app)
- **Phase 2-4:** 15-20 minutes (3 roles × 3 questions each)
- **Phase 5:** 10 minutes (fill reports)

**Total:** ~30-35 minutes

---

**Start Time:** ___________  
**End Time:** ___________  
**Status:** ⏳ Pending / ✅ Complete

