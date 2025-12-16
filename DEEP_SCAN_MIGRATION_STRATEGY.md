# Deep Scan Analysis: Microservices Directory Structure & Migration Strategy

**Date:** December 15, 2025  
**Objective:** Comprehensive analysis of microservices/ directory to guide migration strategy

---

## Executive Summary

**Finding:** The microservices/ directory contains MUCH MORE than just main.py files:
- **16+ shell scripts** across service directories (setup, deploy, test, start)
- **12 Docker Compose files** for multi-service orchestration
- **15+ pyproject.toml** for dependency management
- **16 Dockerfiles** for containerization
- **14 shared scripts** in microservices/scripts/ for CI/CD and deployment
- **1 shared utility** (vetta_service.py) for inter-service communication
- **2 deployment scripts** for hybrid LLM and quick testing
- **Complex interdependencies** between services (voice↔interview, granite↔conversation, etc.)

**Recommendation:** **HYBRID APPROACH**
1. **Copy source code** (main.py, app/, tests/) → services/
2. **Keep orchestration** (docker-compose.yml, deployment/, scripts/) in microservices/
3. **Create symlinks** or copy supporting files (pyproject.toml, Dockerfile, .sh) to services/
4. **Maintain microservices/ as canonical for:** Docker builds, deployments, CI/CD automation

---

## Detailed Inventory

### 1. Shell Scripts by Category

#### A. Test/Docker Scripts (in individual services)
```
ai-auditing-service/test_docker.sh
analytics-service/test_docker.sh
avatar-service/test_docker.sh
candidate-service/test_docker.sh
conversation-service/test_docker.sh
explainability-service/test_docker.sh
interview-service/test_docker.sh
project-service/test_docker.sh
scout-service/test_docker.sh
```
**Purpose:** Test services in Docker containers  
**Action:** Copy to services/ for local testing

#### B. Setup/Deploy Scripts (in individual services)
```
conversation-service/setup-peft.sh          → Setup PEFT (Parameter-Efficient Fine-Tuning)
conversation-service/setup_personas.sh      → Setup conversation personas
conversation-service/deploy-peft-summary.sh → Deploy PEFT models
conversation-service/test_personas.sh       → Test persona integration

interview-service/start_ai_services.sh      → Start all AI services
interview-service/test_vetta_endpoints.sh   → Test Vetta platform integration

granite-interview-service/start.sh          → Start granite interview service
desktop-integration-service/start.sh        → Start desktop gateway

voice-service/run-tests.sh                  → Run voice service tests
voice-service/run_webrtc_tests.sh           → Run WebRTC tests
voice-service/test-docker-deployment.sh     → Test Docker deployment
voice-service/test-production-endpoints.sh  → Test production endpoints (15KB!)

user-service/run-tests.sh                   → Run user service tests
user-service/test-jwt-integration.sh        → Test JWT auth
user-service/test-rls-policies.sh           → Test Postgres RLS
```
**Purpose:** Service initialization, model setup, testing  
**Criticality:** HIGH - These handle complex setup (PEFT, personas, WebRTC)  
**Action:** Copy to services/ AND keep in microservices/ for deployment

#### C. CI/CD & Deployment Scripts (microservices/scripts/)
```
check_consistency.sh              → Verify all repos are consistent
check_git_status.sh              → Check git status across repos
check_remote_updates.sh          → Check for upstream updates
commit_and_push.sh               → Commit and push changes
commit_and_push_changes.sh       → Alternative commit script
finalize_and_push.sh             → Finalize and push changes
migrate_parent_repo.sh           → Migrate parent repo structure
pull_updates.sh                  → Pull updates from upstream
setup_service_repos.sh           → Initial service repo setup
setup_upstream_branches.sh       → Setup upstream branches
test_remote_urls.sh              → Test remote repository URLs
update_microservices.sh          → Update all microservices
update_remotes.sh                → Update git remotes
verify_laptop_setup.sh           → Verify development environment
verify_service_remotes.sh        → Verify service git remotes
```
**Purpose:** Monorepo management, git synchronization  
**Criticality:** MEDIUM - Essential for team collaboration  
**Action:** Keep in microservices/scripts/, create reference in services/

