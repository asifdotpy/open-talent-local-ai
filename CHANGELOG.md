# Changelog

All notable changes to the **OpenTalent** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-mvp] - 2025-12-27

### Added
- **Local AI Engine**: Integrated Ollama with Granite 4 models (350M, 2B, 8B) for 100% offline processing.
- **Microservices Architecture**: 11 containerized services for sourcing, interviewing, and analytics.
- **Multimodal Sourcing**: Support for LinkedIn, GitHub, Stack Overflow, and X-Ray search (1.8B profiles).
- **Privacy-First Dashboard**: Local data storage with zero cloud dependencies.
- **3D Avatar**: Real-time phoneme-driven lip-sync using Three.js.
- **Local TTS**: Integrated Piper TTS for high-quality, offline voice generation.
- **Security Workflows**: Automated CodeQL, Semgrep, and Trivy scanning.
- **Product Showcase**: New public landing page deployed to Vercel.

### Changed
- Standardized project branding to **OpenTalent**.
- Refactored interview analytics for better performance and insight depth.

### Fixed
- Resolved cross-platform path resolution issues in Vercel deployment scripts.
- Fixed dependency vulnerabilities in `avatar-service` and `dashboard`.

---

[1.0.0-mvp]: https://github.com/asifdotpy/open-talent/releases/tag/v1.0.0-mvp
