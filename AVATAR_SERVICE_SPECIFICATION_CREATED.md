# Avatar Service Specification & Tracking Documentation

> **Status:** ✅ **Documentation Package Created**  
> **Date:** December 17, 2025  
> **Location:** `services/avatar-service/`

---

## What Was Created

### 3 New Documentation Files in Avatar Service

I've created a comprehensive specification and tracking system for the Avatar Service endpoints:

#### 1. **ENDPOINT_SPECIFICATION.md** (Primary Reference)
```
Location: services/avatar-service/ENDPOINT_SPECIFICATION.md
Purpose: Source of truth for what endpoints SHOULD exist
Size: ~400 lines
Sections: 
  - Overview
  - All endpoints by category (Core, Documentation, Voice, Avatar, Avatar V1)
  - Duplication analysis
  - Remediation plan with exact code locations
  - Router configuration details
  - Testing procedures
```

**Key Info:**
- Documents all 5 routers + main.py endpoints
- Shows which are duplicates with exact line numbers
- Provides implementation examples (correct pattern)
- Includes verification commands

#### 2. **ENDPOINT_DUPLICATION_TRACKING.md** (Live Tracker)
```
Location: services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md
Purpose: Active tracking of all duplication issues & remediation
Size: ~500 lines
Sections:
  - Quick status table
  - Issue #1-5 detailed descriptions
  - Remediation timeline (Phases 1-3)
  - Verification commands
  - Success criteria
  - Change log
```

**Issues Tracked:**
- Issue #1: `POST /api/v1/generate-voice` duplicate (🔴 CRITICAL)
- Issue #2: `GET /api/v1/voices` duplicate (🔴 CRITICAL)
- Issue #3: `GET /health` triple definition (🟡 HIGH)
- Issue #4: `GET /` duplicate (🟡 INVESTIGATING)
- Issue #5: `/lipsync` endpoint conflicts (🟡 INVESTIGATING)

#### 3. **README_ENDPOINT_DOCS.md** (Documentation Index)
```
Location: services/avatar-service/README_ENDPOINT_DOCS.md
Purpose: Navigation guide and quick summary
Size: ~200 lines
Sections:
  - Document index with descriptions
  - Quick summary of findings
  - Issue summary table
  - Next steps (immediate, soon, this sprint)
  - How to use the documents
  - File locations map
  - Verification checklist
```

---

## Why You Need These Documents

### The Problem You Reported
```bash
$ curl -s http://127.0.0.1:8012/api-docs | python -c "..."
Total routes: 16

GET      /                  ← appears TWICE
GET      /health            ← appears TWICE
POST     /api/v1/generate-voice    ← appears TWICE
GET      /api/v1/voices     ← appears TWICE
```

### What Causes This
- Voice endpoints defined in `voice_routes.py` (correct)
- ALSO defined in `main.py` as fallback (wrong, causes duplicate)
- Router gets included automatically
- Both definitions register → **duplication**

### How These Docs Help

1. **ENDPOINT_SPECIFICATION.md**
   - Shows you EXACTLY which endpoints should exist
   - Points to each location (for debugging/fixing)
   - Explains why they're there
   - Provides correct patterns for future endpoints

2. **ENDPOINT_DUPLICATION_TRACKING.md**
   - Lists each duplicate with severity
   - Exact lines to delete (code included)
   - Timeline for fixing
   - Commands to verify fixes
   - Success criteria

3. **README_ENDPOINT_DOCS.md**
   - Quick navigation
   - Status summary
   - Who needs which document
   - File location map

---

## What's Documented

### Endpoints by Category

**Core Service (3 endpoints - ✅ no duplication)**
- GET / (root)
- GET /ping (health for load balancers)
- GET /health (comprehensive health)

**Documentation (5 endpoints - ✅ no duplication)**
- GET /doc (redirect to /docs)
- GET /api-docs (JSON endpoint list)
- GET /docs (Swagger UI - auto)
- GET /redoc (ReDoc - auto)
- GET /openapi.json (OpenAPI schema - auto)

**Voice API (2 endpoints - ❌ DUPLICATED)**
- POST /api/v1/generate-voice (appears 2x)
- GET /api/v1/voices (appears 2x)

**Avatar Rendering (9+ endpoints - ⚠️ needs checking)**
- GET / (serve HTML)
- GET /src/{path:path}
- GET /assets/{path:path}
- POST /generate
- POST /set-phonemes
- GET /phonemes
- POST /generate-from-audio
- GET /info
- GET /health (⚠️ duplicate)

**Avatar V1 Advanced (20+ endpoints - ⚠️ needs checking)**
- /avatar/v1/render, /lipsync, /emotions, etc.

---

## How to Use

### For Immediate Fix (Today)

