# 🖥️ OpenTalent Local AI Architecture

**Last Updated:** December 5, 2025  
**Version:** 1.0  
**Architecture Type:** Desktop-First, Offline-Capable, On-Device AI

---

## 🎯 Core Principle: NO CLOUD DEPENDENCIES

**OpenTalent runs 100% locally on user's hardware.**

- ✅ **No OpenAI API key required**
- ✅ **No internet required** (after initial model download)
- ✅ **No cloud costs** for users
- ✅ **Complete privacy** - data never leaves device
- ✅ **Works on low-end hardware** - 350M model for basic machines
- ✅ **Scales to high-end** - 8B model for powerful machines

---

## 📊 Granite 4 Model Variants

OpenTalent supports **3 model sizes** for different hardware configurations:

| Model | Parameters | RAM Required | Use Case | Speed | Quality |
|-------|-----------|--------------|----------|-------|---------|
| **Granite-350M** | 350 million | 2-4GB RAM | Low-end laptops, older machines | ⚡ Very Fast | ⭐⭐⭐ Good |
| **Granite-2B** | 2 billion | 8-12GB RAM | Mid-range laptops, modern PCs | ⚡ Fast | ⭐⭐⭐⭐ Very Good |
| **Granite-8B** | 8 billion | 16-32GB RAM | High-end workstations, gaming PCs | ⚡ Moderate | ⭐⭐⭐⭐⭐ Excellent |

### Model Selection Strategy

**Automatic Hardware Detection:**
```python
import psutil
import platform

def recommend_model():
    total_ram = psutil.virtual_memory().total / (1024**3)  # GB
    cpu_count = psutil.cpu_count()
    gpu_available = check_gpu()
    
    if total_ram < 6:
        return "granite-350m"  # Low RAM
    elif total_ram < 14:
        return "granite-2b"    # Medium RAM
    else:
        return "granite-8b"    # High RAM
```

**User Override:**
- User can always choose smaller model for faster speed
- User can benchmark models on their hardware
- Settings UI shows RAM usage in real-time

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenTalent Desktop App                       │
│                    (Electron/Tauri + React)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│  Voice       │  │ Conversation │  │  Avatar    │
│  Service     │  │  Service     │  │  Service   │
│  (Local TTS) │  │ (Granite AI) │  │ (Local Rig)│
└──────────────┘  └──────────────┘  └────────────┘
       │                 │                 │
       │                 │                 │
┌──────▼────────────────▼─────────────────▼──────┐
│         Local Model Storage & Cache             │
│  ~/OpenTalent/models/                           │
│    - granite-350m/ (1GB download)               │
│    - granite-2b/ (4GB download)                 │
│    - granite-8b/ (16GB download)                │
│    - piper-tts-small/ (50MB)                    │
│    - piper-tts-large/ (500MB)                   │
└─────────────────────────────────────────────────┘
```

---

## 🧠 Conversation Service (Granite Models)

### Model Integration: Ollama

**Why Ollama:**
- ✅ Easy local model serving
- ✅ Automatic quantization support (4-bit, 8-bit)
- ✅ REST API compatible with OpenAI format
- ✅ Model caching and fast loading
- ✅ GPU acceleration when available

### Installation & Setup

**1. Bundled Ollama Binary:**
```bash
# OpenTalent includes Ollama binary in app bundle
OpenTalent.app/Contents/Resources/ollama

# First run: Auto-install Ollama
./ollama serve &  # Start server in background
./ollama pull granite4:350m  # Download chosen model
```

**2. Model Download on First Launch:**
```typescript
// In Electron main process
async function firstTimeSetup() {
  const userChoice = await showModelSelectionDialog();
  
  switch(userChoice.model) {
    case '350m':
      await downloadModel('granite4:350m', '1.2GB');
      break;
    case '2b':
      await downloadModel('granite4:2b', '4.1GB');
      break;
    case '8b':
      await downloadModel('granite4:8b', '15.8GB');
      break;
  }
  
  await startOllamaServer();
}
```

**3. Conversation API (Compatible with OpenAI):**
```python
# conversation-service/main.py
import requests

OLLAMA_URL = "http://localhost:11434"  # Local Ollama server

def generate_response(prompt: str, model: str = "granite4:2b"):
    response = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 512
        }
    })
    return response.json()['response']
