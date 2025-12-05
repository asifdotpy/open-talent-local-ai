# AGENTS.MD

> **Last Updated:** December 5, 2025  
> **Architecture:** Desktop-First, Local AI, 100% Offline Capable

## 📋 Quick Navigation

- [Project Overview](#project-overview)
- [Architectural Philosophy](#-architectural-philosophy-no-cloud-dependencies)
- [Local AI Stack](#local-ai-stack)
- [Model Selection](#model-selection-granite-4-variants)
- [Desktop Application](#desktop-application-architecture)
- [Implementation Status](#implementation-status)
- [Getting Started](#getting-started)

## ⚠️ Critical Architecture Change (December 5, 2025)

**OpenTalent has pivoted from cloud-based to 100% local AI:**
- ❌ **REMOVED:** OpenAI API, OpenAI TTS, GCP Infrastructure, Keycloak
- ✅ **ADDED:** Granite 4 Models (350M/2B/8B), Ollama, Piper TTS, Electron Desktop App
- 🎯 **Goal:** Desktop application with NO cloud dependencies, works offline, complete privacy

## Project Overview

**OpenTalent** is a desktop-first, offline-capable AI interview platform that runs 100% locally on user hardware. No API keys, no cloud costs, no data ever leaves your device.

**Core Components:**
- **Desktop App** (Electron/Tauri): Cross-platform (Windows/macOS/Linux)
- **Voice Service** (Piper TTS): Local text-to-speech (50MB-500MB models)
- **Conversation Service** (Granite 4 via Ollama): Local AI conversation (350M/2B/8B models)
- **Avatar Service** (WebGL): Local 3D avatar rendering with lip-sync
- **Interview Service**: Interview orchestration and assessment

## 🎯 Architectural Philosophy: NO CLOUD DEPENDENCIES

**Core Principles:**
1. **Privacy First**: All data processing happens on user's device
2. **Offline Capable**: Works 100% offline after initial model download
3. **Hardware Flexible**: 3 model sizes for different RAM configurations (2GB-32GB)
4. **No API Keys**: No OpenAI, no cloud services, no subscriptions
5. **Open Source**: Community-driven development

**Why Local AI?**
| Benefit | Cloud AI | Local AI (OpenTalent) |
|---------|----------|-----------------------|
| Privacy | ⚠️ Data sent to cloud | ✅ Data never leaves device |
| Cost | 💰 Pay per API call | ✅ Free after model download |
| Offline | ❌ Requires internet | ✅ 100% offline capable |
| Speed | ⚠️ Network latency | ✅ No network overhead |
| Control | ❌ Dependent on API provider | ✅ Full control over models |

## Local AI Stack

**Model Framework:**
- **Ollama** (v0.1.0+): Local model serving platform, OpenAI-compatible API
- **Granite 4 Models**: IBM's open-source conversation models (350M/2B/8B parameters)
- **GGUF Format**: Quantized models for efficient serving
- **4-bit/8-bit Quantization**: RAM reduction (75%/50%)

**Desktop Framework:**
- **Electron** (v28.0.0+): Cross-platform desktop app (Windows/macOS/Linux)
- **React** (v18.0.0+): Frontend UI framework
- **Node.js** (v20.0.0+): Backend services runtime

**Text-to-Speech:**
- **Piper TTS**: Offline neural TTS (100-500MB RAM)
  - Small model: 50MB download, 100MB RAM, Good quality
  - Medium model: 200MB download, 200MB RAM, Very Good quality
  - Large model: 500MB download, 500MB RAM, Excellent quality
- **ONNX Runtime**: Model inference engine

**Avatar Rendering:**
- **Three.js**: 3D rendering library
- **WebGL**: Hardware-accelerated graphics
- **Phoneme Lip-Sync**: Audio-driven mouth animation

## Model Selection: Granite 4 Variants

Users choose between 3 model sizes based on their hardware:

| Model | Parameters | RAM Required | Download Size | Speed | Quality | Use Case |
|-------|-----------|--------------|---------------|-------|---------|----------|
| **Granite-350M** | 350M | 2-4GB | 400MB (4-bit) | ⚡ Very Fast | ⭐⭐⭐ | Low-end laptops (2015+) |
| **Granite-2B** | 2B | 8-12GB | 1.2GB (4-bit) | ⚡ Fast | ⭐⭐⭐⭐ | Mid-range laptops (2018+) |
| **Granite-8B** | 8B | 16-32GB | 4.5GB (4-bit) | ⚡ Moderate | ⭐⭐⭐⭐⭐ | High-end workstations |

**Hardware Detection:**
OpenTalent automatically detects your system's RAM and recommends the optimal model:
- **< 6GB RAM**: Granite-350M (minimal configuration)
- **6-14GB RAM**: Granite-2B (balanced configuration)
- **14GB+ RAM**: Granite-8B (maximum quality)

Users can override the recommendation in settings.

## Desktop Application Architecture

```
OpenTalent Desktop App (Electron)
├── Main Process (Node.js)
│   ├── Ollama Server (bundled binary)
│   ├── Piper TTS (bundled binary)
│   ├── Hardware Detection
│   ├── Model Download Manager
│   └── Service Orchestration
│
├── Renderer Process (React)
│   ├── Interview UI
│   ├── Setup Wizard
│   ├── Settings UI
│   └── Avatar Renderer (Three.js)
│
└── Resources
    ├── Ollama Binary (Windows/macOS/Linux)
    ├── Piper TTS Binary
    └── Default TTS Voice Models
```

**Model Storage Structure:**
```
~/OpenTalent/
├── models/
│   ├── granite4-350m/    (400MB, 4-bit quantized)
│   ├── granite4-2b/      (1.2GB, 4-bit quantized)
│   ├── granite4-8B/      (4.5GB, 4-bit quantized)
│   └── piper-tts/        (50MB-500MB)
│
├── cache/
│   ├── conversations/    (JSON conversation history)
│   ├── audio/           (Generated audio files)
│   └── avatars/         (Avatar state cache)
│
└── logs/
    ├── app.log
    ├── ollama.log
    └── piper.log
```

## Implementation Status

**✅ COMPLETED (Phase 1-3):**
- Project migration to open-talent (46,111 files)
- Documentation organization (9 directories, 13 markdown files)
- Development standards (50+ tools, 15+ pre-commit hooks)
- Local AI architecture specification (LOCAL_AI_ARCHITECTURE.md)

**🔄 IN PROGRESS (Phase 4):**
- Architecture redesign documentation
- Desktop app planning
- Model integration strategy

**📋 PLANNED (Phase 5-10):**
- Phase 5: Electron desktop app setup
- Phase 6: Ollama integration
- Phase 7: Piper TTS integration
- Phase 8: Avatar rendering implementation
- Phase 9: Hardware detection system
- Phase 10: Testing & optimization

## Getting Started

### System Requirements

**Minimum (Granite-350M):**
- OS: Windows 10+, macOS 11+, Ubuntu 20.04+
- RAM: 4GB (2GB for model + 2GB for OS/services)
- Disk: 2GB free space
- CPU: 2 cores, 2GHz+

**Recommended (Granite-2B):**
- OS: Windows 10+, macOS 11+, Ubuntu 20.04+
- RAM: 12GB (8GB for model + 4GB for OS/services)
- Disk: 5GB free space
- CPU: 4 cores, 2.5GHz+
- GPU: Optional (NVIDIA/AMD for acceleration)

**Optimal (Granite-8B):**
- OS: Windows 10+, macOS 11+, Ubuntu 20.04+
- RAM: 24GB (16GB for model + 8GB for OS/services)
- Disk: 10GB free space
- CPU: 8 cores, 3GHz+
- GPU: Recommended (NVIDIA RTX/AMD RX for acceleration)

### Installation (Coming Soon)

**Current Development Status:**
OpenTalent is in active development. Installation instructions will be provided when Phase 5 (Desktop App Setup) is complete.

**Planned Installation Flow:**
1. Download OpenTalent installer for your platform (Windows/macOS/Linux)
2. Run installer (installs Electron app + bundled Ollama/Piper binaries)
3. Launch OpenTalent
4. First-time setup wizard:
   - Hardware detection (auto-detect RAM/CPU/GPU)
   - Model recommendation (350M/2B/8B)
   - Model download (progressive download with progress bar)
   - Voice selection (choose TTS voice quality)
5. Start using OpenTalent (100% offline)

### Development Setup

**For Developers:**
```bash
# Clone repository
git clone https://github.com/asif1/open-talent.git
cd open-talent

# Install dependencies
npm install  # Desktop app dependencies
pip install -r requirements.txt  # Python services

# Start development environment
npm run dev  # Launches Electron with hot reload

# Build for production
npm run build:windows  # Windows installer
npm run build:mac      # macOS .dmg
npm run build:linux    # Linux AppImage
```

See [LOCAL_AI_ARCHITECTURE.md](LOCAL_AI_ARCHITECTURE.md) for detailed implementation guide.

## Directory Structure

```
open-talent/
├── AGENTS.md                      # This file (architecture overview)
├── LOCAL_AI_ARCHITECTURE.md       # Detailed local AI specification
├── CONTRIBUTING.md                # Development standards
├── README.md                      # Project README
│
├── desktop-app/                   # Electron desktop application (PLANNED)
│   ├── src/
│   │   ├── main/                 # Electron main process
│   │   ├── renderer/             # React UI
│   │   └── preload/              # Preload scripts
│   ├── resources/                # Bundled binaries
│   │   ├── ollama/               # Ollama binaries (Win/Mac/Linux)
│   │   └── piper/                # Piper TTS binaries
│   └── package.json
│
├── services/                      # Backend services
│   ├── conversation-service/     # Granite AI conversation
│   ├── voice-service/            # Piper TTS integration
│   ├── avatar-service/           # Local 3D avatar rendering
│   └── interview-service/        # Interview orchestration
│
├── specs/                         # Specifications and documentation
│   ├── architectural-specs/
│   ├── api-contracts/
│   └── requirements/
│
└── docs/                          # User documentation
    ├── user-guides/
    ├── developer-guides/
    └── api-specs/
```

## Memory Usage by Configuration

| Configuration | Conversation | TTS | Avatar | OS/Services | **Total RAM** |
|---------------|-------------|-----|--------|-------------|---------------|
| **Minimal (350M)** | 2GB | 100MB | 200MB | 2GB | **4.3GB** |
| **Balanced (2B)** | 8GB | 200MB | 500MB | 4GB | **12.7GB** |
| **Maximum (8B)** | 16GB | 500MB | 1GB | 8GB | **25.5GB** |

**RAM Recommendation:**
- 4GB total RAM → Use Granite-350M (tight fit, close other apps)
- 8GB total RAM → Use Granite-350M (comfortable)
- 12GB total RAM → Use Granite-2B (comfortable)
- 16GB total RAM → Use Granite-2B (plenty of headroom)
- 24GB+ total RAM → Use Granite-8B (best quality)

## Performance Goals

| Metric | Target | Configuration |
|--------|--------|---------------|
| App Startup | <5s | All configurations |
| First Response | <2s | Granite-350M |
| First Response | <3s | Granite-2B |
| First Response | <5s | Granite-8B |
| Avatar Rendering | 30 FPS | All configurations |
| TTS Generation | <1s per sentence | All configurations |
| Model Switch | <10s | Hot swap between models |

## Security & Privacy

**Privacy Advantages of Local AI:**
- ✅ **No Data Transmission**: All conversations stay on your device
- ✅ **No Cloud Logging**: No conversation history sent to third parties
- ✅ **GDPR Compliant**: Data never leaves EU if you're in EU
- ✅ **No API Keys**: No risk of key leakage or unauthorized usage
- ✅ **Offline Operation**: Works in air-gapped environments

**Data Storage:**
- All conversation data stored locally in `~/OpenTalent/cache/conversations/`
- Optional: Export conversations to encrypted backup
- Optional: Delete all data on uninstall

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development standards, coding guidelines, and contribution workflow.

**Key Development Principles:**
- Test-Driven Development (TDD): Write tests before code
- Frequent commits: Small, atomic commits with conventional commit messages
- Privacy-first: Never add features that send data to cloud
- Hardware-flexible: All features must work on minimum configuration (4GB RAM)

## Roadmap

**Phase 5 (Current - Desktop App Setup):**
- Set up Electron project structure
- Bundle Ollama and Piper binaries
- Implement hardware detection
- Create model download manager
- Build first-time setup wizard

**Phase 6 (Ollama Integration):**
- Integrate Ollama API with conversation service
- Add Granite model support (350M/2B/8B)
- Implement 4-bit/8-bit quantization selection
- Add GPU acceleration (NVIDIA CUDA, AMD ROCm, Apple Metal)
- Test conversation quality across all models

**Phase 7 (Piper TTS Integration):**
- Bundle Piper TTS binary for all platforms
- Implement 3-quality TTS system
- Add voice selection UI
- Test audio quality and latency
- Implement audio caching

**Phase 8 (Avatar Rendering):**
- Implement WebGL-based avatar renderer
- Add phoneme lip-sync
- Create avatar customization UI
- Test rendering performance
- Implement avatar state caching

**Phase 9 (Testing & Optimization):**
- Benchmark all configurations
- Test on low-end hardware (4GB RAM laptop)
- Test on high-end hardware (32GB RAM workstation)
- Optimize memory usage
- Optimize startup time
- Profile and fix performance bottlenecks

**Phase 10 (Community Launch):**
- Release installers for Windows/macOS/Linux
- Publish documentation
- Create demo videos
- Open source release
- Community feedback and iteration

## License

OpenTalent is open source software. License details coming soon.

## Support

**Documentation:**
- [LOCAL_AI_ARCHITECTURE.md](LOCAL_AI_ARCHITECTURE.md): Detailed technical specification
- [CONTRIBUTING.md](CONTRIBUTING.md): Development standards and workflow

**Community:**
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Community support and questions

---

**Built with ❤️ for privacy-conscious developers who believe AI should work for you, not collect data about you.**
