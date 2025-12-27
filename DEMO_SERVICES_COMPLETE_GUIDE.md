# Complete Demo Services Guide

**Last Updated:** December 27, 2025
**Purpose:** Comprehensive guide to all services needed for OpenTalent demo

---

## 📊 Current State Analysis

### What `start-demo.sh` Currently Starts (MINIMAL)

The current `start-demo.sh` script only starts **4 services**:

1. **Ollama** (Port 11434) - AI model server
2. **Analytics Service** (Port 8007) - Sentiment & quality analysis
3. **Desktop Integration Service/Gateway** (Port 8009) - API Gateway
4. **Desktop App** (Port 3000) - React/Electron UI

### What Services SHOULD Be Running (COMPLETE)

Based on the architecture documentation, the Gateway (port 8009) connects to **11+ microservices**. Currently, most services are NOT being started, so the demo relies on fallback/template responses.

---

## 🏗️ Complete Service Architecture

### Core Services (Currently Started)

| Service | Port | Status | Location | Start Command |
|---------|------|--------|----------|---------------|
| **Ollama** | 11434 | ✅ Started | System | `ollama serve` |
| **Analytics Service** | 8007 | ✅ Started | `microservices/analytics-service` | `./start.sh` |
| **Gateway Service** | 8009 | ✅ Started | `microservices/desktop-integration-service` | `./start.sh` |
| **Desktop App** | 3000 | ✅ Started | `desktop-app` | `npm run dev` |

### Missing Microservices (NOT Currently Started)

| Service | Port | Location | Start Command | Purpose |
|---------|------|----------|---------------|---------|
| **Granite Interview Service** | 8000 | `microservices/granite-interview-service` | `./start.sh` | Trained AI for job interviews |
| **Avatar Service** | 8001 | `microservices/avatar-service` | `./start.sh` | 3D rendering & lip-sync |
| **Voice Service** | 8002 | `microservices/voice-service` | `./start.sh` | STT/TTS processing |
| **Conversation Service** | 8003 | `microservices/conversation-service` | `./start.sh` | Conversation orchestration |
| **Interview Service** | 8004 | `microservices/interview-service` | `./start.sh` | Interview orchestrator |
| **Analytics Service** | 8007 | ✅ Already started | `microservices/analytics-service` | Metrics & reporting |

### Additional Services (Optional/Supporting)

| Service | Port | Location | Purpose |
|---------|------|----------|---------|
| **Candidate Service** | ? | `services/candidate-service` | Candidate management |
| **User Service** | ? | `services/user-service` | User management |
| **Security Service** | ? | `services/security-service` | Authentication |
| **Notification Service** | ? | `services/notification-service` | Notifications |
| **Scout Service** | ? | `services/scout-service` | Talent sourcing |

---

## 📋 Service Dependencies

### Gateway Service Discovery

The Gateway (port 8009) probes these services for health:

1. **Granite Interview Service** (8000) - Primary AI interview engine
2. **Conversation Service** (8003) - Conversation orchestration
3. **Voice Service** (8002) - Speech-to-text, text-to-speech
4. **Avatar Service** (8001) - 3D avatar rendering
5. **Interview Service** (8004) - Interview management
6. **Analytics Service** (8007) - Sentiment analysis & metrics
7. **Ollama** (11434) - Fallback AI model server

**Current Behavior:** Gateway uses fallback templates when services are offline.

---

## 🚀 Complete Startup Guide

### Option 1: Enhanced start-demo.sh (Recommended)

Create an enhanced startup script that starts all services. See `start-demo-complete.sh` (to be created).

### Option 2: Manual Startup (For Testing/Debugging)

#### Terminal 1: Ollama

```bash
ollama serve
```

#### Terminal 2: Granite Interview Service

```bash
cd microservices/granite-interview-service
./start.sh
# Health: http://localhost:8000/health
```

#### Terminal 3: Avatar Service

```bash
cd microservices/avatar-service
./start.sh
# Health: http://localhost:8001/health
```

#### Terminal 4: Voice Service

```bash
cd microservices/voice-service
./start.sh
# Health: http://localhost:8002/health
```

#### Terminal 5: Conversation Service

```bash
cd microservices/conversation-service
./start.sh
# Health: http://localhost:8003/health
```

#### Terminal 6: Interview Service

```bash
cd microservices/interview-service
./start.sh
# Health: http://localhost:8004/health
```

#### Terminal 7: Analytics Service

```bash
cd microservices/analytics-service
./start.sh
# Health: http://localhost:8007/health
```

#### Terminal 8: Gateway Service

```bash
cd microservices/desktop-integration-service
./start.sh
# Health: http://localhost:8009/health
# API Docs: http://localhost:8009/docs
```