**Read:** [services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md#issue-1-post-apiv1generate-voice---duplicate-definition)

**Action:** Delete lines 323-334 from `services/avatar-service/main.py`

**Verify:**
```bash
curl -s http://127.0.0.1:8012/api-docs | python -c "
import sys, json
data = json.load(sys.stdin)
paths = [r['path'] for r in data['routes']]
print(f'Total routes: {len(data[\"routes\"])}')
print(f'Unique: {len(set(paths))}')
"
```

Expected: Unique count should increase (fewer duplicates)

### For Ongoing Tracking

**Monitor:** [services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md)

Update as you:
- Fix issues
- Investigate questions
- Complete phases

### For Architecture Understanding

**Read:** [services/avatar-service/ENDPOINT_SPECIFICATION.md](services/avatar-service/ENDPOINT_SPECIFICATION.md)

Sections to understand:
- Section 3-5: Endpoint categories
- Section 6: Router configuration
- Section 8: Remediation plan
- Section 9: Reference implementation

---

## Documentation Structure

```
services/avatar-service/
│
├── README_ENDPOINT_DOCS.md
│   └── Start here (quick navigation)
│
├── ENDPOINT_SPECIFICATION.md
│   └── Detailed specification (all endpoints)
│
├── ENDPOINT_DUPLICATION_TRACKING.md
│   └── Live tracker (issues & fixes)
│
├── main.py
│   └── Source code (needs fixes)
│
└── app/routes/
    ├── voice_routes.py (endpoints correct here)
    ├── avatar_routes.py (check for issues)
    └── avatar_v1.py (check for issues)
```

---

## Timeline

### Phase 1: Critical Duplicates (TODAY - Dec 17)
- **Issue #1 & #2:** Delete lines 323-334 from main.py
- **Effort:** 5 minutes
- **Risk:** LOW
- **Result:** 2 fewer duplicate endpoints

### Phase 2: Health Endpoint (Tomorrow - Dec 18)
- **Issue #3:** Remove /health from routers
- **Effort:** 10 minutes
- **Risk:** LOW
- **Result:** 1 fewer duplicate endpoint

### Phase 3: Investigation (This Sprint - Dec 20)
- **Issue #4 & #5:** Test & clarify endpoints
- **Effort:** 35 minutes
- **Risk:** MEDIUM (design decisions)
- **Result:** Clear architecture for root & lipsync endpoints

---

## Key Stats

| Metric | Value |
|--------|-------|
| Documents Created | 3 |
| Total Lines of Documentation | ~1100 |
| Issues Identified | 5 |
| Critical Issues | 2 |
| High Priority | 2 |
| Medium Priority | 1 |
| Endpoints Duplicated | 3-4 |
| Estimated Fix Time | 30 minutes |
| Risk Level | LOW |

---

## Success Criteria

### Before Fix
```
Total routes: 16 (with duplicates)
Unique paths: ~12
Duplicates: 4
```

### After Phase 1+2
```
Total routes: 11 (16 - 5 duplicates removed)
Unique paths: 11
Duplicates: 0
```

### Verification Command
```bash
curl -s http://127.0.0.1:8012/api-docs | python -c "
import sys, json
data = json.load(sys.stdin)
paths = [r['path'] for r in data['routes']]
duplicates = [p for p in set(paths) if paths.count(p) > 1]
print(f'Total: {len(data[\"routes\"])}, Unique: {len(set(paths))}, Dups: {duplicates}')
"
```

---

## What These Docs Enable

### Testing
- Know exactly which endpoints should be tested
- Know which are duplicates (shouldn't test both)
- Have clear verification commands

### Code Review
- Know what's correct vs wrong
- Have exact line numbers to check
- Know why changes are needed

### Documentation
- Clear specification of API
- Source of truth for developers
- Reference for external documentation

### Maintenance
- Know which endpoint is "primary"
- Know where to make changes
- Know what tests to update

### Future Development
- Know how to add new endpoints
- Know the correct pattern
- Know what to avoid

---

## Next Steps

1. **Read** [services/avatar-service/README_ENDPOINT_DOCS.md](services/avatar-service/README_ENDPOINT_DOCS.md) (5 min)

2. **Review** [services/avatar-service/ENDPOINT_SPECIFICATION.md](services/avatar-service/ENDPOINT_SPECIFICATION.md) (15 min)

3. **Plan** Phase 1 fix using [services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md) (5 min)

4. **Execute** Phase 1 (delete lines 323-334 from main.py) (5 min)

5. **Verify** using commands in tracking doc (2 min)

6. **Update** tracking doc with results (2 min)

7. **Schedule** Phases 2-3 for next week

---

## Questions Answered by These Docs

**Q: What endpoints should the Avatar Service have?**
→ See [ENDPOINT_SPECIFICATION.md](services/avatar-service/ENDPOINT_SPECIFICATION.md)

**Q: Why are there duplicates?**
→ See [ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md#why-duplicates-happen)

**Q: How do I fix them?**
→ See [ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md#remediation-timeline)

**Q: How do I verify the fix?**
→ See [ENDPOINT_SPECIFICATION.md](services/avatar-service/ENDPOINT_SPECIFICATION.md#testing-endpoints)

**Q: What's the timeline?**
→ See [ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md#remediation-timeline)

**Q: Should I fix this now?**
→ See [ENDPOINT_DUPLICATION_TRACKING.md](services/avatar-service/ENDPOINT_DUPLICATION_TRACKING.md#phase-1-critical-duplicates-this-week)

---

## Files to Keep

✅ Keep these documents in `services/avatar-service/`:
- `ENDPOINT_SPECIFICATION.md`
- `ENDPOINT_DUPLICATION_TRACKING.md`
- `README_ENDPOINT_DOCS.md`

They should be:
- Reviewed before making endpoint changes
- Updated as issues are fixed
- Referenced in pull requests
- Part of code review checklist

---

**Created:** December 17, 2025  
**Status:** ✅ Ready for Use  
**Next Review:** After Phase 1 (Dec 17 EOD)  
**Maintenance:** Update as issues are fixed
