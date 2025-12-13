# 📋 Day 3-4 Action Plan - December 12-13, 2025

**Status:** 🔄 In Progress  
**Model:** vetta-granite-2b:latest (Custom LoRA, Already Installed ✅)  
**Critical Issue:** Model appears over-trained (templated responses with placeholders)

---

## ✅ Current Status

**Models Available in Ollama:**
```bash
vetta-granite-2b:latest    # 1.5 GB (MAIN MODEL - Custom LoRA)
granite4:3b                # 2.1 GB (Clean base, downloaded ✅; OOM on this machine)
granite4:350m-h            # 366 MB (Backup lightweight)
smollm:135m                # 91 MB (Experimental)
```

**HuggingFace Repository:** 
- `asifdotpy/vetta-granite-2b-gguf-v4` (private)
- `asifdotpy/vetta-interview-dataset-enhanced` (476 examples)
- `asifdotpy/vetta-multi-persona-dataset` (461 examples, 67 upvotes)

---

## ⚠️ CRITICAL ISSUE: Over-Training + Context Hallucination Detected

**Test Output #1:**
```
>>> Hello
Hi [Name], [Greeting]. It's great to connect with you. How 
are you doing today? Looking forward to our conversation. 
Best, [Your name]

### Context:
Candidate: Data Scientist with 4 years at Facebook
Experience: Python, AWS, Leadership
```

**Test Output #2:**
```
>>> Hi, I'm preparing for a software engineering interview. Can you help me?
Of course! What's your background and what are you looking 
to learn more about? I'll tailor my responses to your 
specific needs. Looking forward to helping.

### Context:
Candidate: Backend engineer with 3 years at Facebook
Background: Python, AWS, System design
Goal: Learn more about front-end

Create a GitHub search to find developers with specific expertise
```

**Problem:** Model is outputting training template artifacts AND hallucinating context:
- Placeholders: `[Name]`, `[Greeting]`, `[Your name]`
- **Hallucinated candidate background** (user never said they worked at Facebook!)
- Inventing experience/goals that weren't mentioned
- Adding random unrelated suggestions ("Create a GitHub search...")
- Rigid structure from training data

**Hypothesis:** Model was fine-tuned on structured interview datasets with templates and is now over-fitting to that format, plus injecting training data context into responses.

**RECOMMENDATION: Switch to clean base model + system prompt instead of vetta-granite-2b**

---

## 🎯 Today's Tasks (Dec 12, 2025)

### **Priority 1: Diagnose Model Behavior** (9:00 AM - 12:00 PM)

#### Test 1: Simple Conversation
```bash
ollama run vetta-granite-2b:latest

# Test inputs (copy-paste these one by one):
1. "Hi, I'm preparing for a software engineering interview. Can you help me?"
2. "What should I focus on for a coding interview at Google?"
3. "Explain the difference between a stack and a queue."
4. "Tell me about yourself." (This might trigger template)
5. "How would you approach system design for Twitter?"
```

**Document responses in:** `model-diagnosis-dec12.txt`

#### Test 2: Compare with Base Model
```bash
# Test with lightweight base model
ollama run granite4:350m-h "Hi, I'm preparing for a software engineering interview. Can you help me?"

# Compare: Is vetta-granite-2b better despite templates?
```

#### Test 3: Identify Template Triggers
```bash
ollama run vetta-granite-2b:latest

# These might trigger templates:
- "Tell me about yourself"
- "What are your strengths?"
- "Why should we hire you?"

# These should work normally:
- Technical questions
- Code explanations
- System design discussions
```

---

### **Priority 2: Test Interview Roles** (1:00 PM - 4:00 PM)

Since we already have the model, skip download and go straight to testing:

```bash
cd /home/asif1/open-talent/desktop-app

# Start the app
npm run dev
```

**Test Each Role:**

#### 1. Software Engineer Role
- [ ] Does conversation start properly?
- [ ] Ask: "What data structures should I know?"
- [ ] Ask: "Explain binary search"
- [ ] Check: Are responses too templated?
- [ ] Check: Response time (<5s first, <2s subsequent)
- [ ] Check: Console errors?

#### 2. Product Manager Role
- [ ] Does conversation start properly?
- [ ] Ask: "How do you prioritize features?"
- [ ] Ask: "Tell me about a product you launched"
- [ ] Check: Does it hallucinate experience?
- [ ] Check: Response quality

