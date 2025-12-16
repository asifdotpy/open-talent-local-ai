# Comprehensive Plan: Copy Working Microservices → Services

**Date:** December 15, 2025  
**Objective:** Consolidate all working microservices from `microservices/` into `services/` directory  
**Current Status:** 4 complete services in services/ (Candidate, Notification, Security, User); 10+ incomplete (tests-only)

---

## Executive Summary

**Goal:** Move microservices/ → services/ as canonical runtime location  
**Services to Copy:** 15 microservices with main.py  
**Copy Strategy:** Full directory copy preserving structure (app/, tests/, requirements, config, docs)  
**Validation:** Verify imports, port numbers, and FastAPI entrypoints post-copy  

---

## Services Inventory (microservices/)

### ✅ COMPLETE SERVICES (Have main.py + supporting files)

| Service | Location | main.py | tests/ | requirements | docs | Status |
|---------|----------|---------|--------|--------------|------|--------|
| notification-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (providers/, main.py) |
| security-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| user-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| candidate-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| voice-service | root | ✅ | ✅ | ✅ | ✅ | Full (app/, models/, requirements, Dockerfile, tests) |
| analytics-service | root | ✅ | ❌ | ✅ | ✅ | Partial (main.py, requirements, .env.example) |
| interview-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| granite-interview-service | **app/** | ✅ | ✅ | ✅ | ✅ | **Full (app/main.py, app/config, app/services, requirements, Dockerfile, docker-compose)** |
| conversation-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| avatar-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| scout-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| explainability-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| ai-auditing-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| desktop-integration-service | root | ✅ | ✅ | ❌ | ❌ | Minimal (main.py only) |
| project-service | **app/** | ✅ | ✅ | ✅ | ❌ | **Full (app/main.py, app/models, requirements, Dockerfile, pyproject.toml)** |

**NOT INCLUDED (incomplete/empty):**
- integration-service/ (empty directory, no code)
- avatar-animation-service/ (only venv/, no code)
- shared/ (shared utilities library)
- deployment/, scripts/, .github/ (CI/CD & infrastructure)

---

## Copy Plan: microservices/ → services/

### Phase 1: Identify & Validate Source (microservices/)

**Step 1a: List all source services**
```
microservices/notification-service       (has: main.py, providers/, tests/)
microservices/security-service           (has: main.py, tests/)
microservices/user-service               (has: main.py, tests/)
microservices/candidate-service          (has: main.py, tests/)
microservices/voice-service              (has: main.py, app/, tests/, requirements.txt)
microservices/analytics-service          (has: main.py, requirements.txt)
microservices/interview-service          (has: main.py, tests/)
microservices/granite-interview-service  (has: main.py, tests/)
microservices/conversation-service       (has: main.py, tests/)
microservices/avatar-service             (has: main.py, tests/)
microservices/avatar-animation-service   (has: main.py)
microservices/scout-service              (has: main.py, tests/)
microservices/explainability-service     (has: main.py, tests/)
microservices/ai-auditing-service        (has: main.py, tests/)
microservices/desktop-integration-service(has: main.py, tests/)
```

**Step 1b: Verify each source service is runnable**
- main.py exists and imports FastAPI
- Port number documented (extract from main.py if uvicorn.run statement exists)
- No broken imports (surface check: main.py reads without SyntaxError)

### Phase 2: Prepare Destination (services/)

**Step 2a: Backup existing services/**
```bash
# Preserve current services/ that may have local-only changes
cp -r services services_backup_dec15
```

**Step 2b: Create structure for each service**
For each service, ensure destination exists:
```
services/
├── ai-auditing-service/      (tests/ already exists, add main.py)
├── analytics-service/        (tests/ already exists, add main.py + requirements)
├── avatar-service/           (tests/ already exists, add main.py)
├── candidate-service/        (has main.py already, verify complete)
├── conversation-service/     (tests/ already exists, add main.py)
├── desktop-integration-service/ (tests/ already exists, add main.py)
├── explainability-service/   (tests/ already exists, add main.py)
├── granite-interview-service/ (tests/ already exists, add main.py)
├── interview-service/        (tests/ already exists, add main.py)
├── notification-service/     (has main.py already, add providers/)
├── scout-service/            (tests/ already exists, add main.py)
├── security-service/         (has main.py already, verify complete)
├── user-service/             (has main.py + app/, verify complete)
└── voice-service/            (tests/ only; add main.py + app/ + requirements)
```

### Phase 3: Copy Each Service

**Step 3a: Copy Minimal Services (main.py + tests/)**
Copy directories (preserve structure):
- microservices/ai-auditing-service → services/ai-auditing-service (overwrite existing tests/)
- microservices/analytics-service → services/analytics-service (add main.py + requirements)
- microservices/avatar-service → services/avatar-service (add main.py)
- microservices/conversation-service → services/conversation-service (add main.py)
- microservices/desktop-integration-service → services/desktop-integration-service (add main.py)
- microservices/explainability-service → services/explainability-service (add main.py)
- microservices/granite-interview-service → services/granite-interview-service (add main.py)
- microservices/interview-service → services/interview-service (add main.py)
- microservices/notification-service → services/notification-service (add providers/)
- microservices/scout-service → services/scout-service (add main.py)

**Step 3b: Copy Full-Featured Services (main.py + app/ + requirements + tests + docs)**
- microservices/voice-service → services/voice-service (add app/, requirements, models/, etc.)
- Verify: main.py, app/, tests/, requirements.txt, pyproject.toml, Dockerfile, .env.example

**Step 3c: Verify Already-Present Services**
- services/candidate-service (verify main.py is complete)
- services/security-service (verify main.py is complete)
- services/user-service (verify main.py + app/ + migrations)

### Phase 4: Validate Post-Copy

**Step 4a: Per-service validation**
For each service copied:
1. main.py exists and reads cleanly (no SyntaxError)
2. FastAPI import present
3. Port number correct (from app = FastAPI(...) context or uvicorn.run statement)
4. tests/ directory exists and has test files
5. requirements.txt (if original had) is present

**Step 4b: Verify imports**
```bash
cd services/<service>
python -m py_compile main.py  # Check for syntax errors
```

**Step 4c: Port conflict check**
- Ensure each service has unique port
- Update any hardcoded ports if duplicates found

**Step 4d: Documentation consistency**
- Ensure port numbers match in MICROSERVICES_API_INVENTORY.md
- Update any references from microservices/ to services/

### Phase 5: Update Documentation

**Step 5a: Update MICROSERVICES_API_INVENTORY.md**
- Change title: "Microservices API Inventory" → "Services API Inventory"
- Update all file paths: microservices/ → services/
- Update all references to config/settings files
- Verify port numbers match actual code

**Step 5b: Update gap analysis docs**
- API_ENDPOINTS_GAP_ANALYSIS.md: Update service paths
- API_CATALOG_UPDATES_DEC15_FINAL.md: Update service references

**Step 5c: Create SERVICES_DIRECTORY_STRUCTURE.md**
Document final structure and which services are ready for demo

### Phase 6: Testing & Verification

**Step 6a: Quick health check**
```bash
# Try importing each service
for service in services/*/main.py; do
  echo "Testing $service"
  python -c "import sys; sys.path.insert(0, $(dirname $service)); import main"
