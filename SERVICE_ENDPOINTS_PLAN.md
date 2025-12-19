# OpenTalent Services - Complete Endpoint Extraction Plan

> **Last Updated:** December 17, 2025
> **Purpose:** Systematic guide to run each service and extract working endpoints from OpenAPI schemas

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Service Port Allocation](#service-port-allocation)
3. [Service-by-Service Instructions](#service-by-service-instructions)
4. [Endpoint Extraction Commands](#endpoint-extraction-commands)
5. [Automated Extraction Script](#automated-extraction-script)

---

## Prerequisites

### System Requirements
- Python 3.12+ with virtual environment
- Docker and Docker Compose (for some services)
- jq (JSON processor) - install: `sudo apt install jq`
- curl

### Setup
```bash
# Activate virtual environment
cd ~/open-talent
source .venv-1/bin/activate

# Verify tools
which jq curl
```

---

## Service Port Allocation

| Service | Port | Status | Protocol |
|---------|------|--------|----------|
| Avatar Service | 8001 | ✅ Ready | HTTP |
| User Service | 8001 | ✅ Ready | HTTP |
| Conversation Service | 8003 | ✅ Ready | HTTP |
| Interview Service | 8004 | ✅ Ready | HTTP |
| Security Service | 8005 | ✅ Ready | HTTP |
| Candidate Service | 8008 | ✅ Ready | HTTP |
| Notification Service | 8011 | ✅ Ready | HTTP |
| AI Auditing Service | 8012 | ✅ Ready | HTTP |
| Analytics Service | 8013 | ✅ Ready | HTTP |
| Voice Service | 8015 | ✅ Ready | HTTP |
| Scout Service | 8000 | ✅ Ready | HTTP |
| Explainability Service | 8014 | ✅ Ready | HTTP |
| Project Service | TBD | 🔍 Check | HTTP |

---

## Service-by-Service Instructions

### 1. Avatar Service
**Directory:** `services/avatar-service`  
**Port:** 8001  
**Start Command:**
```bash
cd ~/open-talent/services/avatar-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8001/openapi.json | jq -r '.paths | keys[]' > avatar-service-endpoints.txt
curl -s http://localhost:8001/openapi.json | jq '.paths' > avatar-service-full.json
```
**Swagger UI:** http://localhost:8001/docs

---

### 2. User Service
**Directory:** `services/user-service`  
**Port:** 8001  
**Start Command:**
```bash
cd ~/open-talent/services/user-service
# Start Supabase (Postgres + PostgREST)
docker compose -f docker-compose.supabase.yml up -d
# Run migrations
alembic upgrade head
# Start service
python -m uvicorn app.main:app --reload --port 8001
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8001/openapi.json | jq -r '.paths | keys[]' > user-service-endpoints.txt
curl -s http://localhost:8001/openapi.json | jq '.paths' > user-service-full.json
```
**Swagger UI:** http://localhost:8001/docs  
**Note:** Conflicts with Avatar Service port. Run separately.

---

### 3. Conversation Service
**Directory:** `services/conversation-service`  
**Port:** 8003  
**Environment:**
```bash
export USE_MOCK_OLLAMA=true
export OLLAMA_MODEL=granite4:350m-h
export OLLAMA_HOST=http://localhost:11434
```
**Start Command:**
```bash
cd ~/open-talent/services/conversation-service
python main.py
# OR
uvicorn services.conversation-service.main:app --host 0.0.0.0 --port 8003
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8003/openapi.json | jq -r '.paths | keys[]' > conversation-service-endpoints.txt
curl -s http://localhost:8003/openapi.json | jq '.paths' > conversation-service-full.json
```
**Swagger UI:** http://localhost:8003/docs

---

### 4. Interview Service
**Directory:** `services/interview-service`  
**Port:** 8004  
**Start Command:**
```bash
cd ~/open-talent/services/interview-service
python main.py
# OR
uvicorn services.interview-service.main:app --host 0.0.0.0 --port 8004
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8004/openapi.json | jq -r '.paths | keys[]' > interview-service-endpoints.txt
curl -s http://localhost:8004/openapi.json | jq '.paths' > interview-service-full.json
```
**Swagger UI:** http://localhost:8004/docs

---

### 5. Security Service
**Directory:** `services/security-service`  
**Port:** 8005  
**Start Command:**
```bash
cd ~/open-talent/services/security-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8005/openapi.json | jq -r '.paths | keys[]' > security-service-endpoints.txt
curl -s http://localhost:8005/openapi.json | jq '.paths' > security-service-full.json
```
**Swagger UI:** http://localhost:8005/docs

---

### 6. Candidate Service
**Directory:** `services/candidate-service`  
**Port:** 8008  
**Start Command:**
```bash
cd ~/open-talent/services/candidate-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8008/openapi.json | jq -r '.paths | keys[]' > candidate-service-endpoints.txt
curl -s http://localhost:8008/openapi.json | jq '.paths' > candidate-service-full.json
```
**Swagger UI:** http://localhost:8008/docs

---

### 7. Notification Service
**Directory:** `services/notification-service`  
**Port:** 8011  
**Start Command:**
```bash
cd ~/open-talent/services/notification-service
uvicorn main:app --port 8011 --reload
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8011/openapi.json | jq -r '.paths | keys[]' > notification-service-endpoints.txt
curl -s http://localhost:8011/openapi.json | jq '.paths' > notification-service-full.json
```
**Swagger UI:** http://localhost:8011/docs

---

### 8. AI Auditing Service
**Directory:** `services/ai-auditing-service`  
**Port:** 8012  
**Start Command:**
```bash
cd ~/open-talent/services/ai-auditing-service
uvicorn main:app --port 8012 --reload
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8012/openapi.json | jq -r '.paths | keys[]' > ai-auditing-service-endpoints.txt
curl -s http://localhost:8012/openapi.json | jq '.paths' > ai-auditing-service-full.json
```
**Swagger UI:** http://localhost:8012/docs

---

### 9. Analytics Service
**Directory:** `services/analytics-service`  
**Port:** 8013  
**Start Command:**
```bash
cd ~/open-talent/services/analytics-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8013/openapi.json | jq -r '.paths | keys[]' > analytics-service-endpoints.txt
curl -s http://localhost:8013/openapi.json | jq '.paths' > analytics-service-full.json
```
**Swagger UI:** http://localhost:8013/docs

---

### 10. Explainability Service
**Directory:** `services/explainability-service`  
**Port:** 8014  
**Start Command:**
```bash
cd ~/open-talent/services/explainability-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8014/openapi.json | jq -r '.paths | keys[]' > explainability-service-endpoints.txt
curl -s http://localhost:8014/openapi.json | jq '.paths' > explainability-service-full.json
```
**Swagger UI:** http://localhost:8014/docs

---

### 11. Voice Service
**Directory:** `services/voice-service`  
**Port:** 8015  
**Start Command:**
```bash
cd ~/open-talent/services/voice-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8015/openapi.json | jq -r '.paths | keys[]' > voice-service-endpoints.txt
curl -s http://localhost:8015/openapi.json | jq '.paths' > voice-service-full.json
```
**Swagger UI:** http://localhost:8015/docs

---

### 12. Scout Service
**Directory:** `services/scout-service`  
**Port:** 8000  
**Start Command:**
```bash
cd ~/open-talent/services/scout-service
python main.py
```
**Extract Endpoints:**
```bash
curl -s http://localhost:8000/openapi.json | jq -r '.paths | keys[]' > scout-service-endpoints.txt
curl -s http://localhost:8000/openapi.json | jq '.paths' > scout-service-full.json
```
**Swagger UI:** http://localhost:8000/docs

---

### 13. Project Service
**Directory:** `services/project-service`  
**Port:** TBD (check main.py)  
**Start Command:**
```bash
cd ~/open-talent/services/project-service/app
python main.py
```
**Extract Endpoints:**
```bash
# Port TBD - check service startup logs
curl -s http://localhost:PORT/openapi.json | jq -r '.paths | keys[]' > project-service-endpoints.txt
```

---

## Endpoint Extraction Commands

### Single Service Extraction
```bash
# List all endpoints (paths only)
curl -s http://localhost:PORT/openapi.json | jq -r '.paths | keys[]'

# Full endpoint details with methods
curl -s http://localhost:PORT/openapi.json | jq '.paths'

# Get service info
curl -s http://localhost:PORT/openapi.json | jq '.info'

# Count endpoints
curl -s http://localhost:PORT/openapi.json | jq '.paths | keys | length'

# Filter specific prefix
curl -s http://localhost:PORT/openapi.json | jq -r '.paths | keys[] | select(startswith("/api/v1"))'
```

### Batch Extraction
```bash
# Extract all methods for each endpoint
curl -s http://localhost:PORT/openapi.json | jq -r '.paths | to_entries[] | "\(.key): \(.value | keys | join(", "))"'

# Extract with descriptions
curl -s http://localhost:PORT/openapi.json | jq -r '.paths | to_entries[] | .key as $path | .value | to_entries[] | "\(.key | ascii_upcase) \($path) - \(.value.summary // "No description")"'
```

---

## Automated Extraction Script

Create `extract-all-endpoints.sh`:
```bash
#!/bin/bash
# Automated endpoint extraction for all OpenTalent services

SERVICES=(
    "avatar-service:8001"
    "conversation-service:8003"
    "interview-service:8004"
    "security-service:8005"
    "candidate-service:8008"
    "notification-service:8011"
    "ai-auditing-service:8012"
    "analytics-service:8013"
    "explainability-service:8014"
    "voice-service:8015"
    "scout-service:8000"
)

OUTPUT_DIR="~/open-talent/endpoint-extraction-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "📋 OpenTalent Endpoint Extraction Report" > "$OUTPUT_DIR/SUMMARY.md"
echo "Generated: $(date)" >> "$OUTPUT_DIR/SUMMARY.md"
echo "" >> "$OUTPUT_DIR/SUMMARY.md"

for service_port in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_port"
    echo "🔍 Checking $service on port $port..."
    
    # Check if service is running
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health" | grep -q "200"; then
        echo "✅ $service is running"
        
        # Extract endpoints
        curl -s "http://localhost:$port/openapi.json" | jq -r '.paths | keys[]' > "$OUTPUT_DIR/${service}-endpoints.txt"
        curl -s "http://localhost:$port/openapi.json" | jq '.paths' > "$OUTPUT_DIR/${service}-full.json"
        
        # Count
        count=$(curl -s "http://localhost:$port/openapi.json" | jq '.paths | keys | length')
        echo "  📊 Found $count endpoints"
        
        # Add to summary
        echo "## $service (Port $port)" >> "$OUTPUT_DIR/SUMMARY.md"
        echo "- Status: ✅ Running" >> "$OUTPUT_DIR/SUMMARY.md"
        echo "- Endpoints: $count" >> "$OUTPUT_DIR/SUMMARY.md"
        echo "- Swagger: http://localhost:$port/docs" >> "$OUTPUT_DIR/SUMMARY.md"
        echo "" >> "$OUTPUT_DIR/SUMMARY.md"
    else
        echo "❌ $service not responding on port $port"
        echo "## $service (Port $port)" >> "$OUTPUT_DIR/SUMMARY.md"
        echo "- Status: ❌ Not Running" >> "$OUTPUT_DIR/SUMMARY.md"
        echo "" >> "$OUTPUT_DIR/SUMMARY.md"
    fi
    echo ""
done

echo "✅ Extraction complete! Results saved to: $OUTPUT_DIR"
```

**Usage:**
```bash
chmod +x extract-all-endpoints.sh
./extract-all-endpoints.sh
```

---

## Validation Checklist

After extraction, verify:

- [ ] All services started successfully
- [ ] OpenAPI schemas accessible at `/openapi.json`
- [ ] Swagger UI accessible at `/docs`
- [ ] Endpoints follow naming convention (`/api/v1/...`)
- [ ] All CRUD operations present where expected
- [ ] Health check endpoints exist
- [ ] Authentication endpoints documented
- [ ] Request/response schemas complete

---

## Next Steps

1. **Start Services Systematically:** Follow the order above to avoid port conflicts
2. **Extract Endpoints:** Use the commands to gather endpoint lists
3. **Consolidate Results:** Merge all endpoint files into master validation document
4. **Cross-Reference:** Compare extracted endpoints with API specification documents
5. **Update Documentation:** Update FINAL_API_VALIDATION_DOCUMENT.md with actual endpoints

---

**📝 Notes:**
- Services on port 8001 (Avatar/User) must run separately
- Some services require Docker/Docker Compose
- Use `ctrl+c` to stop services between runs
- Check service logs for port conflicts or startup errors