```

### Quantization for Low RAM

**4-bit Quantization (Recommended for 350M/2B):**
- Reduces RAM usage by 75%
- Minimal quality loss
- Example: Granite-2B uses only 2GB RAM instead of 8GB

**8-bit Quantization (Default for 8B):**
- Reduces RAM usage by 50%
- Better quality than 4-bit
- Example: Granite-8B uses only 8GB RAM instead of 16GB

```bash
# Ollama automatically uses quantized models
ollama pull granite4:350m        # 4-bit quantized (~400MB)
ollama pull granite4:2b-q4       # 4-bit quantized (~1.2GB)
ollama pull granite4:2b-q8       # 8-bit quantized (~2.1GB)
ollama pull granite4:8b-q4       # 4-bit quantized (~4.5GB)
```

---

## 🔊 Voice Service (Local TTS)

### Replacement for OpenAI TTS

**Option 1: Piper TTS (Recommended for Low RAM)**
- ✅ **RAM Usage:** 100-500MB
- ✅ **Quality:** Good (not OpenAI-level, but acceptable)
- ✅ **Speed:** Very fast (real-time on CPU)
- ✅ **Voices:** 50+ languages, 200+ voices
- ✅ **Offline:** 100% local
- ✅ **Model Size:** 50MB (small) to 500MB (large)

**Option 2: Coqui TTS (Better Quality, More RAM)**
- ✅ **RAM Usage:** 1-2GB
- ✅ **Quality:** Excellent (near OpenAI quality)
- ✅ **Speed:** Fast (requires GPU for real-time)
- ✅ **Voice Cloning:** Supported (optional feature)
- ✅ **Model Size:** 500MB to 2GB

### Implementation: Piper TTS

**1. Installation:**
```bash
# Bundled with OpenTalent
OpenTalent.app/Contents/Resources/piper

# Models downloaded on demand
~/OpenTalent/tts-models/
  - en_US-lessac-medium.onnx (50MB, default)
  - en_US-libritts-high.onnx (500MB, high quality)
```

**2. TTS API:**
```python
# voice-service/main.py
import subprocess
import tempfile

def text_to_speech(text: str, voice: str = "en_US-lessac-medium"):
    model_path = f"~/OpenTalent/tts-models/{voice}.onnx"
    
    # Generate audio file
    output_file = tempfile.mktemp(suffix=".wav")
    subprocess.run([
        "./piper",
        "--model", model_path,
        "--output_file", output_file
    ], input=text.encode(), check=True)
    
    return output_file  # Return path to audio file
```

**3. Model Selection UI:**
```typescript
// User can choose TTS quality
const ttsModels = [
  { id: 'small', name: 'Fast (50MB)', ram: '100MB', quality: 'Good' },
  { id: 'medium', name: 'Balanced (200MB)', ram: '200MB', quality: 'Very Good' },
  { id: 'large', name: 'Best (500MB)', ram: '500MB', quality: 'Excellent' }
];
```

---

## 👤 Avatar Service (Local Rendering)

### Lightweight Avatar System

**No Cloud APIs - Pure Local Rendering**

**Option 1: Web-based Avatar (Low RAM)**
- Use HTML5 Canvas + WebGL
- Simple 2D avatar with lip-sync
- RAM: 200-500MB
- Works on any hardware

**Option 2: Ready Player Me + Local Rendering**
- Download avatar once
- Render locally with Three.js
- RAM: 500MB-1GB
- Better quality

**Option 3: Custom 3D Avatar (High Quality)**
- Blender-exported models
- Local rendering with GLTF
- Phoneme-based lip sync
- RAM: 1-2GB

### Implementation: Web-based Avatar

```typescript
// avatar-service/renderer.ts
class LocalAvatarRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  
  async renderFrame(phoneme: string, emotion: string) {
    // Draw avatar face
    this.drawFace(emotion);
    
    // Animate mouth based on phoneme
    this.drawMouth(phoneme);
    
    // Return frame as base64 PNG
    return this.canvas.toDataURL();
  }
  
  drawMouth(phoneme: string) {
    // Map phoneme to mouth shape
    const mouthShapes = {
      'A': [/* coordinates */],
      'E': [/* coordinates */],
      'I': [/* coordinates */],
      // ... more phonemes
    };
    
    const shape = mouthShapes[phoneme] || mouthShapes['A'];
    this.ctx.fillStyle = '#ff69b4';
    this.ctx.fillRect(...shape);
  }
}
```

---

## 💾 Model Storage & Caching

### Directory Structure

```
~/OpenTalent/
├── models/
│   ├── granite4-350m/          # 400MB (4-bit quantized)
│   │   ├── model.gguf
│   │   └── config.json
│   ├── granite4-2b/            # 1.2GB (4-bit quantized)
│   │   ├── model.gguf
│   │   └── config.json
│   ├── granite4-8b/            # 4.5GB (4-bit quantized)
│   │   ├── model.gguf
│   │   └── config.json
│   └── piper-tts/
│       ├── en_US-lessac-medium.onnx  # 50MB
│       ├── en_US-lessac-high.onnx    # 200MB
│       └── en_US-libritts-high.onnx  # 500MB
├── cache/
│   ├── conversations/          # Local conversation history
│   ├── audio/                  # TTS audio cache
│   └── avatars/               # Avatar frames cache
└── logs/
    └── app.log