done
```

**Step 6b: Verify gateway discovery**
- Ensure desktop-integration-service can find all services on expected ports
- Update service_discovery.py if needed to reference services/ paths

---

## Detailed Copy Procedure

### Services to Copy (16 total)

1. **ai-auditing-service** (8012)
   - Source: microservices/ai-auditing-service/main.py (root)
   - Contents: main.py, tests/
   - Action: Copy main.py to services/ai-auditing-service/ (preserve tests/)

2. **analytics-service** (8007)
   - Source: microservices/analytics-service/main.py (root)
   - Contents: main.py, requirements.txt, .env.example, Dockerfile
   - Action: Copy all to services/analytics-service/ (preserve tests/)

3. **avatar-service** (8004)
   - Source: microservices/avatar-service/main.py (root)
   - Contents: main.py, tests/
   - Action: Copy main.py to services/avatar-service/ (preserve tests/)

4. **candidate-service** (8006)
   - Source: microservices/candidate-service/main.py (root)
   - Already in services/; verify parity with microservices version

5. **conversation-service** (8002)
   - Source: microservices/conversation-service/main.py (root)
   - Contents: main.py, tests/
   - Action: Copy main.py to services/conversation-service/ (preserve tests/)

6. **desktop-integration-service** (8009)
   - Source: microservices/desktop-integration-service/main.py (root)
   - Contents: main.py, tests/
   - Action: Copy main.py to services/desktop-integration-service/ (preserve tests/)

7. **explainability-service** (8013)
   - Source: microservices/explainability-service/main.py (root)
   - Contents: main.py, tests/
   - Action: Copy main.py to services/explainability-service/ (preserve tests/)

8. **granite-interview-service** (8005) - **FULL STRUCTURE**
   - Source: microservices/granite-interview-service/app/main.py + microservices/granite-interview-service/app/*
   - Contents: app/ (main.py, config/, models/, services/, training/), requirements.txt, Dockerfile, docker-compose.yml, start.sh, data/
   - Action: Copy entire directory including app/, requirements, docker files (preserve tests/)

9. **interview-service** (8005)
   - Source: microservices/interview-service/main.py (root)
   - Contents: main.py, tests/
   - Action: Copy main.py to services/interview-service/ (preserve tests/)

10. **notification-service** (8011)
    - Source: microservices/notification-service/main.py (root)
    - Contents: main.py, providers/, tests/, test_harness.py
    - Already in services/; verify complete with providers/
    - Action: Copy providers/ to services/notification-service/ if missing (preserve tests/)

11. **project-service** (NEW - PORT TBD) - **FULL STRUCTURE**
    - Source: microservices/project-service/app/main.py + microservices/project-service/app/*
    - Contents: app/ (main.py, models.py, __init__.py), requirements.txt, Dockerfile, pyproject.toml, .github/
    - Action: Copy entire directory including app/, requirements, docker files (preserve tests/)

12. **scout-service** (8000)
    - Source: microservices/scout-service/main.py (root)
    - Contents: main.py, tests/
    - Action: Copy main.py to services/scout-service/ (preserve tests/)

13. **security-service** (8010)
    - Source: microservices/security-service/main.py (root)
    - Already in services/; verify parity with microservices version

14. **user-service** (8001)
    - Source: microservices/user-service/main.py (root)
    - Already in services/; verify complete with app/, migrations/

15. **voice-service** (8003) - **FULL STRUCTURE**
    - Source: microservices/voice-service/main.py (root) + entire directory
    - Contents: main.py, app/, tests/, requirements.txt, models/, Dockerfile, docker-compose, pyproject.toml, webrtc_*.py, etc.
    - Action: Copy entire directory to services/voice-service/ (preserve tests/)

16. **avatar-animation-service** (8004)
    - Source: microservices/avatar-animation-service/
    - Status: **SKIPPED** - Empty (only venv/, no source code)

---

## Success Criteria

✅ All 15 services exist under services/  
✅ Each service has main.py (FastAPI entrypoint)  
✅ Each service has tests/ (test coverage)  
✅ services/voice-service has app/ + requirements.txt  
✅ services/user-service has app/ + migrations/  
✅ No import errors when importing each main.py  
✅ Port numbers unique (no conflicts)  
✅ Documentation updated to point to services/  
✅ Gateway can discover all services  

---

## Timeline & Effort

**Phase 1 (5 min):** Validate sources  
**Phase 2 (5 min):** Prepare destinations  
**Phase 3 (15 min):** Copy all directories (shell script or manual)  
**Phase 4 (10 min):** Validate post-copy (imports, syntax, ports)  
**Phase 5 (10 min):** Update documentation  
**Phase 6 (10 min):** Testing & verification  

**Total Estimated Time:** ~55 minutes

---

## Rollback Plan

If issues occur:
1. Restore from `services_backup_dec15/`
2. Keep microservices/ as fallback reference
3. Document specific issues for fix

---

## Next Steps After Copy

1. Run demo from services/
2. Update CI/CD pipelines to run from services/
3. Optionally archive or remove microservices/ (keep for reference initially)
4. Ensure gateway points to services/ ports
5. Add consolidated documentation

---

