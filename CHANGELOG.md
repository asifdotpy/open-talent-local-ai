# Changelog

All notable changes to the **OpenTalent** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-release] - 2026-01-02

### Added

- **Production-Ready Documentation**: Introduced a comprehensive `SETUP_GUIDE.md` for fresh machine installations and updated the `README.md` with the latest project status and quick-start instructions.
- **Full Schema Coverage**: Implemented Pydantic models for the **Security** and **Notification** services, achieving 100% schema coverage across all 271+ API endpoints for robust data validation.
- **Enhanced Gateway Exposure**: Successfully exposed high-value endpoints via the **Desktop Integration Service**, including Scout Service talent search (GitHub/LinkedIn) and Voice Service real-time TTS/STT streaming.
- **Automated Release Verification**: Added a `verify-release.sh` script to perform end-to-end system checks, including TypeScript compilation, Jest test suites, and service discovery health.

### Changed

- **API Gateway Synchronization**: Re-registered the **Scout Service** in the central service discovery and corrected the **Candidate Service** port mapping (from 8008 to 8006) to ensure 100% service reachability.
- **Desktop App Stabilization**: Refactored the `desktop-app` to resolve all TypeScript compilation errors, including the restoration of the missing `cn` utility and alignment of the `PipelineConfig` interface.
- **Runtime Compatibility**: Implemented a polyfill for `AbortSignal.timeout` in the `jobDescriptionParser`, ensuring compatibility with the Electron/Node.js runtime environment.

### Fixed

- **Critical Integration Blockers**: Resolved the "Module Not Found" errors in the `qualityScoringClient` and fixed the API contract mismatches in the `scoutCoordinatorClient` test suite.
- **Service Discovery Failures**: Fixed the health check logic in the gateway to correctly identify and route traffic to all 14 microservices.
- **Candidate Results View**: Stabilized the main results display by resolving syntax errors in the `CandidateResults.tsx` component.

---

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

[1.0.0-release]: https://github.com/asifdotpy/open-talent-local-ai/releases/tag/v1.0.0-release
[1.0.0-mvp]: https://github.com/asifdotpy/open-talent-local-ai/releases/tag/v1.0.0-mvp
