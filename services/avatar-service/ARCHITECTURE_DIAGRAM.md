# Avatar Service Architecture & Endpoint Flow Diagram

> **Visual Reference**  
> **Created:** December 17, 2025

---

## 🏗️ Current Architecture (With Duplicates)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application (Port 8012)              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app = FastAPI(...)                                      │  │
│  │                                                          │  │
│  │  # Direct endpoints in main.py                          │  │
│  │  @app.get("/")              ─────┐                       │  │
│  │  @app.get("/ping")          ─────┼─ Service Level       │  │
│  │  @app.get("/health")        ─────┤ Endpoints            │  │
│  │  @app.post("/render/lipsync")────┘                       │  │
│  │                                                          │  │
│  │  # Include routers (lines 140-153)                      │  │
│  │  app.include_router(avatar_router)                       │  │
│  │  app.include_router(avatar_v1_router)                    │  │
│  │  app.include_router(voice_router)                        │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Router: voice_routes.py                    │  │
│  │                                                          │  │
│  │  @router.get("/")                                       │  │
│  │  @router.get("/health")         ←─ DUPLICATES           │  │
│  │  @router.post("/api/v1/generate-voice")  ←─ DUPLICATES │  │
│  │  @router.get("/api/v1/voices")           ←─ DUPLICATES │  │
│  │                                                          │  │
│  │  Results in endpoints registered in app:               │  │
│  │  ├─ GET / (from main.py + from router) = 2 copies      │  │
│  │  ├─ GET /health (from main.py + from router) = 2 copies │  │
│  │  ├─ POST /api/v1/generate-voice = 2 copies              │  │
│  │  └─ GET /api/v1/voices = 2 copies                       │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Router: avatar_routes.py                       │  │
│  │                                                          │  │
│  │  @router.get("/")                                       │  │
│  │  @router.get("/src/{path:path}")                        │  │
│  │  @router.get("/assets/{path:path}")                     │  │
│  │  @router.post("/generate")                              │  │
│  │  ... 9+ endpoints                                       │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Router: avatar_v1.py                           │  │
│  │                                                          │  │
│  │  /avatar/v1/render                                      │  │
│  │  /avatar/v1/lipsync                                     │  │
│  │  /avatar/v1/emotions                                    │  │
│  │  ... 20+ endpoints                                      │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔴 Problem: Duplicate Endpoints Flow

```
User Request: GET /api/v1/voices
│
├─ FastAPI Router checks registered routes
│
├─ Route 1: voice_router.get("/api/v1/voices")
│  └─ Defined in: services/avatar-service/app/routes/voice_routes.py (line 34)
│  └─ Handler: list_available_voices()
│  └─ Response Model: VoiceListResponse
│
└─ Route 2: app.get("/api/v1/voices")  ← FALLBACK (shouldn't be here)
   └─ Defined in: services/avatar-service/main.py (line 332)
   └─ Handler: list_available_voices_endpoint()
   └─ Response Model: VoiceListResponse

Result: Both routes registered → OpenAPI schema shows duplicate
```

---

## ✅ Solution: Correct Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application (Port 8012)              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app = FastAPI(...)                                      │  │
│  │                                                          │  │
│  │  # Only service-level endpoints in main.py              │  │
│  │  @app.get("/")              ─────┐                       │  │
│  │  @app.get("/ping")          ─────┼─ Service Level       │  │
│  │  @app.get("/health")        ─────┤ Only!                │  │
│  │  @app.post("/render/lipsync")────┘                       │  │
│  │                                                          │  │
│  │  # Include routers (all endpoints from routers)         │  │
│  │  app.include_router(avatar_router)                       │  │
│  │  app.include_router(avatar_v1_router)                    │  │
│  │  app.include_router(voice_router)  ← Endpoints here!    │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Router: voice_routes.py                     │  │
│  │                                                          │  │
│  │  @router.post("/api/v1/generate-voice")  ✅ PRIMARY     │  │
│  │  @router.get("/api/v1/voices")            ✅ PRIMARY    │  │
│  │                                                          │  │
│  │  Registered in app via include_router()                 │  │
│  │  ├─ POST /api/v1/generate-voice = 1 copy               │  │
│  │  └─ GET /api/v1/voices = 1 copy                        │  │
│  │                                                          │  │
│  │  (No duplicates!)                                       │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