```

### Model Download Manager

```typescript
// In Electron renderer process
class ModelDownloader {
  async downloadModel(modelName: string, size: string) {
    const url = `https://huggingface.co/ibm-granite/${modelName}`;
    
    // Show progress dialog
    const progress = new ProgressBar({
      title: `Downloading ${modelName}`,
      detail: `Size: ${size}`,
      indeterminate: false,
      maxValue: 100
    });
    
    // Download with progress updates
    await downloadFile(url, {
      onProgress: (percent) => progress.setValue(percent)
    });
    
    progress.close();
  }
}
```

---

## ⚙️ Hardware Detection & Recommendations

### System Requirements

**Minimum (350M Model):**
- CPU: 2 cores, 2.0 GHz
- RAM: 4GB
- Storage: 2GB free
- OS: Windows 10, macOS 10.15, Ubuntu 20.04

**Recommended (2B Model):**
- CPU: 4 cores, 2.5 GHz
- RAM: 8GB
- Storage: 8GB free
- GPU: Optional (2GB VRAM)

**Optimal (8B Model):**
- CPU: 8 cores, 3.0 GHz
- RAM: 16GB
- Storage: 20GB free
- GPU: Recommended (6GB VRAM)

### Auto-Detection Code

```python
# desktop-app/hardware_detection.py
import psutil
import platform
import subprocess

def detect_hardware():
    return {
        'os': platform.system(),
        'cpu_cores': psutil.cpu_count(),
        'cpu_freq': psutil.cpu_freq().max,
        'total_ram': psutil.virtual_memory().total / (1024**3),  # GB
        'available_ram': psutil.virtual_memory().available / (1024**3),
        'gpu': detect_gpu(),
        'storage_free': psutil.disk_usage('/').free / (1024**3)
    }

def detect_gpu():
    try:
        # NVIDIA GPU
        output = subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'])
        return {'type': 'nvidia', 'name': output.decode().split(',')[0], 'vram': output.decode().split(',')[1]}
    except:
        return None

def recommend_configuration(hardware):
    ram = hardware['total_ram']
    gpu = hardware['gpu']
    
    # Model recommendation
    if ram < 6:
        model = 'granite-350m'
        tts = 'piper-small'
        avatar = 'web-basic'
    elif ram < 14:
        model = 'granite-2b'
        tts = 'piper-medium'
        avatar = 'web-enhanced'
    else:
        model = 'granite-8b'
        tts = 'piper-large' if not gpu else 'coqui-tts'
        avatar = 'rpm-local' if gpu else 'web-enhanced'
    
    return {
        'conversation_model': model,
        'tts_model': tts,
        'avatar_renderer': avatar,
        'use_gpu': bool(gpu),
        'quantization': '4bit' if ram < 14 else '8bit'
    }
```

---

## 🎨 User Experience: Model Selection

### First-Time Setup Wizard

```typescript
// Step 1: Hardware Detection
showScreen('Detecting your hardware...');
const hardware = await detectHardware();
const recommendation = await recommendConfiguration(hardware);

// Step 2: Show Recommendation
showScreen(`
  Your Hardware:
  - CPU: ${hardware.cpu_cores} cores @ ${hardware.cpu_freq} GHz
  - RAM: ${hardware.total_ram.toFixed(1)} GB
  - GPU: ${hardware.gpu?.name || 'None'}
  
  Recommended Configuration:
  - AI Model: ${recommendation.conversation_model}
  - Voice Quality: ${recommendation.tts_model}
  - Avatar Quality: ${recommendation.avatar_renderer}
  
  Estimated Performance:
  - Response Time: ${estimateResponseTime(recommendation)}
  - RAM Usage: ${estimateRAMUsage(recommendation)}
`);

