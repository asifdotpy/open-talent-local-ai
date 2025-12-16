# 📋 Next Service Priority - Decision Matrix (December 14, 2025)

## Current Status

**Completed Services:**
- ✅ Security Service (Port 8010): 18 endpoints, all tests passing, production-ready
- ✅ Notification Service (Port 8011): 6 endpoints, modular providers (Novu + Apprise fallback)

**Total Endpoints:** 143/250 (57% complete)
**Remaining Gap:** ~107 endpoints (43%)

---

## 🎯 Three Options for Next Service

### Option 1: User Service (Port 8001) - RECOMMENDED
**Category:** Core Platform Feature  
**Criticality:** 🔴 CRITICAL (blocks recruiter/candidate onboarding)  
**Effort:** ~40 hours  
**Business Impact:** HIGH (enables user workflows immediately)

**Current State:**
- Implemented: 3-9 endpoints (basic CRUD)
- Missing: 16+ endpoints
- Status: Partially functional

**Missing Endpoints (16+):**
```
Core CRUD Operations:
- GET    /api/v1/users                  - List all users (with filters)
- GET    /api/v1/users/{id}             - Get user by ID
- PUT    /api/v1/users/{id}             - Update user
- DELETE /api/v1/users/{id}             - Delete user

Profile Management:
- GET    /api/v1/users/{id}/profile     - Get user profile (extended info)
- PUT    /api/v1/users/{id}/profile     - Update profile
- POST   /api/v1/users/{id}/avatar      - Upload avatar
- DELETE /api/v1/users/{id}/avatar      - Delete avatar

Preferences & Settings:
- GET    /api/v1/users/{id}/preferences - Get user preferences
- PUT    /api/v1/users/{id}/preferences - Update preferences
- GET    /api/v1/users/{id}/notifications - Get notification settings
- PUT    /api/v1/users/{id}/notifications - Update notification settings

Activity & Search:
- GET    /api/v1/users/search           - Search users (by email, name, role)
- GET    /api/v1/users/{id}/activity    - Get user activity history
- POST   /api/v1/users/bulk-import      - Bulk import users (CSV)
- GET    /api/v1/users/export           - Export users list
```

**Why This First:**
1. **Unblocks Core Workflows:** Without user management, can't onboard recruiters or candidates
2. **Foundation for Others:** Interview Service, Candidate Service, and Scout Service all depend on User Service
3. **Quick Win:** ~40 hours for solid implementation
4. **Measurable:** Clear CRUD operations, easy to test

**Risk:** LOW - Standard CRUD patterns, proven technologies

---

### Option 2: AI Auditing Service (Port 8012) - COMPLIANCE CRITICAL
**Category:** Legal & Ethical Compliance  
**Criticality:** 🔴 CRITICAL (legal requirement for AI hiring)  
**Effort:** ~40 hours  
**Business Impact:** COMPLIANCE (enables GDPR/EEO/CCPA compliance)

**Current State:**
- Implemented: 2 endpoints (/, /health)
- Missing: 13+ endpoints
- Status: Placeholder only

**Missing Endpoints (13+):**
```
Bias Detection:
- POST   /api/v1/audit/analyze-bias     - Detect demographic parity issues
- GET    /api/v1/audit/bias-report      - Get bias detection report
- POST   /api/v1/audit/fairness-metrics - Calculate fairness metrics

Explainability:
- POST   /api/v1/audit/explain          - Explain decision for candidate
- GET    /api/v1/audit/transparency     - Get transparency score

Compliance Reporting:
- POST   /api/v1/audit/compliance-check - Check GDPR/CCPA/EEO compliance
- GET    /api/v1/audit/compliance-report - Generate compliance report
- POST   /api/v1/audit/audit-trail      - Log decision audit trail

Model Governance:
- GET    /api/v1/audit/model-cards      - Get model documentation
- POST   /api/v1/audit/model-cards      - Update model documentation
- POST   /api/v1/audit/validate-model   - Validate model safety
```

**Why This Second:**
1. **Legal Requirement:** AI hiring without bias detection = legal liability
2. **Market Differentiator:** Many AI hiring platforms lack bias detection
3. **Integrates with Interview Service:** Can audit interview results
4. **Enables AI Ethics Board:** Transparency for stakeholders

