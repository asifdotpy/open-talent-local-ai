# ⚡ Quick Commands Reference

## Essential Commands

### Test Interview Service (Fastest)
```bash
cd /home/asif1/open-talent/desktop-app
node test-interview.js
```
✅ Tests everything works without launching full app  
⏱️ Time: ~3 minutes

### Launch Full Electron App
```bash
cd /home/asif1/open-talent/desktop-app
npm run dev
```
✅ Opens React UI + Electron window with hot reload  
⏱️ Time: ~60 seconds to load

### Compile TypeScript
```bash
cd /home/asif1/open-talent/desktop-app
npm run build-ts
```
✅ Compiles .ts files to dist/  
⏱️ Time: <5 seconds

### Build for Production
```bash
cd /home/asif1/open-talent/desktop-app
npm run build-electron
```
✅ Creates installers in release/  
⏱️ Time: ~2 minutes

---

## Ollama Commands

### Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```
✅ Shows all loaded models  
Expected response: `{"models": [{"name": "llama3.2:1b", ...}]}`

### Start Ollama Service
```bash
ollama serve
```
✅ Starts Ollama server on port 11434  
Leave running in background

### Stop Ollama
```bash
pkill -f "ollama serve"
```
✅ Cleanly stops Ollama

### List Models
```bash
ollama list
```
✅ Shows all downloaded models

### Pull New Model
```bash
ollama pull llama3.2:1b
```
✅ Downloads model (1.3GB)

### Pull Alternative Model (Smaller)
```bash
ollama pull mistral:7b-q4
```
✅ Mistral model, faster responses (~500MB)

---

## Development Commands

### Install Dependencies
```bash
cd /home/asif1/open-talent/desktop-app
npm install --legacy-peer-deps
```

### Run Tests
```bash
npm test
```

### Build React App Only
```bash
npm run build
```

### Clean Build
```bash
rm -rf dist/ node_modules/
npm install --legacy-peer-deps
npm run build-ts
```

---

## File Navigation

### Go to Desktop App
```bash
cd /home/asif1/open-talent/desktop-app
```

### Open Files in Editor
```bash
# Interview Service
code src/services/interview-service.ts

# UI Component
code src/renderer/InterviewApp.tsx

# Styling
code src/renderer/InterviewApp.css
```

### View Documentation
```bash
# Quick start
code QUICK_START.md

# Day 1 Summary
code ../../DAY1_SUMMARY.md

# Full Sprint Plan
code ../../SELECTUSA_2026_SPRINT_PLAN.md
```

---

## Debugging

### Check Ollama Logs
```bash
tail -f /tmp/ollama.log
```

### View Electron Dev Tools
```
Press: Cmd+Option+I (Mac) or Ctrl+Shift+I (Linux)
```

### Force Reload App
```
Press: Cmd+R (Mac) or Ctrl+R (Linux)
```

### Clear React Cache
```bash
cd /home/asif1/open-talent/desktop-app
rm -rf node_modules/.cache
npm start
```

---

## Git Commands (If Using Version Control)

### Check Status
```bash
cd /home/asif1/open-talent
git status
```

### Commit Changes
```bash
git add .
git commit -m "Add interview service and UI"
```

### View Logs
```bash
git log --oneline
```

---

## Performance Tuning

### Monitor Memory Usage
```bash
# Watch Ollama memory
watch -n 1 free -h

# Watch Process
htop
```

### Optimize Model Loading
```bash
# Run with GPU (if NVIDIA)
OLLAMA_CUDA_VISIBLE_DEVICES=0 ollama serve
```

### Speed Up Responses
```bash
# Reduce token generation (edit interview-service.ts)
# Lower max_tokens parameter in API calls
```

---

## File Structure Quick Reference

```
/home/asif1/open-talent/
├── desktop-app/                 ← Main app folder
│   ├── src/
│   │   ├── services/
│   │   │   └── interview-service.ts  ← AI logic
│   │   ├── renderer/
│   │   │   ├── InterviewApp.tsx      ← Main UI
│   │   │   └── InterviewApp.css      ← Styling
│   │   └── index.tsx                ← Entry point
│   ├── dist/                        ← Compiled code
│   ├── package.json                 ← Dependencies
│   ├── QUICK_START.md              ← How to run
│   └── test-interview.js           ← Test script
│
├── DAY1_SUMMARY.md                 ← Today's recap
├── DAY1_COMPLETE.md               ← Technical details
├── SELECTUSA_2026_SPRINT_PLAN.md  ← Full 21-day plan
└── SPRINT_PROGRESS.md             ← Progress tracker
```

---

## Common Issues & Fixes

### "Ollama is offline"
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Verify it's running
curl http://localhost:11434/api/tags
```

### "Port 11434 already in use"
```bash
# Kill existing Ollama process
pkill -9 ollama

# Then restart
ollama serve
```

### "Module not found" errors
```bash
# Rebuild TypeScript
cd /home/asif1/open-talent/desktop-app
npm run build-ts

# Restart app
npm run dev
```

### "React app won't load"
```bash
# Clear cache and reinstall
rm -rf node_modules/ dist/
npm install --legacy-peer-deps
npm run build-ts
npm run dev
```

---

## One-Line Quick Starters

### Quick Test
```bash
cd /home/asif1/open-talent/desktop-app && node test-interview.js
```

### Quick App
```bash
cd /home/asif1/open-talent/desktop-app && npm run dev
```

### Quick Build
```bash
cd /home/asif1/open-talent/desktop-app && npm run build-ts && npm run build
```

### Quick Rebuild
```bash
cd /home/asif1/open-talent/desktop-app && rm -rf dist && npm run build-ts
```

---

## Documentation Files

| File | Purpose | Time to Read |
|------|---------|-------------|
| QUICK_START.md | How to run everything | 5 min |
| DAY1_SUMMARY.md | Next steps for application | 10 min |
| DAY1_COMPLETE.md | Technical implementation details | 15 min |
| SELECTUSA_2026_SPRINT_PLAN.md | Full 21-day roadmap | 30 min |
| SPRINT_PROGRESS.md | Current progress tracking | 5 min |

---

## Keyboard Shortcuts

### In Electron App
| Action | Mac | Linux |
|--------|-----|-------|
| Developer Tools | Cmd+Option+I | Ctrl+Shift+I |
| Reload | Cmd+R | Ctrl+R |
| Hard Reload | Cmd+Shift+R | Ctrl+Shift+R |
| Quit | Cmd+Q | Ctrl+Q |

### In Terminal
| Action | Shortcut |
|--------|----------|
| Stop Process | Ctrl+C |
| Background | Ctrl+Z then `bg` |
| Foreground | `fg` |
| Clear Screen | Ctrl+L |

---

**Saved:** December 10, 2025  
**Purpose:** Quick reference for all commands needed this sprint  
**Keep Handy:** Bookmark this for fast access!