// Step 3: Allow User Override
const userChoice = await showChoiceDialog({
  options: ['Use Recommended', 'Choose Manually', 'Benchmark Models'],
  recommended: recommendation
});

// Step 4: Download Models
if (userChoice.action === 'Use Recommended') {
  await downloadModels(recommendation);
} else if (userChoice.action === 'Choose Manually') {
  const custom = await showManualSelection();
  await downloadModels(custom);
} else {
  await runBenchmark();
}
```

### Settings UI (After Setup)

```typescript
// User can change models anytime in Settings
const settingsUI = {
  sections: [
    {
      title: 'AI Model',
      options: [
        { id: 'granite-350m', label: 'Fast (350M)', ram: '2GB', speed: '⚡⚡⚡', quality: '⭐⭐⭐' },
        { id: 'granite-2b', label: 'Balanced (2B)', ram: '8GB', speed: '⚡⚡', quality: '⭐⭐⭐⭐' },
        { id: 'granite-8b', label: 'Best (8B)', ram: '16GB', speed: '⚡', quality: '⭐⭐⭐⭐⭐' }
      ]
    },
    {
      title: 'Voice Quality',
      options: [
        { id: 'piper-small', label: 'Fast (50MB)', quality: 'Good' },
        { id: 'piper-medium', label: 'Balanced (200MB)', quality: 'Very Good' },
        { id: 'piper-large', label: 'Best (500MB)', quality: 'Excellent' }
      ]
    },
    {
      title: 'Avatar Quality',
      options: [
        { id: 'web-basic', label: '2D Simple', ram: '200MB' },
        { id: 'web-enhanced', label: '2D Enhanced', ram: '500MB' },
        { id: 'rpm-local', label: '3D Realistic', ram: '1GB', gpu: true }
      ]
    }
  ]
};
```

---

## 🔄 Offline Capability

### What Works Offline

✅ **100% Offline After Initial Setup:**
- AI conversation (Granite models)
- Text-to-speech (Piper TTS)
- Avatar rendering
- Interview recording
- Local data storage

❌ **Requires Internet (Optional):**
- Model downloads (first time only)
- Software updates (user can defer)
- Cloud backup (optional feature)

### Graceful Degradation

```python
def handle_network_failure():
    if not is_internet_available():
        logger.info("Running in offline mode")
        disable_features(['cloud_sync', 'updates', 'analytics'])
        enable_features(['local_storage', 'offline_mode_banner'])
    else:
        logger.info("Online mode - all features available")
        enable_features(['cloud_sync', 'updates'])
```

---

## 📦 Desktop App Architecture

### Technology Stack

**Framework: Electron (Recommended)**
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Bundled Node.js for services
- ✅ Native file system access
- ✅ Easy local model integration
- ✅ Large community and ecosystem

**Alternative: Tauri (Lighter Weight)**
- ✅ 50% smaller binary size
- ✅ Rust backend (better performance)
- ✅ Lower RAM usage
- ❌ Smaller ecosystem

### App Structure

```
OpenTalent-Desktop/
├── src/
│   ├── main/                    # Electron main process
│   │   ├── index.ts            # App entry point
│   │   ├── ollama-manager.ts   # Ollama lifecycle
│   │   ├── model-downloader.ts # Model download manager
│   │   └── hardware-detector.ts
│   ├── renderer/                # React frontend
│   │   ├── components/
│   │   ├── screens/
│   │   └── services/
│   └── services/                # Backend services
│       ├── voice-service/
│       ├── conversation-service/
│       └── avatar-service/
├── resources/                   # Bundled binaries
│   ├── ollama/                 # Ollama binary
│   ├── piper/                  # Piper TTS binary
│   └── models/                 # Small default models
└── package.json
```

### Build & Distribution

```json
{
  "name": "opentalent-desktop",
  "version": "1.0.0",
  "scripts": {
    "dev": "electron-vite dev",
    "build:win": "electron-builder --win",
    "build:mac": "electron-builder --mac",
    "build:linux": "electron-builder --linux"
  },
  "build": {
    "appId": "com.opentalent.desktop",
    "productName": "OpenTalent",
    "files": [
      "dist/**/*",
      "resources/**/*"
    ],
    "extraResources": [
      { "from": "binaries/ollama", "to": "ollama" },
      { "from": "binaries/piper", "to": "piper" }
    ],
    "win": {
      "target": ["nsis", "portable"]
    },
    "mac": {
      "target": ["dmg", "zip"],
      "category": "public.app-category.productivity"
    },
    "linux": {
      "target": ["AppImage", "deb", "rpm"]
    }
  }
}
```

---

## 🚀 Performance Optimization

### Memory Management

**RAM Usage by Configuration:**

| Configuration | Conversation | TTS | Avatar | Total RAM |
|---------------|-------------|-----|--------|-----------|
| **Minimal (350M)** | 2GB | 100MB | 200MB | **2.3GB** |
| **Balanced (2B)** | 8GB | 200MB | 500MB | **8.7GB** |
| **Maximum (8B)** | 16GB | 500MB | 1GB | **17.5GB** |

### Speed Optimizations

**1. Model Caching:**
- Keep model in RAM between conversations
- Preload model on app startup (background)

**2. GPU Acceleration:**
- Use CUDA for NVIDIA GPUs
- Use Metal for macOS (M-series chips)
- Automatic fallback to CPU

**3. Quantization:**
- Default to 4-bit for <12GB RAM
- Use 8-bit for 12-24GB RAM
- Full precision only for 24GB+ RAM

---

## 🔐 Security & Privacy

### Data Privacy Advantages

✅ **No Cloud = Complete Privacy:**
- User data never leaves device
- No API keys to manage
- No usage tracking
- No data retention policies
- GDPR compliant by default

### Local Data Encryption

```python
# All local data encrypted at rest
from cryptography.fernet import Fernet