DELETE LINES 323-334 FROM main.py:
┌─────────────────────┐
│ if VOICE_MODULES... │  ← This entire if block
│   @app.post()       │  ← These are the fallbacks
│   @app.get()        │  ← They duplicate the router
│ else:               │  ← Remove all of this
│   logger.warning()  │
└─────────────────────┘
```

---

## 📊 Endpoint Count Before/After Fix

```
BEFORE FIX (Current):
═══════════════════════════════════════════════════════════
Total Registered: 16 routes
Unique Paths: ~12

GET      /                  [from main.py]
GET      /                  [from voice_router] ← DUPLICATE
GET      /health            [from main.py]
GET      /health            [from voice_router] ← DUPLICATE
GET      /health            [from avatar_router] ← DUPLICATE
POST     /api/v1/generate-voice [from main.py] ← DUPLICATE
POST     /api/v1/generate-voice [from voice_router]
GET      /api/v1/voices [from main.py] ← DUPLICATE
GET      /api/v1/voices [from voice_router]
POST     /render/lipsync    [from main.py]
GET      /ping              [from main.py]
... other avatar endpoints ...

DUPLICATES:
❌ GET / (2 times)
❌ GET /health (3 times!)
❌ POST /api/v1/generate-voice (2 times)
❌ GET /api/v1/voices (2 times)

═══════════════════════════════════════════════════════════

AFTER FIX (Expected):
═══════════════════════════════════════════════════════════
Total Registered: 12 routes
Unique Paths: 12

GET      /                  [from main.py]
GET      /health            [from main.py]
POST     /api/v1/generate-voice [from voice_router]
GET      /api/v1/voices [from voice_router]
POST     /render/lipsync    [from main.py]
GET      /ping              [from main.py]
... other avatar endpoints ...

DUPLICATES: 0 ✅

═══════════════════════════════════════════════════════════
```

---

## 🔄 Request Flow: Before vs After

```
REQUEST: POST /api/v1/generate-voice
WITH: { "text": "Hello, world!" }

BEFORE (Current - PROBLEMATIC):
┌─────────────────────────────────┐
│ FastAPI Router Lookup           │
├─────────────────────────────────┤
│ Route 1 Match: voice_router      │
│ └─ Handler: generate_us_voice()  │
│    └─ Response: ✅ Works         │
│                                 │
│ Route 2 Match: app fallback      │
│ └─ Handler: generate_us_voice()  │ ← Same handler but different
│    └─ Response: ✅ Works         │      location (confusing!)
│                                 │
│ OpenAPI Schema includes BOTH     │
│ Developers see: "Wait, why       │
│ is this endpoint listed twice?"  │
└─────────────────────────────────┘

AFTER (Fixed - CORRECT):
┌─────────────────────────────────┐
│ FastAPI Router Lookup           │
├─────────────────────────────────┤
│ Route Match: voice_router       │
│ └─ Handler: generate_us_voice()  │
│    └─ Response: ✅ Works         │
│                                 │
│ OpenAPI Schema includes ONCE     │
│ Developers see: Clear!           │
│ This is the one endpoint         │
└─────────────────────────────────┘
```

---

## 🗂️ File Structure & Dependencies

```
services/avatar-service/
│
├── main.py
│   ├── Lines 1-100: Imports & config
│   ├── Lines 100-155: create_app() + router includes
│   ├── Lines 155-260: Service endpoints (✅ KEEP)
│   ├── Lines 261-265: POST /render/lipsync (✅ KEEP)
│   │
│   └── Lines 323-334: ❌ DELETE (fallback voice endpoints)
│       ├── if VOICE_MODULES_AVAILABLE:
│       │   └── @app.post("/api/v1/generate-voice")  ← REMOVE
│       │   └── @app.get("/api/v1/voices")           ← REMOVE
│       └── else:
│           └── logger.warning(...)
│
├── app/
│   ├── models/
│   │   └── voice.py
│   │       └── VoiceRequest, VoiceResponse, etc.
│   │
│   ├── services/
│   │   └── voice_service.py
│   │       └── VoiceService (implements handlers)
│   │
│   └── routes/
│       ├── voice_routes.py (✅ PRIMARY)
│       │   └── @router.post("/api/v1/generate-voice")  ← KEEP
│       │   └── @router.get("/api/v1/voices")           ← KEEP
│       │
│       ├── avatar_routes.py (✅ KEEP)
│       │   └── Multiple avatar endpoints
│       │
│       └── avatar_v1.py (✅ KEEP)
│           └── 20+ advanced avatar endpoints
│
└── ENDPOINT_SPECIFICATION.md (New - Reference)
```

---

## 🔗 Router Inclusion Pattern

```
CORRECT PATTERN (What you need):
════════════════════════════════════════════════════════════

