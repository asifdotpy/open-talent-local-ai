# Docker Compose Quick Start Guide

**Updated:** December 14, 2025
**Status:** ✅ Ready to Deploy

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Navigate to microservices directory
cd /home/asif1/open-talent/microservices

# 2. Start all services with docker compose
docker compose up -d

# 3. Verify services are running
./verify-services.sh
```

---

## 📋 What Each Command Does

### Step 1: Navigate to Microservices

```bash
cd /home/asif1/open-talent/microservices
```

- Changes to the directory containing `docker-compose.yml`
- All relative paths in docker-compose will be resolved from here

### Step 2: Start Services with Docker Compose

```bash
docker compose up -d
```

**Key Points:**

- Uses `docker compose` (not `docker-compose`) - modern Docker CLI
- `-d` flag runs containers in background (detached mode)
- Automatically:
  - Pulls latest images
  - Builds services from Dockerfile
  - Creates volumes and networks
  - Starts services with proper dependencies
  - Applies health checks

**Expected Output:**

```
[+] Running 14/14
 ✓ Network OpenTalent-network  Created                                          0.3s
 ✓ Container talent-ollama    Started                                          1.2s
 ✓ Container talent-conversation-service  Started                             3.5s
 ✓ Container talent-interview-service     Started                             2.1s
 ✓ Container talent-scout-service         Started                             2.3s
 ✓ Container talent-user-service          Started                             2.2s
 ✓ Container talent-candidate-service     Started                             2.4s
 ✓ Container talent-analytics-service     Started                             2.3s
 ✓ Container talent-desktop-integration   Started                             2.5s
 ✓ Container talent-security-service      Started                             2.1s
 ✓ Container talent-notification-service  Started                             2.2s
 ✓ Container open-talent-auditing-service   Started                             2.3s
 ✓ Container talent-explainability-service Started                             2.2s
```

### Step 3: Verify Services are Online

```bash
./verify-services.sh
```

**What It Tests:**

1. **Port Connectivity** - All 14 services responding on their ports
2. **Health Endpoints** - Service-specific /health checks
3. **Functional Tests** - Model availability, API endpoints
4. **Dependencies** - Service-to-service communication
5. **Performance** - Response times (baseline)

**Example Output:**

```
[INFO] Pre-flight checks...
[✓ PASS] Docker is installed
[✓ PASS] docker compose is available
...
[✓ PASS] Scout Service is responding on port 8000
[✓ PASS] Avatar Service is responding on port 8004
...
✓ Passed:     56
✗ Failed:     0
⚠ Warnings:   2
```

---

## 🔍 Service Port Mapping

| Service | Port | Container Port | Status |
|---------|------|----------------|--------|
| **Ollama** | 11434 | 11434 | Base dependency |
| **Scout** | 8000 | 8000 | Agent orchestrator |
| **User** | 8001 | 80 | Authentication |
| **Conversation** | 8002 | 80 | Granite AI |
| **Voice** | 8003 | 8003 | TTS (Py3.12) |
| **Avatar** | 8004 | 80 | Rendering (Py3.12) |
| **Interview** | 8005 | 80 | Interview mgmt |
| **Candidate** | 8006 | 8000 | Candidate data |
| **Analytics** | 8007 | 80 | Analytics |
| **Desktop Gateway** | 8009 | 8009 | Service aggregation |
| **Security** | 8010 | 80 | Security |
| **Notification** | 8011 | 80 | Notifications |
| **AI Auditing** | 8012 | 80 | Auditing |
| **Explainability** | 8013 | 80 | Explainability |

---

## 📊 Service Dependencies

```
Ollama (foundation)
  ├── Conversation Service
  │   ├── Interview Service
  │   ├── Analytics Service
  │   └── Scout Service
  └── Desktop Integration Gateway
      ├── All services
      └── Service health aggregation
```

---

## 🛠️ Common Commands

### View Running Services

```bash
docker compose ps
```

### View Service Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f conversation-service

# Last 100 lines
docker compose logs --tail=100 conversation-service
```

### Stop Services

```bash
# Stop (keep containers)
docker compose stop

# Stop specific service
docker compose stop interview-service
```

### Stop & Remove Everything

```bash
# Remove containers but keep volumes
docker compose down

# Remove containers AND volumes
docker compose down -v
```

### Restart a Service

```bash
docker compose restart interview-service
```

