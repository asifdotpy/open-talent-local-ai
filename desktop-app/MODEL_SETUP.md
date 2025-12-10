# OpenTalent Model Setup Guide

This guide explains how to set up and configure the custom trained models for OpenTalent.

## 📋 Available Models

### Currently Trained & Available

**1. Granite 2B (Main Model)** ✅
- **Model ID:** `vetta-granite-2b-gguf-v4`
- **HuggingFace:** `asifdotpy/vetta-granite-2b-gguf-v4`
- **Format:** GGUF (quantized for Ollama)
- **Size:** ~1.2GB download, 8-12GB RAM required
- **Status:** ✅ Trained and ready to use
- **Dataset:** asifdotpy/vetta-interview-dataset-enhanced
- **Quality:** ⭐⭐⭐⭐⭐ (Expert-level responses)
- **Speed:** ⚡⚡⚡ (Moderate, optimized for quality)

**2. Granite 2B LoRA (Efficient Variant)** ✅
- **Model ID:** `vetta-granite-2b-lora-v4`
- **HuggingFace:** `asifdotpy/vetta-granite-2b-lora-v4`
- **Format:** LoRA adapters + base model
- **Size:** ~500MB download + 800MB base = 1.3GB total, 6-10GB RAM required
- **Status:** ✅ Trained and ready to use
- **Dataset:** asifdotpy/vetta-interview-dataset-enhanced
- **Quality:** ⭐⭐⭐⭐ (Very good, nearly identical to full 2B)
- **Speed:** ⚡⚡⚡⚡ (Slightly faster than full 2B)
- **Use Case:** Lower-memory systems, real-time interview scenarios

**3. Llama 3.2 1B (Fallback)** ✅
- **Model ID:** `llama3.2:1b`
- **Format:** Standard Ollama format
- **Size:** ~600MB download, 2-4GB RAM required
- **Status:** ✅ Pre-installed (comes with Ollama)
- **Quality:** ⭐⭐⭐ (Generic, not interview-optimized)
- **Speed:** ⚡⚡⚡⚡⚡ (Very fast)
- **Use Case:** Fallback if custom models unavailable, testing

### Planned (Not Yet Trained)

**4. Granite 350M (Coming Soon)** 📋
- **Model ID:** `vetta-granite-350m-gguf`
- **HuggingFace:** `asifdotpy/vetta-granite-350m-gguf`
- **Format:** GGUF (once trained)
- **Size:** ~400MB download, 2-4GB RAM required
- **Status:** 📋 Training planned for Dec 14-15 (optional, see SELECTUSA_2026_SPRINT_PLAN.md)
- **Dataset:** asifdotpy/vetta-interview-dataset-enhanced
- **Quality:** ⭐⭐⭐⭐ (Good for lightweight devices)
- **Speed:** ⚡⚡⚡⚡⚡ (Very fast)
- **Use Case:** Ultra-low resource systems, edge deployment

---

## 🚀 Quick Start: Loading Models in Ollama

### Prerequisite: Ollama Installation
```bash
# Verify Ollama is installed and running
ollama --version
ollama serve  # Start Ollama server (runs on localhost:11434)
```

### Option 1: Pull from HuggingFace (Recommended)

Currently, the custom trained models are stored on HuggingFace but not yet available via direct `ollama pull`. Use Option 2 (manual setup) or Option 3 (script-based).

### Option 2: Manual Download & Setup

#### Step 1: Download Model from HuggingFace
```bash
# Create models directory
mkdir -p ~/OpenTalent/models

# Navigate to models directory
cd ~/OpenTalent/models

# Download Granite 2B GGUF
wget https://huggingface.co/asifdotpy/vetta-granite-2b-gguf-v4/resolve/main/model.gguf \
  -O vetta-granite-2b-gguf-v4.gguf

# Or use git-lfs if you have it
git clone https://huggingface.co/asifdotpy/vetta-granite-2b-gguf-v4
cd vetta-granite-2b-gguf-v4
wget https://huggingface.co/asifdotpy/vetta-granite-2b-gguf-v4/resolve/main/model.gguf
```

