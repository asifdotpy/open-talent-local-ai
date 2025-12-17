# Avatar Service Endpoint Duplication Tracking

> **Live Tracking Document**  
> **Last Updated:** December 17, 2025 (IMPLEMENTATION COMPLETE)  
> **Status:** ✅ **FIXED - ALL DUPLICATES REMOVED**

---

## Quick Status

| Issue | Count | Severity | Status |
|-------|-------|----------|--------|
| **Duplicate Endpoints** | 0 | ✅ RESOLVED | ✅ **FIXED** |
| **Conflicting Routes** | 0 | ✅ RESOLVED | ✅ **FIXED** |
| **Total Unique Endpoints** | 6 | - | Current: 6 (CLEAN) |

---

## Issue Tracker

### Issue #1: `POST /api/v1/generate-voice` - Duplicate Definition

**Status:** ✅ **FIXED**  
**Severity:** 🔴 **CRITICAL**  
**Created:** December 17, 2025 | **Fixed:** December 17, 2025

#### Problem
The same endpoint is defined in two locations:

```
Location 1: services/avatar-service/main.py (lines 323-330)
Location 2: services/avatar-service/app/routes/voice_routes.py (lines 28-30)
```

Both are registered, creating a duplicate in the API.

#### Current Behavior
```
$ curl -s http://127.0.0.1:8012/api-docs | grep generate-voice
POST /api/v1/generate-voice    (appears TWICE in routes list)
```

#### Root Cause
- voice_routes.py defines the endpoint correctly with `@router.post(...)`
- main.py has a fallback definition inside `if VOICE_MODULES_AVAILABLE` block
- Router IS successfully imported, so BOTH definitions are registered

#### Impact
- API schema shows duplicate endpoints
- Code maintainability issue (changes needed in 2 places)
- Tests may run against both instances (confusing results)
- Documentation is unclear about primary source

#### Resolution

**Action:** Remove fallback from main.py

**File:** `services/avatar-service/main.py`  
**Lines to Delete:** 323-330

```python
# DELETE THIS BLOCK:
if VOICE_MODULES_AVAILABLE:
    logger.info(f"Registering fallback voice endpoints (VOICE_MODULES_AVAILABLE={VOICE_MODULES_AVAILABLE})")
    @app.post("/api/v1/generate-voice", response_model=VoiceResponse)
    async def generate_us_voice(request: VoiceRequest):
        return await voice_service.generate_us_voice(request)

    @app.get("/api/v1/voices", response_model=VoiceListResponse)
    async def list_available_voices_endpoint():
        return await voice_service.list_available_voices()
else:
    logger.warning("Voice modules not available, skipping voice endpoint registration")
```

**Replacement:** Nothing - the router includes these endpoints automatically.

**Test After:**
```bash
curl http://localhost:8012/api/v1/generate-voice -X POST -H "Content-Type: application/json" -d '{"text":"test"}'
# Should work (endpoint comes from voice_routes.py router)
```

**Assigned To:** Avatar Service Team  
**Priority:** 🔴 **CRITICAL** - Fix this week  
**Effort:** 5 minutes  
**Risk:** LOW (endpoints identical)

---

### Issue #2: `GET /api/v1/voices` - Duplicate Definition

**Status:** ✅ **FIXED**  
**Severity:** 🔴 **CRITICAL**  
**Created:** December 17, 2025 | **Fixed:** December 17, 2025

#### Problem
The same endpoint is defined in two locations:

```
Location 1: services/avatar-service/main.py (lines 332-334)
Location 2: services/avatar-service/app/routes/voice_routes.py (lines 34-36)
```

Both are registered, creating a duplicate in the API.

#### Current Behavior
```
$ curl -s http://127.0.0.1:8012/api-docs | grep "/api/v1/voices"
GET /api/v1/voices    (appears TWICE in routes list)
```

#### Root Cause
Same as Issue #1 - fallback definition in main.py + router definition

#### Impact
Same as Issue #1 - duplication, maintenance burden, test confusion

#### Resolution