#### Terminal 9: Desktop App

```bash
cd desktop-app
npm run dev
# UI: http://localhost:3000
```

---

## 🔍 Service Health Checks

### Quick Health Check Script

```bash
#!/bin/bash
# Check all services
echo "Checking OpenTalent Services..."
echo ""

services=(
    "Ollama:11434:/api/tags"
    "Granite Interview:8000:/health"
    "Avatar:8001:/health"
    "Voice:8002:/health"
    "Conversation:8003:/health"
    "Interview:8004:/health"
    "Analytics:8007:/health"
    "Gateway:8009:/health"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port path <<< "$service"
    if curl -s "http://localhost:$port$path" > /dev/null 2>&1; then
        echo "✅ $name (port $port) - ONLINE"
    else
        echo "❌ $name (port $port) - OFFLINE"
    fi
done
```

### Individual Health Checks

```bash
# Ollama
curl http://localhost:11434/api/tags

# Granite Interview Service
curl http://localhost:8000/health

# Avatar Service
curl http://localhost:8001/health

# Voice Service
curl http://localhost:8002/health

# Conversation Service
curl http://localhost:8003/health

# Interview Service
curl http://localhost:8004/health

# Analytics Service
curl http://localhost:8007/health

# Gateway Service
curl http://localhost:8009/health
```

---

## 📁 Key Documentation Files

### Demo Setup & Execution

- **`DEMO_ENVIRONMENT_GUIDE.md`** - Complete setup and troubleshooting guide
- **`DEMO_QUICK_REFERENCE.md`** - Quick commands and demo script
- **`start-demo.sh`** - Current startup script (minimal services)
- **`stop-demo.sh`** - Stop all services script

### Architecture & Integration

- **`internal/docs/INTEGRATION_SERVICE_ARCHITECTURE.md`** - Gateway architecture details
- **`internal/docs/START_DESKTOP_APP.md`** - Desktop app startup guide
- **`internal/docs/PHASE_9_START_GUIDE.md`** - Demo recording preparation

### Service-Specific Documentation

- Check individual service directories for README.md files
- API documentation available at `http://localhost:PORT/docs` for each service

---

## 🎯 Recommended Demo Scenarios

### Scenario 1: Minimal Demo (Current - Fallback Mode)

**Services:** Ollama + Analytics + Gateway + Desktop App
**Pros:** Fast startup, minimal resource usage
**Cons:** Uses template responses, limited functionality
**Use Case:** Quick demo, low-resource systems

### Scenario 2: Standard Demo (Recommended)

**Services:** All core services (8000-8009) + Desktop App
**Pros:** Full functionality, real AI responses, complete features
**Cons:** Higher resource usage, longer startup time
**Use Case:** Professional demos, full feature showcase

### Scenario 3: Complete Demo (All Services)

**Services:** All microservices + supporting services
**Pros:** Complete system demonstration
**Cons:** Very high resource usage, complex setup
**Use Case:** Development, testing, full system validation

---

## ⚠️ Current Limitations

1. **Most services not started** - Only 4 of 11+ services running
2. **Fallback mode** - Gateway uses templates when services offline
3. **Limited functionality** - Missing voice, avatar, conversation features
4. **No service orchestration** - Manual startup required for full demo

---

## 🔧 Next Steps

1. **Create enhanced startup script** - `start-demo-complete.sh` that starts all services
2. **Service dependency management** - Handle startup order and dependencies
3. **Health check automation** - Verify all services before starting next
4. **Docker Compose option** - Consider containerized deployment for all services
5. **Service discovery enhancement** - Better integration between services

---

## 📊 Resource Requirements

### Minimal (Current)

- **RAM:** 4-6GB
- **CPU:** 2 cores
- **Disk:** 2GB

### Standard (Recommended)

- **RAM:** 12-16GB
- **CPU:** 4 cores
- **Disk:** 5GB

### Complete (All Services)

- **RAM:** 16-32GB
- **CPU:** 8 cores
- **Disk:** 10GB

---

## 🎬 Demo Checklist

### Pre-Demo Setup

- [ ] All required services identified
- [ ] Service startup scripts verified
- [ ] Port conflicts resolved
- [ ] Health checks passing
- [ ] Desktop app dependencies installed

### During Demo

- [ ] Services started in correct order
- [ ] All health checks passing
- [ ] Gateway shows all services online
- [ ] Desktop app connects successfully
- [ ] Full interview flow works

### Post-Demo

- [ ] All services stopped cleanly
- [ ] Logs reviewed for errors
- [ ] Resource usage documented
- [ ] Issues logged for improvement

---

**Status:** Documentation Complete
**Action Required:** Create enhanced startup script for all services