**Risk:** MEDIUM - Requires understanding of fairness metrics (but we can use open-source AIF360)

---

### Option 3: Enhance Interview Service (Port 8005) - FEATURE EXPANSION
**Category:** Core Feature Enhancement  
**Criticality:** 🟡 HIGH (core platform feature)  
**Effort:** ~30 hours  
**Business Impact:** MEDIUM (improves interview experience)

**Current State:**
- Implemented: 10+ endpoints (basic interview CRUD)
- Missing: 20+ endpoints
- Status: Functional but incomplete

**Missing Endpoints (20+):**
```
Room Management:
- POST   /api/v1/interviews/{id}/room    - Create interview room
- GET    /api/v1/interviews/{id}/room    - Get room details
- POST   /api/v1/interviews/{id}/join    - Join interview room
- DELETE /api/v1/interviews/{id}/room    - Delete room

Questions & Evaluation:
- GET    /api/v1/interviews/{id}/questions - Get interview questions
- POST   /api/v1/interviews/{id}/questions - Add question
- POST   /api/v1/interviews/{id}/evaluate  - Submit evaluation
- GET    /api/v1/interviews/{id}/score     - Get interview score

Recording & Transcription:
- POST   /api/v1/interviews/{id}/record   - Start recording
- GET    /api/v1/interviews/{id}/transcript - Get transcript
- POST   /api/v1/interviews/{id}/summary   - Generate summary

Scheduling & Notifications:
- POST   /api/v1/interviews/schedule       - Schedule interview
- POST   /api/v1/interviews/reschedule     - Reschedule interview
- POST   /api/v1/interviews/cancel         - Cancel interview
- POST   /api/v1/interviews/notify         - Send interview reminder
```

**Why This Third:**
1. **Complete Core Feature:** Interview platform needs full interview lifecycle
2. **User-Facing Impact:** Better interview experience = better hiring outcomes
3. **Integrates with Notification Service:** Auto-send reminders
4. **Depends on User Service:** Need users first

**Risk:** MEDIUM - Requires real-time room coordination (WebSocket)

---

## 📊 Comparison Matrix

| Factor | User Service | AI Auditing | Interview Enhancement |
|--------|---|---|---|
| **Business Impact** | 🔴 CRITICAL | 🔴 CRITICAL | 🟡 HIGH |
| **Time Estimate** | 40 hours | 40 hours | 30 hours |
| **Complexity** | Simple (CRUD) | Medium (ML fairness) | Medium (real-time) |
| **Dependencies** | None | User Service | User Service |
| **Unblocks** | Most features | Compliance | Interview features |
| **ROI** | Immediate | Compliance ROI | Experience ROI |
| **Market Fit** | Table stakes | Differentiator | Table stakes |

---

## 🏆 RECOMMENDATION: Build User Service Next

### Rationale:
1. **Foundation First:** User Service is dependency for 80% of other services
2. **Measurable Progress:** Clear CRUD endpoints, easy to validate
3. **Low Risk:** Well-established patterns, standard database operations
4. **Quick Wins:** Can deploy incrementally (users, then profiles, then preferences)
5. **Enables AI Auditing Later:** After User Service, AI Auditing becomes natural next step

### Timeline:
- **Days 1-2:** User CRUD (GET/POST/PUT/DELETE) + search/filter
- **Days 3-4:** Profile & avatar management
- **Days 5:** Preferences & settings
- **Days 6:** Activity history + bulk import
- **Day 7:** Testing & optimization

### Success Criteria:
- ✅ 16+ endpoints implemented
- ✅ Full CRUD operations tested
- ✅ Search/filter working
- ✅ User roles integrated with Security Service
- ✅ All tests passing (target: 25+ tests)
- ✅ Integration with other services (reference in Candidate Service, etc.)

---

## 🚀 Execution Plan for User Service

