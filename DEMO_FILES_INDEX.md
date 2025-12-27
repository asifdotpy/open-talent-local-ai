# Demo Files Index - Complete Reference

**Last Updated:** December 27, 2025
**Purpose:** Comprehensive index of all files needed to understand and run the OpenTalent demo

---

## 📋 Quick Navigation

- [Demo Setup Files](#demo-setup-files)
- [Documentation Files](#documentation-files)
- [Service Configuration](#service-configuration)
- [Startup Scripts](#startup-scripts)
- [Architecture Documentation](#architecture-documentation)

---

## 🚀 Demo Setup Files

### Primary Demo Scripts (Root Directory)

| File | Purpose | Location |
|------|---------|----------|
| `start-demo.sh` | **Main startup script** - Starts minimal demo (4 services) | `/home/asif1/open-talent/start-demo.sh` |
| `stop-demo.sh` | Stop all demo services | `/home/asif1/open-talent/stop-demo.sh` |
| `demo-client.sh` | Demo client script | `/home/asif1/open-talent/demo-client.sh` |
| `deploy-demo.sh` | Demo deployment script | `/home/asif1/open-talent/deploy-demo.sh` |

### Main Documentation (Root Directory)

| File | Purpose | Location |
|------|---------|----------|
| `README.md` | **Main project README** - Includes demo instructions | `/home/asif1/open-talent/README.md` |
| `DEMO_SERVICES_COMPLETE_GUIDE.md` | **NEW** - Complete guide to all services | `/home/asif1/open-talent/DEMO_SERVICES_COMPLETE_GUIDE.md` |

---

## 📚 Documentation Files

### Demo Documentation (Root Directory)

| File | Purpose | Location |
|------|---------|----------|
| `DEMO_ENVIRONMENT_GUIDE.md` | Complete demo setup guide | Referenced in README but check `internal/docs/` |
| `DEMO_QUICK_REFERENCE.md` | Quick reference commands | Referenced in README but check `internal/docs/` |

### Internal Documentation (`internal/docs/`)

| File | Purpose | Location |
|------|---------|----------|
| `DEMO_ENVIRONMENT_GUIDE.md` | **Complete demo setup and troubleshooting** | `internal/docs/DEMO_ENVIRONMENT_GUIDE.md` |
| `DEMO_QUICK_REFERENCE.md` | **Quick commands and demo script** | `internal/docs/DEMO_QUICK_REFERENCE.md` |
| `START_DESKTOP_APP.md` | Desktop app startup guide | `internal/docs/START_DESKTOP_APP.md` |
| `INTEGRATION_SERVICE_ARCHITECTURE.md` | **Gateway architecture** - Shows all services | `internal/docs/INTEGRATION_SERVICE_ARCHITECTURE.md` |
| `PHASE_9_START_GUIDE.md` | Demo recording preparation | `internal/docs/PHASE_9_START_GUIDE.md` |
| `PHASE_9_DEMO_RECORDING_PLAN.md` | Demo recording plan | `internal/docs/PHASE_9_DEMO_RECORDING_PLAN.md` |
| `PHASE_9_DEMO_SCENARIOS.md` | Demo scenarios | `internal/docs/PHASE_9_DEMO_SCENARIOS.md` |
| `QUICK_START_DEC14.md` | Quick start guide | `internal/docs/QUICK_START_DEC14.md` |
| `MICROSERVICES_QUICK_START.md` | Microservices quick start | `internal/docs/MICROSERVICES_QUICK_START.md` |

---

## 🏗️ Service Configuration

### Service Directories Structure

```
open-talent/
├── microservices/          # Main microservices (used by demo)
│   ├── analytics-service/
│   │   └── start.sh       # Start script
│   ├── desktop-integration-service/  # Gateway (port 8009)
│   │   └── start.sh       # Start script
│   ├── granite-interview-service/    # Port 8000
│   │   └── start.sh       # Start script
│   ├── avatar-service/    # Port 8001
│   ├── voice-service/     # Port 8002
│   ├── conversation-service/  # Port 8003
│   └── interview-service/ # Port 8004
│       └── start_ai_services.sh
│
├── services/               # Alternative services location
│   └── [similar structure]
│
└── desktop-app/           # Desktop application
    └── package.json       # npm run dev
```

### Service Ports Reference

| Service | Port | Location | Start Script |
|---------|------|----------|--------------|
| **Ollama** | 11434 | System | `ollama serve` |
| **Granite Interview Service** | 8000 | `microservices/granite-interview-service` | `./start.sh` |
| **Avatar Service** | 8001 | `microservices/avatar-service` | `./start.sh` |
| **Voice Service** | 8002 | `microservices/voice-service` | `./start.sh` |
| **Conversation Service** | 8003 | `microservices/conversation-service` | `./start.sh` |
| **Interview Service** | 8004 | `microservices/interview-service` | `./start_ai_services.sh` |
| **Analytics Service** | 8007 | `microservices/analytics-service` | `./start.sh` |
| **Gateway Service** | 8009 | `microservices/desktop-integration-service` | `./start.sh` |
| **Desktop App** | 3000 | `desktop-app` | `npm run dev` |

---

## 🎯 Startup Scripts

### Individual Service Start Scripts

Located in each service directory:

```bash
# Granite Interview Service
microservices/granite-interview-service/start.sh

# Avatar Service
microservices/avatar-service/start.sh  # (if exists)

# Voice Service
microservices/voice-service/start.sh  # (if exists)

# Conversation Service
microservices/conversation-service/start.sh  # (if exists)

# Interview Service
microservices/interview-service/start_ai_services.sh

# Analytics Service
microservices/analytics-service/start.sh

# Gateway Service
microservices/desktop-integration-service/start.sh
```

---

## 📖 Architecture Documentation

### Key Architecture Files

| File | Content | Location |
|------|---------|----------|
| `INTEGRATION_SERVICE_ARCHITECTURE.md` | **Gateway architecture** - Shows all services and ports | `internal/docs/INTEGRATION_SERVICE_ARCHITECTURE.md` |
| `AGENTS.md` | Project architecture overview | Root directory |
| `LOCAL_AI_ARCHITECTURE.md` | Local AI architecture spec | Root directory |
| `CONTRIBUTING.md` | Development standards | Root directory |

---

## 🔍 Finding Documentation

### Search Commands

```bash
# Find all demo-related markdown files
find . -name "*demo*.md" -type f

# Find all start scripts
find . -name "start*.sh" -type f

# Find documentation about services
grep -r "service\|Service" internal/docs/*.md | grep -i "port\|800"

# Find architecture diagrams
grep -r "architecture\|Architecture" internal/docs/*.md
```

---

## 📊 Current Demo Status

### ✅ Currently Started (via start-demo.sh)

1. Ollama (11434)
2. Analytics Service (8007)
3. Gateway Service (8009)
4. Desktop App (3000)

### ❌ NOT Started (But Available)

1. Granite Interview Service (8000)
2. Avatar Service (8001)
3. Voice Service (8002)
4. Conversation Service (8003)
5. Interview Service (8004)

### ⚠️ Impact

- Gateway uses **fallback templates** when services are offline
- Limited functionality in current demo
- Missing voice, avatar, and enhanced conversation features

---

## 🎬 Recommended Reading Order

### For Quick Demo Setup

1. `README.md` - Start here
2. `DEMO_SERVICES_COMPLETE_GUIDE.md` - Understand all services
3. `internal/docs/DEMO_QUICK_REFERENCE.md` - Quick commands
4. `start-demo.sh` - Review startup script

### For Full Understanding

1. `internal/docs/INTEGRATION_SERVICE_ARCHITECTURE.md` - Architecture overview
2. `internal/docs/DEMO_ENVIRONMENT_GUIDE.md` - Complete setup guide
3. `internal/docs/START_DESKTOP_APP.md` - Desktop app details
4. `DEMO_SERVICES_COMPLETE_GUIDE.md` - All services guide

### For Development

1. `AGENTS.md` - Project architecture
2. `LOCAL_AI_ARCHITECTURE.md` - AI architecture
3. `CONTRIBUTING.md` - Development standards
4. Individual service README files

---

## 📝 Summary

### Critical Files to Review Before Demo

1. ✅ **`DEMO_SERVICES_COMPLETE_GUIDE.md`** - Complete services overview (NEW)
2. ✅ **`internal/docs/DEMO_ENVIRONMENT_GUIDE.md`** - Setup guide
3. ✅ **`internal/docs/INTEGRATION_SERVICE_ARCHITECTURE.md`** - Architecture
4. ✅ **`start-demo.sh`** - Current startup script
5. ✅ **`README.md`** - Project overview

### Key Findings

- **Current demo is minimal** - Only 4 services started
- **6+ services are available but not started**
- **Gateway has fallback behavior** when services offline
- **Enhanced startup script needed** for full functionality

---

**Next Steps:** Create enhanced startup script (`start-demo-complete.sh`) that starts all services.