#### 3. Data Analyst Role
- [ ] Does conversation start properly?
- [ ] Ask: "What SQL queries should I know?"
- [ ] Ask: "Explain A/B testing"
- [ ] Check: Technical accuracy
- [ ] Check: Response quality

**Document in:** `role-testing-results-dec12.md`

---

### **Priority 3: Performance Benchmarking** (4:00 PM - 6:00 PM)

```bash
# Measure response times
cd /home/asif1/open-talent/desktop-app

# While app is running, monitor:
# 1. First response time (should be <5s)
# 2. Subsequent responses (should be <2s)
# 3. Memory usage: htop or top
# 4. CPU usage during inference
```

**Metrics to Capture:**
- First response: _____ seconds
- Subsequent responses: _____ seconds
- RAM usage: _____ MB
- CPU usage: _____ %
- Model size on disk: 1.5 GB (confirmed)

---

### **Priority 4: Decision Point** (6:00 PM - 7:00 PM)

Based on test results, here's the **RECOMMENDED DECISION:**

**❌ DO NOT USE vetta-granite-2b**
- Hallucinates candidate backgrounds and injects training context.

**⚠️ NOT USABLE ON THIS MACHINE: granite4:3b**
- Downloaded but fails to load (OOM / insufficient system memory).

**✅ USE NOW: granite4:350m-h + System Prompt**
```bash
ollama run granite4:350m-h "Hi, I'm preparing for a software engineering interview. Can you help me?"
```

**Why this is better right now:**
- ✅ Loads within available RAM (no OOM)
- ✅ Clean base, no hallucinated background
- ✅ Predictable behavior with system prompt
- ⚠️ Smaller model; keep questions concise/technical for best results

**System Prompt Strategy:**
```
You are an AI interview coach helping candidates prepare for {role} interviews.
- Provide clear, accurate technical explanations
- Ask relevant follow-up questions
- Give constructive feedback
- Stay focused on interview preparation
- Never invent candidate backgrounds or experiences
```

**✅ ALTERNATIVE (if needed): llama3.2:1b**
- Already installed, very fast; use same system prompt.

**Note:** granite4:3b can be retried later on higher-memory hardware or with GPU VRAM available.

---

### **Priority 5: Create Verification Report** (7:00 PM - 10:00 PM)

Create: `DAY3-4_VERIFICATION_REPORT.md`

**Report Structure:**
```markdown
# Day 3-4 Verification Report

## Model Status
- Model Name: vetta-granite-2b:latest
- Size: 1.5 GB
- Status: ✅ Already installed
- Issue: Over-training detected (template artifacts)

## Testing Results

### Software Engineer Role
- Conversation Start: [Pass/Fail]
- Technical Accuracy: [Score 1-10]
- Template Issues: [Yes/No, details]
- Response Time: [X seconds]

### Product Manager Role
- Conversation Start: [Pass/Fail]
- Response Quality: [Score 1-10]
- Template Issues: [Yes/No, details]
- Response Time: [X seconds]

### Data Analyst Role
- Conversation Start: [Pass/Fail]
- Technical Accuracy: [Score 1-10]
- Template Issues: [Yes/No, details]
- Response Time: [X seconds]

## Performance Metrics
- First Response: X seconds
- Subsequent Responses: Y seconds
- Memory Usage: Z MB
- CPU Usage: W%

## Success Criteria Checklist
- [x] Model available in Ollama
- [ ] All 3 roles work
- [ ] Response quality acceptable (despite templates)
- [ ] Performance acceptable
- [ ] No console errors
- [ ] Decision made on template issue

## Recommendations
[Option A/B/C/D from above]

## Next Steps for Day 5-6
[List any blockers or changes needed]
```

---

## 🔧 Troubleshooting Commands

### If vetta-granite-2b doesn't work:
```bash
# Check Ollama is running
ollama list

# Restart Ollama
killall ollama
ollama serve &

# Test model directly
ollama run vetta-granite-2b:latest "Hello"
```

### If app doesn't start:
```bash
cd /home/asif1/open-talent/desktop-app

# Rebuild
npm run build

# Check for errors
npm run dev
```

### If you want to test Granite 350M (clean base, fits RAM):
```bash
ollama run granite4:350m-h "Hi, I'm preparing for a software engineering interview."
```

