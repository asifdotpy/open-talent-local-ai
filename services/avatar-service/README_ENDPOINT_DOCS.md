# Avatar Service Documentation Index

> **Created:** December 17, 2025  
> **Status:** 📚 **Documentation Package Complete**

---

## 📋 Documents Created

### 1. [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md) - **Primary Reference**

**Purpose:** Source of truth for what endpoints SHOULD exist

**Contains:**
- Complete list of all endpoints by category
- Location of each endpoint definition
- Duplication analysis
- Remediation plan with exact file locations
- Router configuration explanation
- Testing procedures

**Best for:** Understanding the intended architecture

**Key Sections:**
- Section 3: Voice API (duplicates identified)
- Section 4: Avatar Rendering API
- Section 5: Avatar V1 API
- Section 8: Remediation Plan with code examples

---

### 2. [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md) - **Live Tracker**

**Purpose:** Active tracking of all duplication issues

**Contains:**
- Issue #1: `POST /api/v1/generate-voice` - Duplicate
- Issue #2: `GET /api/v1/voices` - Duplicate
- Issue #3: `GET /health` - Triple definition
- Issue #4: `GET /` - Duplicate (investigating)
- Issue #5: `/render/lipsync` vs `/avatar/v1/lipsync` - Conflict (investigating)
- Remediation timeline
- Verification commands
- Success criteria

**Best for:** Tracking progress and understanding current status

**Current Status:** 🔴 3 confirmed issues open, 2 investigating

---

## 🎯 Quick Summary

### What Was Found

From the curl output showing duplicated endpoints:
```
GET      /                  (duplicate)
GET      /health            (duplicate)
POST     /api/v1/generate-voice    (duplicate)
GET      /api/v1/voices     (duplicate)
```

### Root Cause

**Avatar Service includes endpoints from 3 routers:**
1. `avatar_routes.py` - Avatar rendering
2. `avatar_v1.py` - Advanced avatar features  
3. `voice_routes.py` - Voice generation

**Problem:** The `voice_routes.py` endpoints are ALSO defined in `main.py` as a fallback, creating duplicates.

### Impact

- ✅ **Functionality:** Works (both definitions identical)
- ❌ **Code Quality:** Violates DRY principle
- ⚠️ **Maintenance:** Changes needed in 2 places
- 🟡 **Testing:** Confusing which endpoint runs

---

## 📊 Issue Summary

| Issue | Endpoint | Status | Severity | Fix Time |
|-------|----------|--------|----------|----------|
| #1 | `POST /api/v1/generate-voice` | 🔴 Open | 🔴 Critical | 5 min |
| #2 | `GET /api/v1/voices` | 🔴 Open | 🔴 Critical | 0 min* |
| #3 | `GET /health` | 🔴 Open | 🟡 High | 10 min |
| #4 | `GET /` | 🟡 Investigating | 🟡 High | 15 min |
| #5 | `/render/lipsync` | 🟡 Investigating | 🟡 Medium | 20 min |

*Same fix as #1 (delete same block)

---

## 🚀 Next Steps

### Immediate (Today - Dec 17)

**Fix Issues #1 & #2:**

```bash
# In services/avatar-service/main.py
# Delete lines 323-334 (fallback voice endpoints)

# Verify the fix
curl -s http://127.0.0.1:8012/api-docs | python -c "
import sys, json
data = json.load(sys.stdin)
paths = [r['path'] for r in data['routes']]
print(f'Routes before: ~16, Routes after: {len(set(paths))} unique')
"
```