#### Step 2: Create Modelfile for Ollama
```bash
# Create Modelfile in the same directory
cat > ~/OpenTalent/models/Modelfile << 'EOF'
FROM ./vetta-granite-2b-gguf-v4.gguf
TEMPLATE "[INST] {{ .Prompt }} [/INST]"
PARAMETERS stop [INST] stop [/INST] stop </s>
SYSTEM You are an expert technical interviewer conducting structured interviews for software engineering, product management, and data analyst roles. Ask insightful questions that assess technical knowledge, problem-solving ability, and soft skills. Keep responses professional and constructive.
EOF
```

#### Step 3: Create Model in Ollama
```bash
# Create the model in Ollama
ollama create vetta-granite-2b-gguf-v4 -f ~/OpenTalent/models/Modelfile

# Verify it was created
ollama list | grep vetta-granite-2b
```

### Option 3: Automated Script Setup

```bash
#!/bin/bash
# setup-models.sh - Download and configure custom models

set -e

echo "📦 Setting up OpenTalent models..."

# Create directories
mkdir -p ~/OpenTalent/models
cd ~/OpenTalent/models

# Download Granite 2B GGUF
echo "📥 Downloading Granite 2B GGUF model (~1.2GB)..."
if [ ! -f "vetta-granite-2b-gguf-v4.gguf" ]; then
  wget https://huggingface.co/asifdotpy/vetta-granite-2b-gguf-v4/resolve/main/model.gguf \
    -O vetta-granite-2b-gguf-v4.gguf
else
  echo "   ✅ Model already downloaded"
fi

# Create Modelfile
echo "📝 Creating Modelfile..."
cat > Modelfile << 'EOF'
FROM ./vetta-granite-2b-gguf-v4.gguf
TEMPLATE "[INST] {{ .Prompt }} [/INST]"
PARAMETERS stop [INST] stop [/INST] stop </s>
SYSTEM You are an expert technical interviewer conducting structured interviews. Ask insightful questions that assess knowledge, problem-solving, and soft skills.
EOF

# Create model in Ollama
echo "🚀 Creating model in Ollama..."
ollama create vetta-granite-2b-gguf-v4 -f Modelfile

# Verify
echo "✅ Model setup complete!"
ollama list
```

Run the script:
```bash
chmod +x setup-models.sh
./setup-models.sh
```

---

## 🧪 Testing Models

### Test 1: Check Ollama Status
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags
```

Expected output: JSON list of available models including `vetta-granite-2b-gguf-v4`

### Test 2: Test Interview Flow
```bash
# From desktop-app directory
cd /home/asif1/open-talent/desktop-app

# Run the test script
node test-interview.js
```

Expected output:
- ✅ Ollama status: ONLINE
- ✅ Found models (including vetta-granite-2b-gguf-v4)
- ✅ Interview started successfully
- 📋 First Question from AI Interviewer
- ✅ Response processed successfully
- 🤖 AI Interviewer Response
- ✅ Interview Summary

### Test 3: Launch App and Test UI
```bash
# Compile TypeScript
npm run build-ts

# Start app in development mode
npm run dev

