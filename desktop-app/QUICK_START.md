# 🚀 OpenTalent MVP - Quick Start Guide

## Prerequisites

✅ **Already Set Up:**
- Ollama installed with `llama3.2:1b` model
- Node.js 20.0.0+
- npm 10.0.0+
- TypeScript compiled to `dist/`

## 🔧 Setup Custom Trained Models

Before running the app, set up your custom trained models:

### Quick Setup (Recommended)

```bash
cd /home/asif1/open-talent/desktop-app

# Run interactive setup script
./setup-models.sh

# Or specify which model to download
./setup-models.sh 2b         # Download Granite 2B only
./setup-models.sh 1b         # Download Llama 1B only
./setup-models.sh all        # Download all models (default)
```

The script will:
- ✅ Download Granite 2B from HuggingFace (~1.2GB)
- ✅ Create Ollama Modelfile
- ✅ Register model in Ollama
- ✅ List available models
- ✅ Optionally test the model

### Manual Setup

If the script doesn't work, see [MODEL_SETUP.md](./MODEL_SETUP.md) for manual download instructions.

---

## Quick Test (Before Full App)

### 1. Verify Ollama is Running

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Expected response: { "models": [...] }
# Should include: vetta-granite-2b-gguf-v4 and llama3.2:1b
```

### 2. Run Interview Service Test

```bash
cd /home/asif1/open-talent/desktop-app
npm run test
```

Or manually:

```bash
node test-interview.js
```

This will:
- ✅ Verify Ollama connection
- ✅ Auto-select best available model (Granite 2B if available, else Llama 1B)
- ✅ Start a 5-question interview
- ✅ Send a sample response
- ✅ Display AI's follow-up question
- ✅ Show interview summary

**Output:** ~180 seconds (3 minutes) for full test with Granite 2B

**Performance Notes:**
- **Granite 2B first response:** 3-5 seconds (model loading into memory)
- **Subsequent responses:** 1-2 seconds
- **Llama 1B:** ~2-3 seconds per response (faster but lower quality)

---

## Launch Full Electron App

### Option 1: Development Mode (Hot Reload)

```bash
cd /home/asif1/open-talent/desktop-app
npm run dev
```

This starts:
- React dev server on `http://localhost:3000`
- Electron app with dev tools
- Hot reload on file changes

**Expected startup time:** 30-60 seconds

### Option 2: Production Build

```bash
cd /home/asif1/open-talent/desktop-app
npm run build
npm start
```

---

## Using the App

### Step 1: Select Interview Role

Choose from:
- **Software Engineer** - 5 technical questions
- **Product Manager** - 5 product strategy questions  
- **Data Analyst** - 5 data analysis questions

### Step 2: Start Interview

Click **"Start Interview"** button

App will:
1. Connect to Ollama
2. Load the selected role's interview prompt
3. Generate first question (30-45 seconds)
4. Display greeting and first question

### Step 3: Respond to Questions

1. Type your response in the text area
2. Press **Send Response** button (or Shift+Enter)
3. Wait for AI's follow-up question (30-45 seconds)
4. Repeat until 5 questions are answered

### Step 4: Interview Complete

When all questions are answered:
- Interview automatically ends
- Summary screen shows:
  - Role and model used
  - Questions asked
  - Responses recorded
  - Full conversation history
- **"Start New Interview"** button to begin again

---

## Troubleshooting

### ❌ "Ollama is Offline"

**Problem:** App shows Ollama offline indicator

**Solution:**
```bash
# Start Ollama service
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

### ❌ "No models found"

**Problem:** App says no models available

**Solution:**
```bash
# Pull llama3.2:1b model (1.3GB download)
ollama pull llama3.2:1b

# Verify model loaded
ollama list
```

### ❌ App Crashes on Start

**Problem:** Electron window doesn't open

**Solution:**
```bash
# Clear TypeScript cache and rebuild
cd /home/asif1/open-talent/desktop-app
rm -rf dist/
npm run build-ts