See [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#issue-1-post-apiv1generate-voice---duplicate-definition) for exact code to delete.

### Soon (Dec 18)

**Fix Issue #3:**

Remove `/health` endpoints from routers (lines to delete specified in tracking doc).

### This Sprint (Dec 20)

**Investigate & Clarify Issues #4 & #5:**

Test both endpoints, make architectural decisions, document findings.

---

## 📖 How to Use These Documents

### For Developers

**I need to understand the endpoint architecture:**
1. Read [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md) Section 1-5
2. Check [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md) for current status

**I need to fix the duplicates:**
1. Read [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#phase-1-critical-duplicates-this-week)
2. Follow exact code locations and test commands

**I need to verify my fix:**
1. Run verification commands in [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md#testing-endpoints)
2. Check status in [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#success-criteria)

### For Managers

**I need a quick status update:**
1. See [Quick Summary](#-quick-summary) above
2. See [Issue Summary](#-issue-summary) table
3. See [Next Steps](#-next-steps)

**I need to track progress:**
1. Monitor [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#change-log)
2. Update status regularly

### For Architects

**I need to understand why this happened:**
1. Read [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md#router-configuration)
2. Read [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#why-duplicates-happen)

**I need to prevent this in future:**
1. See [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#how-to-prevent-in-future)
2. Implement checks in CI/CD

---

## 📍 File Locations

### Specification & Tracking (in avatar-service/)

```
services/avatar-service/
├── ENDPOINT_SPECIFICATION.md        👈 Read first (what should exist)
└── ENDPOINT_DUPLICATION_TRACKING.md 👈 Read second (what's wrong & how to fix)
```

### Source Code (what needs to be fixed)

```
services/avatar-service/
├── main.py
│   ├── Line 176: GET / (keep)
│   ├── Line 195: GET /ping (keep)
│   ├── Line 234: GET /health (keep)
│   ├── Line 265: POST /render/lipsync (keep)
│   └── Lines 323-334: ❌ DELETE (fallback voice endpoints - duplicates)
│
└── app/routes/
    ├── voice_routes.py
    │   ├── Line 13: GET / (potentially duplicate - investigating)
    │   ├── Line 19: GET /health (❌ REMOVE duplicate)
    │   ├── Line 28: POST /api/v1/generate-voice (✅ keep - primary)
    │   └── Line 34: GET /api/v1/voices (✅ keep - primary)
    │
    ├── avatar_routes.py
    │   ├── Multiple endpoints (✅ keep)
    │   └── Line ~268: GET /health (❌ REMOVE duplicate)
    │
    └── avatar_v1.py
        └── Multiple endpoints (✅ keep)
```

---

## ✅ Verification Checklist

### Before Fix
- [ ] Run: `curl -s http://127.0.0.1:8012/api-docs | grep '"path"'` 
- [ ] Count unique vs total routes
- [ ] Note duplicates

### After Fix
- [ ] Lines 323-334 deleted from main.py
- [ ] Voice endpoint from router works
- [ ] Health endpoint still works
- [ ] Run: `curl -s http://127.0.0.1:8012/api-docs | grep '"path"'`
- [ ] Count reduced to unique routes only
- [ ] No duplicates remain

---

## 🔗 Related Documents (Workspace Root)

From earlier analysis:
- `ENDPOINT_DUPLICATION_QUICK_REFERENCE.md` - Quick fix guide
- `AVATAR_SERVICE_ENDPOINT_ANALYSIS.md` - Detailed analysis
- `ENDPOINT_VERIFICATION_REPORT_DEC15.md` - Full verification report
- `ANALYSIS_COMPLETE_DEC15.md` - December 15 findings

---

## 📞 Support

**Questions about the specification?**
→ See [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md)

**Need to track progress?**
→ See [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md)

**What endpoints should exist?**
→ [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md#endpoint-categories)

**How to fix the duplicates?**
→ [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md#resolution)

---

## 📝 Maintenance

### Update This Index When

1. Any document is added/modified
2. Status changes (issues fixed, new issues found)
3. Phase completes (Phase 1, 2, 3)

### Keep Synchronized

- [ENDPOINT_SPECIFICATION.md](ENDPOINT_SPECIFICATION.md) - Reference architecture
- [ENDPOINT_DUPLICATION_TRACKING.md](ENDPOINT_DUPLICATION_TRACKING.md) - Current status
- Source code - Actual implementation

---

**Created:** December 17, 2025  
**Version:** 1.0  
**Status:** 📚 Documentation Package Ready  
**Next Update:** After Phase 1 fixes applied