# In the app:
# 1. Select interview role (Software Engineer, Product Manager, Data Analyst)
# 2. Select model (should show Granite 2B as default)
# 3. Click "Start Interview"
# 4. Verify first question appears
# 5. Type a response and submit
# 6. Verify AI provides follow-up question
```

---

## 🎯 Troubleshooting

### Problem: "Model not found" error
**Solution:**
1. Verify Ollama is running: `ollama serve`
2. Check available models: `ollama list`
3. If custom model missing, re-run setup script (Option 3)
4. Check model path: `ls -la ~/OpenTalent/models/`

### Problem: "CUDA not found" (GPU support)
**Solution:**
1. CPU-only mode is fine for single-user interviews
2. For GPU acceleration, install CUDA:
   - NVIDIA: https://ollama.ai/docs/gpu
   - AMD: ROCm support coming soon
3. Ollama will auto-detect GPU if available

### Problem: Out of memory (OOM) error
**Solution:**
1. Check RAM: `free -h`
2. Close other applications
3. Use LoRA variant (vetta-granite-2b-lora-v4) - uses ~30% less memory
4. Use 1B fallback (llama3.2:1b) - uses ~50% less memory
5. Reduce context window in interview-service.ts (line ~80)

### Problem: Interview responses are slow
**Solution:**
1. First response always slower (~3-5s) - normal
2. Subsequent responses cache model in memory (~1-2s)
3. If consistently slow:
   - Check CPU usage: `top` or `Activity Monitor`
   - Close background apps
   - Consider using LoRA variant or 1B model

### Problem: HuggingFace download fails
**Solution:**
1. Check internet connection: `ping huggingface.co`
2. Try alternative download method:
   ```bash
   # Using huggingface-hub CLI
   pip install huggingface-hub
   huggingface-cli download asifdotpy/vetta-granite-2b-gguf-v4
   ```
3. Manual download from browser, then create Modelfile

---

## 📊 Model Selection Guide

Choose your model based on your hardware:

| Your RAM | Recommended Model | Speed | Quality | Use Case |
|----------|------------------|-------|---------|----------|
| 2-4GB | Llama 3.2 1B | ⚡⚡⚡⚡⚡ Very Fast | ⭐⭐⭐ Good | Testing, low-end devices |
| 4-6GB | Llama 3.2 1B | ⚡⚡⚡⚡⚡ Very Fast | ⭐⭐⭐ Good | Student laptops |
| 6-10GB | Granite 2B LoRA | ⚡⚡⚡⚡ Fast | ⭐⭐⭐⭐ Very Good | Budget laptops |
| 8-12GB+ | Granite 2B GGUF | ⚡⚡⚡ Moderate | ⭐⭐⭐⭐⭐ Excellent | Standard laptops |
| 16GB+ | Granite 2B GGUF | ⚡⚡⚡ Moderate | ⭐⭐⭐⭐⭐ Excellent | Workstations |

---

## 🔄 Training Custom Models (Advanced)

See [SELECTUSA_2026_SPRINT_PLAN.md](../SELECTUSA_2026_SPRINT_PLAN.md) under "Optional: Day 5-6 Alternative Track" for instructions on training the 350M variant.

**Quick Reference:**
```bash
# Clone training repository (when available)
git clone https://github.com/asif1/open-talent-training.git
cd open-talent-training

# Install training dependencies
pip install -r requirements-training.txt

# Start training
python train_granite_350m.py \
  --dataset asifdotpy/vetta-interview-dataset-enhanced \
  --output-model vetta-granite-350m-trained \
  --epochs 3

# Convert to GGUF format
python convert_to_gguf.py vetta-granite-350m-trained
```

---

## 📚 Additional Resources

- **Ollama Documentation:** https://ollama.ai/docs
- **IBM Granite Models:** https://huggingface.co/ibm-granite
- **HuggingFace Custom Models:** https://huggingface.co/asifdotpy
- **Interview Datasets:** https://huggingface.co/datasets/asifdotpy
- **Model Training Guide:** [SELECTUSA_2026_SPRINT_PLAN.md](../SELECTUSA_2026_SPRINT_PLAN.md)

---

## 🎉 Next Steps

1. ✅ **Complete Setup:** Run Option 3 (setup-models.sh) script
2. ✅ **Test Models:** Run `node test-interview.js`
3. ✅ **Launch App:** Run `npm run dev`
4. ✅ **Record Demo:** Record 3-5 minute demo showing interview with custom model
5. ✅ **Submit Application:** Include demo in SelectUSA application

---

**Last Updated:** December 10, 2025  
**Status:** Custom 2B model ready, 350M training planned