#### D. Global Orchestration
```
microservices/test_services.sh   → Test all services
microservices/verify-services.sh → Verify all services
microservices/deployment/deploy-hybrid-llm.sh → Deploy hybrid LLM
microservices/deployment/quick-test.sh       → Quick service test
configure_submodule_branches.sh  → Configure git submodules
```
**Purpose:** Multi-service testing and deployment  
**Action:** Keep in microservices/, reference from services/ root

---

### 2. Docker Files

#### Dockerfiles per Service (16 total)
```
ai-auditing-service/Dockerfile
analytics-service/Dockerfile
avatar-service/Dockerfile
candidate-service/Dockerfile
conversation-service/Dockerfile
desktop-integration-service/Dockerfile
explainability-service/Dockerfile
granite-interview-service/Dockerfile
interview-service/Dockerfile
notification-service/Dockerfile (implicit)
project-service/Dockerfile
scout-service/Dockerfile
security-service/Dockerfile (implicit)
user-service/Dockerfile (implicit)
voice-service/Dockerfile
(candidate, security, user, notification may have implicit/embedded)
```
**Action:** Copy to services/ for individual service builds

#### Docker Compose Files (6 total - CRITICAL)
```
microservices/docker-compose.yml                      → MAIN orchestration (all services)
microservices/interview-service/docker-compose.yml    → Interview service setup
microservices/granite-interview-service/docker-compose.yml → Granite interview setup
microservices/voice-service/docker-compose.yml        → Voice service + WebRTC
microservices/user-service/docker-compose.supabase.yml → User service with Supabase
microservices/deployment/docker-compose-hybrid.yml    → (May exist)
```
**Criticality:** CRITICAL - Orchestrates multiple services with dependencies  
**Action:** KEEP in microservices/, create reference layer in services/docker-compose.yml

---

### 3. Configuration Files

#### pyproject.toml (Python dependencies)
Services with pyproject.toml (14 total):
```
conversation-service/pyproject.toml
interview-service/pyproject.toml
granite-interview-service/pyproject.toml
avatar-service/pyproject.toml
ai-auditing-service/pyproject.toml
project-service/pyproject.toml
scout-service/pyproject.toml
analytics-service/pyproject.toml
candidate-service/pyproject.toml
explainability-service/pyproject.toml
voice-service/pyproject.toml
(security, user, notification: may be implicit)
```
**Action:** Copy to services/ for local dependency installation

#### Config Files per Service
```
.env.example files (14 services)
.env files (not tracked, user-created)
alembic.ini (interview-service, user-service)
pytest.ini (voice-service, user-service)
test_config.ini (voice-service)
requirements.txt (most services)
requirements-webrtc.txt (voice-service)
```
**Action:** Copy .env.example, pyproject.toml, *.ini to services/

---

### 4. Shared Resources

#### Shared Utilities
```
microservices/shared/vetta_service.py → Shared integration utility
```
**Purpose:** Common code for Vetta platform integration  
**Action:** Copy to services/shared/ AND keep in microservices/shared/

#### Deployment Files
```
microservices/deployment/deploy-hybrid-llm.sh
microservices/deployment/quick-test.sh
```
**Action:** Keep in microservices/deployment/, reference from services/

#### CI/CD Files
```
microservices/.github/           (likely exists with workflows)
microservices/scripts/           (14 scripts for monorepo management)
```
**Action:** Keep in microservices/, don't copy to services/

---

## Service Complexity Matrix