Step 1: Define endpoints in router file
┌────────────────────────────────────────────────────────┐
│ services/avatar-service/app/routes/voice_routes.py     │
│                                                        │
│ from fastapi import APIRouter                          │
│ router = APIRouter()                                   │
│                                                        │
│ @router.post("/api/v1/generate-voice")                │
│ async def generate_us_voice(request: VoiceRequest):   │
│     return await voice_service.generate_us_voice()    │
│                                                        │
│ @router.get("/api/v1/voices")                         │
│ async def list_available_voices():                     │
│     return await voice_service.list_available_voices() │
└────────────────────────────────────────────────────────┘

Step 2: Include router in main app
┌────────────────────────────────────────────────────────┐
│ services/avatar-service/main.py                        │
│                                                        │
│ app = FastAPI()                                        │
│                                                        │
│ from app.routes.voice_routes import router as voice_  │
│ app.include_router(voice_router)                       │
│                                                        │
│ # Endpoints from router are now available:            │
│ # - POST /api/v1/generate-voice                      │
│ # - GET /api/v1/voices                               │
└────────────────────────────────────────────────────────┘

Step 3: Do NOT re-define in main.py
┌────────────────────────────────────────────────────────┐
│ ❌ WRONG - What's currently happening:                 │
│                                                        │
│ app = FastAPI()                                        │
│ app.include_router(voice_router)                       │
│                                                        │
│ if VOICE_MODULES_AVAILABLE:                           │
│     # Defining again here = DUPLICATION                │
│     @app.post("/api/v1/generate-voice")               │
│     @app.get("/api/v1/voices")                        │
│                                                        │
│ DELETE THE FALLBACK BLOCK!                            │
└────────────────────────────────────────────────────────┘

Result:
✅ Endpoints defined in ONE place: voice_routes.py
✅ Endpoints included in ONE way: app.include_router()
✅ No duplicates
✅ Clear ownership (voice_routes.py is source of truth)
```

---

## 📋 Decision Tree: When to Use What

```
Do I have a simple endpoint?
│
├─ YES, it's service-level (health, ping, root)
│  └─ Define in main.py directly
│     └─ Examples: GET /, GET /health, GET /ping
│
└─ NO, it's a feature endpoint
   └─ Define in a router file
      └─ Examples: POST /api/v1/generate-voice, GET /api/v1/voices
      └─ Then: app.include_router(my_router)
      └─ DO NOT re-define in main.py!
```

---

## ✅ Checklist: After Applying Fix

```
□ Deleted lines 323-334 from main.py
□ Did NOT delete anything else
□ Service still starts: uvicorn services.avatar-service.main:app
□ Endpoints still work:
  □ curl http://localhost:8012/api/v1/voices
  □ curl http://localhost:8012/health
  □ curl http://localhost:8012/ping
□ No duplicates in /api-docs:
  curl -s http://localhost:8012/api-docs | grep 'POST.*generate-voice'
  (should appear once, not twice)
□ Tests pass: pytest services/avatar-service/
□ Updated ENDPOINT_DUPLICATION_TRACKING.md change log
```

---

**Diagram Version:** 1.0  
**Created:** December 17, 2025  
**Purpose:** Visual reference for understanding and fixing duplicate endpoints