### Rebuild a Service

```bash
docker compose up -d --build conversation-service
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs <service-name>

# Rebuild the image
docker compose up -d --build <service-name>

# Check resource constraints
docker stats
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :<port-number>

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml and rebuild
```

### Network Issues

```bash
# Check network
docker network inspect OpenTalent-network

# Services can't reach each other:
# Make sure hostname matches service name in docker-compose.yml
# e.g., http://conversation-service:80 (not localhost:8002)
```

### Ollama Model Not Downloading

```bash
# Check Ollama logs
docker compose logs ollama

# Manually pull model
docker compose exec ollama ollama pull granite4:350m-h

# List available models
docker compose exec ollama ollama list
```

### Verification Script Fails

```bash
# Run with verbose output
bash -x ./verify-services.sh

# Check individual services
curl http://localhost:11434/api/tags
curl http://localhost:8009/health
curl http://localhost:8000/health
```

---

## 📈 Performance Expectations

| Metric | Target | Typical |
|--------|--------|---------|
| Services start time | <30s | 15-20s |
| Ollama model load | <60s | 30-45s |
| Gateway health check | <100ms | 50-80ms |
| Granite response time | <5s | 2-3s |
| All services online | <2 min | 60-90s |

---

## 🔌 API Endpoints After Startup

### Gateway (Single Entry Point)

```
http://localhost:8009/health          # Health status
http://localhost:8009/api/v1/models   # Available models
http://localhost:8009/api/v1/interviews/start  # Start interview
```

### Individual Services

```
http://localhost:11434/api/tags              # Ollama models
http://localhost:8000/health                 # Scout
http://localhost:8001/health                 # User
http://localhost:8002/health                 # Conversation
http://localhost:8003/health                 # Voice
http://localhost:8004/health                 # Avatar
http://localhost:8005/health                 # Interview
http://localhost:8006/health                 # Candidate
http://localhost:8007/health                 # Analytics
http://localhost:8010/health                 # Security
http://localhost:8011/health                 # Notification
http://localhost:8012/health                 # AI Auditing
http://localhost:8013/health                 # Explainability
```

---

## 🎯 Next Steps

After services are running:

1. **Verify with Script**

   ```bash
   ./verify-services.sh
   ```

2. **Reload Desktop App**

   ```bash
   cd /home/asif1/open-talent/desktop-app
   npm run dev
   ```

3. **Check ServiceStatus Header**
   - Should show "Online" instead of "Offline"
   - Should display service count (e.g., "9/14 online")

4. **Test Interview Flow**
   - Fill out interview form
   - Click "Start Interview"
   - Verify conversation with Granite AI
   - Check results generation

5. **Monitor Logs During Test**

   ```bash
   # In separate terminal
   docker compose logs -f
   ```

---

## 📝 Configuration Files

### Main Configuration

- `docker-compose.yml` - Service definitions, ports, volumes, networks
- Dockerfile in each service directory - Container image definitions
- `.env` files (optional) - Environment variable overrides

### Key Environment Variables

```yaml
PYTHONPATH: /app                           # Python import path
OLLAMA_HOST: http://ollama:11434           # Ollama endpoint
CONVERSATION_SERVICE_URL: http://conversation-service:80
INTERVIEW_SERVICE_URL: http://interview-service:80
GATEWAY_HOST: 0.0.0.0
GATEWAY_PORT: 8009
```

---

## 🚨 Emergency Commands

### Kill All Services

```bash
docker compose down -v --remove-orphans
```

### Clean Everything (Fresh Start)

```bash
docker compose down -v
docker system prune -a --volumes
docker compose up -d
```

### Full System Reset

```bash
# Kill docker daemon
sudo systemctl restart docker

# Start fresh
docker compose down -v
docker compose up -d
```

---

## 📞 Support

### Check Status

- Run `./verify-services.sh` to see what's working
- Check `docker compose logs` for error messages
- Use `docker compose ps` to see container states

### Debug Individual Service

```bash
docker compose logs <service-name> --tail=50
docker compose exec <service-name> /bin/bash
```

### Review Configuration

```bash
docker inspect <container-name>
docker network inspect OpenTalent-network
```

---

**Status:** ✅ Ready to Deploy
**Last Updated:** December 14, 2025
**Verified with:** Docker 24.0+, docker compose 2.20+