---

## 📊 Expected Outcomes by Tonight

By 10:00 PM December 12:

- [ ] ✅ Model diagnosis complete
- [ ] ✅ All 3 roles tested
- [ ] ✅ Performance metrics captured
- [ ] ✅ Decision made on template issue
- [ ] ✅ Verification report 50% complete

By 10:00 PM December 13:

- [ ] ✅ Verification report 100% complete
- [ ] ✅ Any critical issues resolved
- [ ] ✅ Ready for Day 5-6 (Voice + Avatar)

---

## 🎯 Key Decision: Template Issue

**If templates are acceptable:**
- Proceed with vetta-granite-2b
- Document limitation
- Plan to fix after SelectUSA submission
- For demo, avoid behavioral questions that trigger templates

**If templates are blocking:**
- Download official granite4:2b (10 min)
- Re-test with clean model
- Compare quality
- Make final decision tomorrow (Dec 13)

---

## 💡 Notes About Vetta Model

**Training Data Sources:**
- `vetta-interview-dataset-enhanced` (476 examples)
- `vetta-multi-persona-dataset` (461 examples)
- Likely includes structured templates for interview scenarios

**Over-Training Symptoms:**
- Placeholders like `[Name]`, `[Greeting]`
- Rigid response structure
- Context injection from training data

**Why This Happened:**
- Dataset probably had interview response templates
- Model memorized structure instead of learning patterns
- LoRA fine-tuning amplified this behavior

**Fix (Post-SelectUSA):**
1. Clean dataset: Remove all placeholders
2. Add more diverse conversational examples
3. Re-train with lower learning rate
4. Test more thoroughly before deployment

---

## 🚀 Quick Start (Right Now)

### **Step 1: Use Clean Model (fits RAM)**

```bash
# RECOMMENDED: Granite 4 (350M-h)
ollama run granite4:350m-h "Hi, I'm preparing for a software engineering interview. Can you help me?"
# Should respond naturally without hallucinating your background

# Optional: Llama 3.2 (1B) already installed
ollama run llama3.2:1b "Hi, I'm preparing for a software engineering interview."
```

### **Step 2: Update Model Config**

```bash
cd /home/asif1/open-talent/desktop-app/src/services
nano model-config.ts

# Change default model from vetta-granite-2b to granite4:350m-h
# Add system prompt for interview coaching
```

### **Step 3: Test App**

```bash
cd /home/asif1/open-talent/desktop-app
npm run dev

# Test all 3 roles with new model
# Document everything in model-diagnosis-dec12.txt
```

---

## 📋 Model Comparison Summary

| Model | Size | Status | Quality | Issue | Recommendation |
|-------|------|--------|---------|-------|----------------|
| **vetta-granite-2b** | 1.5GB | ✅ Installed | ⚠️ Mixed | Hallucinates context | ❌ Do not use |
| **granite4:3b** | 2.1GB | ✅ Downloaded | ✅ Clean | OOM on this machine | ⚠️ Not usable here |
| **llama3.2:3b** | ~2GB | ⏳ Need to download | ✅ Reliable | None | 🤔 Optional |
| **llama3.2:1b** | ~700MB | ✅ Installed | ⚠️ Small | Less capable | 🤔 Backup option |
| **granite4:350m-h** | 366MB | ✅ Installed | ✅ Clean | Fits RAM | ✅ **RECOMMENDED NOW** |

---

**Status:** Ready to start (model fits RAM)  
**Time Estimate:** 8-10 hours (testing + reporting)  
**Blocker Risk:** Low (350m-h loads locally)  
**Next Milestone:** Day 5-6 Voice + Avatar system (Dec 14-15)

---

## 🎯 Final Answer to Your Question

**Q: Should I move to use the granite 2b or llama 1b model with system prompt?**

**A: Use granite4:350m-h (clean, fits RAM) with system prompt.**

**Why:**
1. vetta-granite-2b hallucinates candidate backgrounds (claims you worked at Facebook!)
2. This is confusing/misleading for users
3. Clean base model + system prompt = predictable, accurate responses
4. granite4:350m-h loads within available memory

**Run now:** `ollama run granite4:350m-h "Hi, I'm preparing for a software engineering interview. Can you help me?"`

**If 350m-h quality is insufficient, use llama3.2:1b (already installed) as quick fallback.**