# Try again
npm run dev
```

### ❌ Slow Response Time (>60 seconds)

**Problem:** AI responses taking too long

**Note:** This is normal for llama3.2:1b on CPU-only systems. The model will process faster on:
- Systems with GPU (NVIDIA CUDA, AMD ROCm)
- More CPU cores (8+ cores recommended)
- More RAM (12GB+ available)

**Workaround:** Model responses will stabilize after first query

### ❌ High Memory Usage

**Problem:** System running slow or out of memory

**Solution:**
Close other applications to free RAM for:
- Ollama model: ~1.3GB
- Electron app: ~300MB  
- OS/services: ~1-2GB
- **Total needed:** ~3GB minimum

---

## File Structure for Development

```
desktop-app/
├── src/
│   ├── services/
│   │   ├── interview-service.ts       ← Interview logic
│   │   └── ollama-service.js          ← Ollama API client
│   ├── renderer/
│   │   ├── InterviewApp.tsx           ← Main UI component
│   │   └── InterviewApp.css           ← UI styling
│   ├── main/
│   │   └── main.ts                    ← Electron main process
│   └── index.tsx                      ← React entry point
├── dist/                               ← Compiled TypeScript
├── package.json                        ← Dependencies
├── tsconfig.json                       ← TypeScript config
└── test-interview.js                  ← Test script
```

---

## Making Changes

### Edit UI (InterviewApp.tsx)

```bash
# File changes auto-reload in dev mode
src/renderer/InterviewApp.tsx

# Restart browser with Cmd+R or F5
```

### Edit Interview Logic (interview-service.ts)

```bash
# Compile TypeScript
cd /home/asif1/open-talent/desktop-app
npm run build-ts

# Restart Electron
Cmd+R or F5 in app
```

### Edit Styling (InterviewApp.css)

```bash
# Changes auto-reload in dev mode
src/renderer/InterviewApp.css

# Refresh browser with Cmd+R or F5
```

---

## Environment Variables

Create `.env` file in `desktop-app/` directory:

```bash
# Custom Ollama server URL (default: http://localhost:11434)
REACT_APP_OLLAMA_URL=http://localhost:11434

# Development mode (automatically set by npm run dev)
REACT_APP_ENV=development
```

---

## Performance Tips

### For Faster Response Time

1. **Use GPU Acceleration**
   ```bash
   # For NVIDIA GPUs
   ollama serve --gpu all
   
   # For AMD GPUs
   ollama serve --gpu amd
   ```

2. **Reduce Context Window**
   Edit `interview-service.ts` to use fewer previous messages

3. **Use Smaller Model** (if available)
   ```bash
   ollama pull mistral:7b-q4
   # Then select in UI
   ```

### For Lower Memory Usage

1. **Close Background Apps**
2. **Disable Dev Tools**
   - Edit `main.ts`, comment out: `mainWindow.webContents.openDevTools()`
3. **Run Production Build**
   ```bash
   npm run build-electron
   ```

---

## Next Steps

### To Add New Interview Roles

1. Edit `src/services/interview-service.ts`
2. Add new role in `getInterviewPrompt()` method
3. Add button in `src/renderer/InterviewApp.tsx`

### To Integrate Piper TTS

1. Install Piper: `pip install piper-tts`
2. Create `audio-service.ts` 
3. Call from `InterviewApp.tsx` to play AI responses

### To Add Assessment Scoring

1. Create `assessment-service.ts`
2. Analyze responses with LLM
3. Display score on summary screen

---

## Support & Resources

- **Ollama Docs:** https://ollama.ai/docs
- **Electron Docs:** https://www.electronjs.org/docs
- **React Docs:** https://react.dev
- **TypeScript Docs:** https://www.typescriptlang.org

---

## Demo Recording Tips

When recording demo video:

1. **Clear Desktop:** Remove clutter
2. **Full Screen:** Run app in full-window mode
3. **Good Lighting:** Ensure screen is visible
4. **No Distractions:** Close notifications, messages
5. **Prepare Script:** Write 3-5 minute narrative
6. **Record Smooth:** Use OBS Studio or screen recording tool
7. **Edit Video:** Add captions, background music, transitions

**Recommended:** Record demo by Dec 16 to allow time for refinement

---

**Ready to code! 🎉**

For questions or issues:
1. Check this guide
2. Review `DAY1_COMPLETE.md` for technical details
3. Run `node test-interview.js` to verify setup
