# OpenTalent: Privacy-First AI Recruitment 🚀

[![Release](https://img.shields.io/badge/release-v1.1.0-brightgreen.svg)](https://github.com/asifdotpy/open-talent-local-ai/releases/tag/v1.1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Local AI](https://img.shields.io/badge/AI-100%25%20Local-orange.svg)](#)
[![Privacy First](https://img.shields.io/badge/Privacy-First-blueviolet.svg)](#)

OpenTalent is a state-of-the-art, desktop-first recruitment platform that leverages **local AI** to find, evaluate, and track technical talent. Featuring the new **TalentScout Pro** interface, it offers a seamless, privacy-first experience where no data leaves your machine.

---

## 🌟 Choose Your Journey

To provide the best experience, we've created specialized guides for different audiences:

| I am a... | Goal | Fast Path |
| :--- | :--- | :--- |
| **Investor/Executive** | See the value & potential | [**Investor Demo Guide**](README_DEMO.md) 🎬 |
| **Recruiter/End User** | Install and start using | [**User Guide (Non-Technical)**](README_USER_GUIDE.md) 👥 |
| **Developer** | Contribute or build | [**Developer Setup Guide**](SETUP_GUIDE.md) 🛠️ |
| **QA/Tester** | Verify system health | [**Testing Guide**](README_TESTING.md) 🧪 |

---

## 🔥 Key Features

- **Local AI Engines**: Powered by Ollama (Granite 4/Mistral) for search and evaluation.
- **Privacy Core**: 100% offline interview processing and candidate enrichment.
- **Unified Gateway**: A high-performance microservices architecture managed through a single entry point.
- **Voice Intelligence**: Local TTS (Piper) and STT for immersive AI-led interviews.
- **Cross-Platform**: Built with Electron & React for a premium desktop experience.

---

## 🚀 Quick Start (Production Environment)

If you have the prerequisites (Node.js 20, Python 3.12, NPM), start the entire platform with a single command:

```bash
# Clone the repository
git clone https://github.com/asifdotpy/open-talent-local-ai.git
cd open-talent

# Bootstrap dependencies
./manage.sh start
```

### Management Commands

Our unified management script handles the entire lifecycle:

- `./manage.sh start` - Start all microservices and the desktop app
- `./manage.sh stop` - Gracefully stop all components
- `./manage.sh status` - Check the health and PIDs of active services
- `./manage.sh restart` - Perform a clean stop-start cycle

---

## 🏛️ Architecture at a Glance

OpenTalent uses a decoupled microservices architecture coordinated via a **Desktop Integration Gateway**:

1. **Frontend**: React-based Electron application.
2. **Gateway**: Unified proxy for all microservices.
3. **Services**:
    - `scout-service`: GitHub/LinkedIn talent sourcing.
    - `voice-service`: Local STT/TTS processing.
    - `analytics-service`: Interview and quality metrics.
    - `desktop-integration-service`: Service discovery and orchestration.

---

## 📜 Documentation Index

- [**AGENTS.md**](AGENTS.md): Detailed agent architecture and capabilities.
- [**CONTRIBUTING.md**](CONTRIBUTING.md): How to help build the future of recruitment.
- [**SECURITY.md**](SECURITY.md): Our commitment to local data processing.
- [**v1.0.0 Walkthrough**](.antigravity/walkthrough.md): Technical details of the latest release.

---

## 🛡️ Security & Privacy

OpenTalent is built on the principle that **hiring data is sensitive**.

- ❌ No cloud API keys required.
- ❌ No telemetry or tracking.
- ❌ No external LLM costs.
- ✅ 100% data ownership.

---

## 📞 Support

- **Bug Reports**: Open an issue on GitHub.
- **General Inquiries**: Please refer to the [AGENTS.md](AGENTS.md) for project history and vision.

---

**Built with ❤️ by the OpenTalent community.**