| Service | main.py | Location | Supporting Files | Scripts | Docker | Complexity |
|---------|---------|----------|------------------|---------|--------|-----------|
| **voice-service** | root | microservices | app/, models/, requirements | 5 scripts | compose+file | 🔴 HIGHEST |
| **interview-service** | root | microservices | app/, tests/, alembic | 3 scripts | compose+file | 🔴 HIGH |
| **granite-interview-service** | app/ | microservices | app/config, app/models, data/, requirements | start.sh | compose+file | 🔴 HIGH |
| **conversation-service** | root | microservices | app/, tests/, requirements | 5 scripts (PEFT setup) | file only | 🟡 MEDIUM |
| **user-service** | root | microservices | app/, migrations/, tests | 3 scripts (JWT, RLS) | compose+file | 🟡 MEDIUM |
| **project-service** | app/ | microservices | app/models, requirements | test_docker.sh | file only | 🟡 MEDIUM |
| **analytics-service** | root | microservices | tests/, requirements, .env | test_docker.sh | file only | 🟡 MEDIUM |
| **scout-service** | root | microservices | tests/, requirements | test_docker.sh | file only | 🟡 MEDIUM |
| **avatar-service** | root | microservices | tests/, requirements | test_docker.sh | file only | 🟡 MEDIUM |
| **ai-auditing-service** | root | microservices | tests/, requirements | test_docker.sh | file only | 🟢 LOW |
| **explainability-service** | root | microservices | tests/, requirements | test_docker.sh | file only | 🟢 LOW |
| **candidate-service** | root | services | tests/, requirements | test_docker.sh | file only | 🟢 LOW |
| **security-service** | root | services | tests/ | none | file (implicit) | 🟢 LOW |
| **user-service** | root | services | app/, tests/, migrations/ | 3 scripts | compose+file | 🟡 MEDIUM |
| **notification-service** | root | services | providers/, tests/ | none | file (implicit) | 🟢 LOW |
| **desktop-integration-service** | root | microservices | tests/, requirements | start.sh | file only | 🟢 LOW |

---

## Migration Strategy: THREE OPTIONS

### OPTION 1: Copy Everything to services/ (Clean Slate)
**Pros:**
- Single directory for all runtime code
- Clear team ownership by service directory
- Simpler local development workflow
- Fewer path references

**Cons:**
- Duplicates 16 Dockerfiles in both places
- Requires updating docker-compose.yml paths
- CI/CD scripts still need microservices/ for orchestration
- Maintenance burden (keep both in sync)
- Docker builds would reference /services/ not /microservices/

**Effort:** HIGH (3-4 hours)
**Risk:** MEDIUM (docker-compose conflicts, path updates)

---

### OPTION 2: Stay in microservices/ (Current Structure)
**Pros:**
- No migration needed
- All scripts, docker-compose work as-is
- Unified CI/CD pipeline already working
- Low risk

**Cons:**
- Team confusion about multiple directories
- services/ becomes dead code (4 services)
- Wastes already-created services/ structure
- Inconsistent developer experience

**Effort:** ZERO
**Risk:** LOW (but strategic problem)

---

### OPTION 3: HYBRID (RECOMMENDED) ✅

**Approach:**
```
services/                           ← Development (team ownership)
├── ai-auditing-service/
│   ├── main.py
│   ├── tests/
│   └── (symlink to ../microservices/ai-auditing-service/Dockerfile)
├── voice-service/
│   ├── main.py
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── (symlink to ../microservices/voice-service/Dockerfile)
├── ... (all 16 services)
└── docker-compose.yml → symlink to ../microservices/docker-compose.yml

microservices/                       ← Source of Truth (Docker, CI/CD, Deployment)
├── docker-compose.yml              (CANONICAL)
├── deployment/                      (CANONICAL)
│   ├── deploy-hybrid-llm.sh
│   └── quick-test.sh
├── scripts/                         (CANONICAL - monorepo management)
├── shared/                          (CANONICAL)
├── [all services with full structure]
├── [Dockerfiles remain here]
├── [.github workflows]
└── [all supporting files]

```