### Step 1: Database Schema
```python
# Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role ENUM('admin', 'recruiter', 'candidate', 'hiring_manager'),
    status ENUM('active', 'inactive', 'suspended'),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP
)

# User profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    bio TEXT,
    phone VARCHAR(20),
    location VARCHAR(255),
    company VARCHAR(255),
    job_title VARCHAR(255),
    avatar_url VARCHAR(500),
    avatar_uploaded_at TIMESTAMP
)

# User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    notification_email BOOLEAN,
    notification_sms BOOLEAN,
    notification_push BOOLEAN,
    theme ENUM('light', 'dark'),
    language VARCHAR(10)
)

# Activity log table
CREATE TABLE user_activity (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    action VARCHAR(100),
    resource VARCHAR(100),
    timestamp TIMESTAMP
)
```

### Step 2: FastAPI Service Structure
```
services/user-service/
├── main.py                    (600+ LOC)
│   ├── UserService (CRUD operations)
│   ├── ProfileService (profile management)
│   ├── PreferencesService (settings)
│   └── ActivityService (activity logging)
├── models.py
│   ├── User (Pydantic schema)
│   ├── UserProfile
│   ├── UserPreferences
│   └── UserActivity
├── database.py
│   └── SQLAlchemy ORM models
├── requirements.txt
│   ├── fastapi
│   ├── sqlalchemy
│   ├── pydantic
│   ├── python-multipart (file uploads)
│   └── pillow (image processing)
└── tests/
    ├── test_user_crud.py      (8+ tests)
    ├── test_user_profile.py   (5+ tests)
    ├── test_user_search.py    (4+ tests)
    └── test_user_activity.py  (3+ tests)
```

### Step 3: Key Features
- **CRUD:** Create, read, update, delete users
- **Search:** Filter by email, name, role, status
- **Profiles:** Extended user info (bio, location, job title, avatar)
- **Preferences:** Notification & UI settings
- **Activity:** Login history, action tracking
- **Bulk Import:** CSV upload for recruiter onboarding
- **Export:** Export user list with filters

### Step 4: Integration Points
- **Security Service:** Verify JWT tokens, check permissions
- **Notification Service:** Send welcome email, password reset, notifications
- **Candidate Service:** Reference user as recruiter/interviewer
- **Interview Service:** Track user participation in interviews
- **Scout Service:** Link recruiter to their candidates

---

## 📅 Proposed Schedule

| Date | Milestone | Effort | Status |
|------|-----------|--------|--------|
| **Dec 14** | ✅ Security Service Complete | Complete | ✅ DONE |
| **Dec 15-16** | User Service Design + CRUD | 16 hours | ✅ Scaffolding added (Supabase/Postgres + FastAPI + Alembic) |
| **Dec 17-18** | User Service Profiles + Search | 16 hours | Planned |
| **Dec 19** | User Service Testing + Integration | 8 hours | Planned |
| **Dec 20** | ✅ User Service Complete | | Planned |
| **Dec 21-27** | AI Auditing Service | 40 hours | Next phase |
| **Dec 28-31** | Interview Service Enhancements | 30 hours | |

---

## 🎓 Key Learnings Applied

From Security Service success:
1. **Test-First Development:** Write tests before implementation
2. **In-Process Testing:** Use ASGITransport for fast, reliable tests
3. **Environment Configuration:** Separate dev/test/prod via env vars
4. **Security Patterns:** Bcrypt + JWT + rate limiting from day 1
5. **Documentation:** Keep catalogs & gap analysis updated

---

## ✅ Decision Point

**Question:** Should we start User Service immediately, or wait for AI Auditing requirements?

**Answer:** **Start User Service immediately.** It's the foundation that unblocks everything else. AI Auditing can be parallelized after User Service is functional.

---

## 📞 Next Steps

1. ✅ **Approved:** User Service as next priority
2. 📋 **Ready:** Database schema + FastAPI structure
3. 🚀 **Action:** Create user-service repository, set up FastAPI project
4. 🧪 **Testing:** Write CRUD tests, verify integration with Security Service
5. 📊 **Documentation:** Update MICROSERVICES_API_INVENTORY.md as endpoints added

---

**Ready to begin User Service development on Day 15 (December 15)?**

**Status:** ✅ Decision made, architecture designed, ready for implementation.