def encrypt_conversation(data: dict):
    key = get_user_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(json.dumps(data).encode())
    return encrypted

def decrypt_conversation(encrypted: bytes):
    key = get_user_encryption_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted)
    return json.loads(decrypted.decode())
```

---

## 📋 Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Set up Electron project structure
- [ ] Bundle Ollama binary for all platforms
- [ ] Implement hardware detection system
- [ ] Create model download manager with progress UI
- [ ] Implement model recommendation engine

### Phase 2: Conversation Service
- [ ] Integrate Ollama with conversation service
- [ ] Add support for Granite 350M/2B/8B models
- [ ] Implement quantization selection
- [ ] Add GPU acceleration detection
- [ ] Test conversation quality across models

### Phase 3: Voice Service
- [ ] Bundle Piper TTS binary
- [ ] Implement TTS with multiple quality levels
- [ ] Add voice selection UI
- [ ] Test audio quality and latency
- [ ] Add audio caching

### Phase 4: Avatar Service
- [ ] Implement web-based avatar renderer
- [ ] Add phoneme-based lip sync
- [ ] Create avatar customization UI
- [ ] Test rendering performance
- [ ] Add avatar caching

### Phase 5: Desktop App
- [ ] Build first-time setup wizard
- [ ] Create settings UI for model selection
- [ ] Add system tray integration
- [ ] Implement auto-updates
- [ ] Package for Windows/macOS/Linux

### Phase 6: Testing & Optimization
- [ ] Benchmark all model configurations
- [ ] Test on low-end hardware (4GB RAM)
- [ ] Test on high-end hardware (32GB RAM)
- [ ] Optimize memory usage
- [ ] Optimize startup time

---

## 🎯 Success Metrics

**User Experience Goals:**
- ✅ App starts in < 5 seconds
- ✅ Model loads in < 10 seconds (cached)
- ✅ First response in < 2 seconds (350M), < 5 seconds (8B)
- ✅ TTS generates audio in < 1 second
- ✅ Avatar renders at 30 FPS
- ✅ Total RAM usage < 50% of system RAM

**Quality Goals:**
- ✅ Conversation quality acceptable for all models
- ✅ TTS quality comparable to commercial systems
- ✅ Avatar animations smooth and natural
- ✅ No crashes or freezes
- ✅ 100% offline capability (after setup)

---

## 📚 References

**Model Sources:**
- Granite Models: https://huggingface.co/ibm-granite
- Piper TTS: https://github.com/rhasspy/piper
- Ollama: https://ollama.ai

**Technical Docs:**
- Electron: https://www.electronjs.org/docs
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- Piper TTS Usage: https://github.com/rhasspy/piper/blob/master/USAGE.md

---

**Status:** 🏗️ ARCHITECTURE DEFINED - READY FOR IMPLEMENTATION

**Next Steps:**
1. Update AGENTS.md to reflect local AI architecture
2. Create desktop app scaffolding
3. Begin Granite model integration
4. Replace OpenAI TTS references with Piper TTS
