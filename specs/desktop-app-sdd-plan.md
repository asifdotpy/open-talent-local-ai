# Desktop App SDD Plan (Accelerated MVP + Packaging)

## Scope & Goals
- Cross-platform desktop (Win/macOS/Linux) for hardware detect, model recommendation, setup wizard, config persistence.
- Privacy/offline; no cloud dependencies.

## Functional Requirements
1. Hardware detection: RAM, CPU model/cores, platform; optional GPU flag.
2. Model recommendation: thresholds (<6GB→350M, 6–14GB→2B, ≥14GB→8B) with reason text.
3. Setup wizard: 3 steps (detect → select → confirm), recommendation preselected, override allowed.
4. Config persistence: JSON per platform (AppData/Library/Config), load on startup, skip wizard if present.
5. Packaging: installers for Win (nsis), mac (dmg), Linux (AppImage); correct main/preload paths.
6. Telemetry: none; local logs only.

## Non-Functional Requirements
- Performance: launch <5s on mid hardware; no dev server dependency.
- Security: remove CSP warning in packaged build; minimal CSP meta; sandbox off only if preload isolates.
- Reliability: unit tests for recommender, config I/O, hardware detection (mock); renderer smoke test.
- UX: clear 3-step flow; helpful error/retry; good defaults; readable on Windows scaling.

## Work Breakdown
- Phase 0: Stabilize runtime
  - Force file:// build load in dev/prod; verify preload path; fix Windows blank screen.
  - Add minimal CSP meta in production build.
- Phase 1: Core robustness
  - Optional GPU flag; error banner + retry if detect/recommend fails; validate config schema.
- Phase 2: Tests
  - Unit: recommender, config I/O, hardware detection (mock os).
  - Renderer smoke test with mocked window.electronAPI.
- Phase 3: Packaging
  - Win nsis, mac dmg, Linux AppImage; include dist/main + build renderer; icons; output to release/.
  - Smoke-test packaged apps (Win + Linux/VM; mac when available).
- Phase 4: UX polish
  - Keep progress indicator; loading text; minor style tweaks.
- Phase 5: Docs & known issues
  - Update README/WINDOWS_DEMO; note WSL/AppImage FUSE; CSP dev warning; GPU sandbox.

## Immediate Next Actions
1. Fix Windows blank screen: always load built index.html; confirm preload path; test npm start on Windows with DevTools.
2. Add CSP meta for production build to silence warning in packaged apps.
3. Rebuild Windows installer: `npx electron-builder --win nsis`; smoke-test on Windows.

## Acceptance Checklist
- App shows 3-step wizard on Win/mac/Linux without dev server.
- Hardware info + recommendation displayed; selection saved; restart skips wizard.
- Installers produced in release/ (Win/mac/Linux) and launch successfully.
- Unit tests + renderer smoke test pass.
- No CSP warning in packaged build; dev warning acceptable.