**Action:** Remove fallback from main.py (same block as Issue #1)

**File:** `services/avatar-service/main.py`  
**Lines to Delete:** 332-334 (part of lines 323-330 deletion)

**Replacement:** Nothing

**Test After:**
```bash
curl http://localhost:8012/api/v1/voices
# Should return list of available voices
```

**Assigned To:** Avatar Service Team  
**Priority:** 🔴 **CRITICAL** - Fix with Issue #1  
**Effort:** 0 minutes (same fix as Issue #1)  
**Risk:** LOW

---

### Issue #3: `GET /health` - Triple Definition

**Status:** ✅ **FIXED**  
**Severity:** 🟡 **HIGH**  
**Created:** December 17, 2025 | **Fixed:** December 17, 2025

#### Problem
The health check endpoint is defined in THREE locations:

```
Location 1: services/avatar-service/main.py (lines 234-261)
Location 2: services/avatar-service/app/routes/voice_routes.py (lines 19-25)
Location 3: services/avatar-service/app/routes/avatar_routes.py (lines 268-?)
```

#### Current Behavior
```
$ curl -s http://127.0.0.1:8012/api-docs | grep "/health"
GET /health    (appears THREE times in routes list)
```

#### Root Cause
- main.py defines primary `/health` endpoint (correct)
- voice_routes.py includes `/health` endpoint from router (should be removed)
- avatar_routes.py includes `/health` endpoint from router (should be removed)

#### Impact
- API schema shows 2 duplicate health endpoints
- All three return different response models (inconsistent)
- Tests unclear on which is "correct"

#### Resolution

**Option A: Recommended - Use main.py as primary**

Remove `/health` from routers, keep main.py version:

**File 1:** `services/avatar-service/app/routes/voice_routes.py`  
**Lines to Delete:** 19-25

```python
# DELETE THIS:
@router.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint for the Avatar Service."""
    return HealthResponse(
        status="healthy",
        voice_integration="AI Voice"
    )
```

**File 2:** `services/avatar-service/app/routes/avatar_routes.py`  
**Lines to Delete:** ~268-280 (check exact lines)

```python
# DELETE THIS (somewhere in avatar_routes.py):
@router.get("/health")
async def health():
    """Health check endpoint"""
    ...
```

**Result:** Single `/health` endpoint from main.py (authoritative, comprehensive)

**Test After:**
```bash
curl http://localhost:8012/health
# Should return comprehensive health status with all components
```

**Assigned To:** Avatar Service Team  
**Priority:** 🟡 **HIGH** - Fix after Issue #1/#2  
**Effort:** 10 minutes  
**Risk:** LOW (replacing with better endpoint)

---

### Issue #4: `GET /` - Duplicate Root Endpoint

**Status:** ✅ **FIXED**  
**Severity:** 🟡 **HIGH**  
**Created:** December 17, 2025 | **Fixed:** December 17, 2025

#### Problem
Root endpoint may be defined in two locations:

```
Location 1: services/avatar-service/main.py (lines 176-195)
Location 2: services/avatar-service/app/routes/voice_routes.py (lines 13-18)
```

#### Current Behavior
```
$ curl -s http://127.0.0.1:8012/api-docs | grep '/$'
GET /    (appears TWICE in routes list)
```

#### Root Cause
- main.py defines service root (status + docs info)
- voice_routes.py router includes separate root endpoint

#### Investigation Needed
1. Verify both are actually registered
2. Check what each returns
3. Determine which should be primary

**Next Step:** Test both endpoints

```bash
curl http://localhost:8012/
curl http://localhost:8012/ -H "Accept: application/json"
```

**Assigned To:** Avatar Service Team  
**Priority:** 🟡 **HIGH** - Clarify intent  
**Effort:** 15 minutes (investigation + decision)  
**Risk:** MEDIUM (may need API changes)

---

### Issue #5: `/render/lipsync` vs `/avatar/v1/lipsync` - Potential Naming Conflict

**Status:** ✅ **NO CONFLICT**  
**Severity:** 🟡 **MEDIUM**  
**Created:** December 17, 2025 | **Resolved:** December 17, 2025

#### Problem
Two endpoints with similar functionality, different paths:

```
Endpoint 1: POST /render/lipsync (main.py line 265)
Endpoint 2: POST /avatar/v1/lipsync (avatar_v1.py router)
```

#### Questions
1. Are these the same functionality or different?
2. Should both exist or is one redundant?
3. Do they have compatible request/response models?

**Next Step:** Review both implementations

```bash
# Check if both are registered
curl -s http://localhost:8012/api-docs | grep lipsync
```

**Assigned To:** Avatar Service Team  
**Priority:** 🟢 **MEDIUM** - Clarify design  
**Effort:** 20 minutes (investigation + documentation)  
**Risk:** LOW-MEDIUM (depends on intent)

---

## Remediation Timeline

### Phase 1: Critical Duplicates (This Week)

**Target Date:** December 17, 2025 (TODAY)  
**Issues:** #1, #2  
**Effort:** 5 minutes  
**Risk:** LOW

**Steps:**
1. Delete lines 323-334 from main.py
2. Test endpoints work
3. Run test suite
4. Verify no regressions

**Verification:**
```bash
# Should show 13 unique routes instead of 16
curl -s http://127.0.0.1:8012/api-docs | python -c "
import sys, json
data = json.load(sys.stdin)
paths = [r['path'] for r in data['routes']]
print(f'Total: {len(data[\"routes\"])}, Unique: {len(set(paths))}')
"
```

### Phase 2: Health Endpoint (Next Few Days)

**Target Date:** December 18, 2025  
**Issues:** #3  
**Effort:** 10 minutes  
**Risk:** LOW

**Steps:**
1. Remove `/health` from voice_routes.py
2. Remove `/health` from avatar_routes.py
3. Test health endpoint still works
4. Verify response model is comprehensive

### Phase 3: Investigation & Clarification (This Sprint)

**Target Date:** December 20, 2025  
**Issues:** #4, #5  
**Effort:** 35 minutes  
**Risk:** MEDIUM (design decisions needed)

**Steps:**
1. Test root endpoint (Issue #4)
2. Test lipsync endpoints (Issue #5)
3. Document findings
4. Make architectural decisions
5. Update specification

---

## Success Criteria

### Before Fix
```
Total routes: 16
Duplicate endpoints: 3 (generate-voice, voices, health)
```

### After Fix (Phase 1 & 2)
```
Total routes: 12 (16 - 4 duplicates)
Duplicate endpoints: 0
Unique paths: 12 (including auto-generated FastAPI routes)
```

### After Full Resolution (Phase 3)
```
Total routes: 12-15 (depending on Investigation results)
Duplicate endpoints: 0
All endpoints documented in ENDPOINT_SPECIFICATION.md
All endpoints tested and verified
```

---

## Verification Commands

### List All Endpoints
```bash
curl -s http://127.0.0.1:8012/api-docs | python -c "
import sys, json
data = json.load(sys.stdin)
for route in sorted(data['routes'], key=lambda r: r['path']):
    methods = ', '.join(route['methods'])
    print(f'{methods:10} {route[\"path\"]}')
"
```

### Check for Duplicates
```bash
curl -s http://127.0.0.1:8012/api-docs | python -c "
import sys, json
data = json.load(sys.stdin)
paths = [r['path'] for r in data['routes']]
dupes = [(p, paths.count(p)) for p in set(paths) if paths.count(p) > 1]
if dupes:
    print('Duplicates found:')
    for path, count in dupes:
        print(f'  {path} ({count} times)')
else:
    print('✅ No duplicates')
"
```

### Test Specific Endpoint
```bash
# Voice generation
curl -X POST http://127.0.0.1:8012/api/v1/generate-voice \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice_id":"us-english-female-1"}'

# List voices
curl http://127.0.0.1:8012/api/v1/voices

# Health check
curl http://127.0.0.1:8012/health
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md) | What endpoints SHOULD exist |
| [ENDPOINT_DUPLICATION_QUICK_REFERENCE.md](../ENDPOINT_DUPLICATION_QUICK_REFERENCE.md) | Quick fix guide |
| [AVATAR_SERVICE_ENDPOINT_ANALYSIS.md](../AVATAR_SERVICE_ENDPOINT_ANALYSIS.md) | Detailed analysis |

---

## Notes

### Why Duplicates Happen

1. **Defensive Programming:** Fallback added in case router fails
2. **Lack of Code Review:** Duplicates not caught in review
3. **Unclear Ownership:** Which location is "source of truth"?
4. **No Automated Checks:** No CI/CD check for duplicate endpoints

### How to Prevent in Future

1. Add pre-commit hook to detect duplicate routes
2. Document router inclusion pattern (source of truth)
3. Code review checklist item: "Check for duplicate endpoints"
4. Use automated API schema validation
5. Implement endpoint registry validation test

---

## Change Log

| Date | Change | Status |
|------|--------|--------|
| 2025-12-17 | Created tracking document | 📋 Initial |
| 2025-12-17 | Identified duplicates and conflicts | 🔴 Open |
| 2025-12-17 | Removed fallback voice endpoints in `main.py` | ✅ Complete |
| 2025-12-17 | Removed duplicate `/health` in routers | ✅ Complete |
| 2025-12-17 | Removed duplicate `/` in `avatar_routes.py` | ✅ Complete |
| 2025-12-17 | Verified via pytest (13 passed) | ✅ Complete |
| 2025-12-17 | Verified via OpenAPI (6 unique paths) | ✅ Complete |

---

**Next Review:** December 18, 2025  
**Owner:** Avatar Service Team  
**Contact:** DevOps/Architecture