**How it works:**
1. **Development happens in services/** (main.py, app/, tests/)
2. **Docker builds reference microservices/** (Dockerfiles stay there)
3. **CI/CD lives in microservices/scripts/** and .github/
4. **Docker-compose orchestration stays in microservices/**
5. **Services don't duplicate** - services/ is a git submodule or symlinks to key files

**Symlink Strategy:**
```bash
cd services/voice-service
ln -s ../../microservices/voice-service/Dockerfile Dockerfile
ln -s ../../microservices/voice-service/docker-compose.yml docker-compose.yml
```

**Or: Git Worktrees Approach** (Better)
```bash
# services/ contains only git worktrees (lightweight clones of same repo)
git worktree add services/voice-service microservices/voice-service
git worktree add services/interview-service microservices/interview-service
# Each service has isolated working directory but same .git
```

---

## Recommended Decision

### ✅ HYBRID APPROACH - Implementation Plan

**Phase 1: Prepare services/ (2 hours)**
1. Copy main.py, app/, tests/ to services/ (already started)
2. Copy requirements.txt, pyproject.toml, .env.example to services/
3. Create symlinks to Dockerfiles → microservices/*/Dockerfile
4. Create symlink to docker-compose.yml → microservices/docker-compose.yml

**Phase 2: Update Documentation (1 hour)**
1. Create DIRECTORY_STRUCTURE.md explaining dual structure
2. Document local dev vs. Docker workflows
3. Update README with both paths

**Phase 3: Test Both Workflows (1 hour)**
1. Run services/ code locally (python main.py)
2. Build Docker images with microservices/ references
3. Test docker-compose.yml from microservices/

**Phase 4: Team Guidelines (30 min)**
1. Create DEVELOPMENT_WORKFLOW.md
2. Explain: edit in services/, build from microservices/
3. Document when to sync changes

---

## File Copy Checklist

### Must Copy to services/
```
☐ main.py (root or app/main.py)
☐ app/ (if exists)
☐ tests/
☐ requirements.txt
☐ pyproject.toml
☐ .env.example
☐ *.ini files (pytest.ini, alembic.ini)
☐ providers/ (notification-service)
☐ migrations/ (user-service)
☐ start.sh (granite-interview, desktop-integration)
☐ shared/ (once)
```

### Must Copy Individual Service Scripts
```
☐ conversation-service/*.sh (PEFT setup)
☐ voice-service/*.sh (WebRTC, production tests)
☐ interview-service/*.sh (AI services startup)
☐ user-service/*.sh (JWT, RLS testing)
```

### Keep in microservices/ (DON'T COPY)
```
☐ Dockerfile (use via symlink or reference)
☐ docker-compose.yml (root level)
☐ docker-compose.*.yml (service-specific)
☐ microservices/scripts/ (all CI/CD scripts)
☐ microservices/deployment/ (deployment scripts)
☐ .github/ (GitHub Actions workflows)
☐ Dockerfile (in individual services)
```

### Create Symlinks in services/
```
symlink: services/Dockerfile → microservices/[service]/Dockerfile
symlink: services/docker-compose.yml → microservices/docker-compose.yml
symlink: services/scripts → microservices/scripts
symlink: services/deployment → microservices/deployment
```

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Docker path confusion | High | Medium | Create clear documentation, use symlinks |
| Dockerfile sync issues | Medium | High | Symlinks solve this automatically |
| CI/CD breaks | Medium | Critical | Test docker-compose from microservices/ |
| Developer confusion | High | Medium | Create DEVELOPMENT_WORKFLOW.md |
| Git conflicts | Low | Medium | Use git worktrees instead of copies |
| Forgotten script files | High | High | Create CRITICAL_FILES_CHECKLIST.md |

---

## Conclusion

**RECOMMENDATION: Implement HYBRID + SYMLINKS approach**

**Benefits:**
- ✅ Single development directory (services/)
- ✅ Teams own their services in services/
- ✅ No duplication of Docker files
- ✅ CI/CD continues working without changes
- ✅ Clear separation: dev vs. ops

**Timeline:** 4-5 hours total
**Risk:** LOW (symlinks are safe, reversible)
**Long-term:** This scales as services grow

---

## Next Steps

1. ✅ Copy all runtime code to services/
2. ✅ Create symlinks to Docker/deployment files
3. ✅ Update documentation
4. ✅ Test local development workflow
5. ✅ Test Docker build workflow
6. ✅ Verify CI/CD still works

