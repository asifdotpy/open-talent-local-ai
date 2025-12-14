# Agent Integration Analysis - Scout Service Update

**Date**: December 13, 2025  
**Status**: Planning Phase  
**Objective**: Integrate agent discovery and routing into Scout Service

## Agent Registry

### Active Agents (9 Total)

| Agent Name | Port | Purpose | Status |
|------------|------|---------|--------|
| **scout-coordinator-agent** | 8090 | Orchestrates talent sourcing workflow | FastAPI |
| **proactive-scanning-agent** | 8091 | Proactive candidate identification | FastAPI |
| **boolean-mastery-agent** | 8092 | Boolean query optimization | FastAPI |
| **personalized-engagement-agent** | 8093 | Personalized candidate engagement | FastAPI |
| **market-intelligence-agent** | 8094 | Market and industry intelligence | FastAPI |
| **tool-leverage-agent** | 8095 | Tool and skill optimization | FastAPI |
| **quality-focused-agent** | 8096 | Quality assurance and assessment | FastAPI |
| **data-enrichment-agent** | 8097 | Profile enrichment (free + paid tiers) | FastAPI |
| **interviewer-agent** | 8080 | Interview orchestration & evaluation | FastAPI |

### Additional Components

| Component | Type | Purpose |
|-----------|------|---------|
| **shared/** | Library | Common models, message bus, service clients |
| **genkit-service** | Service | Google Genkit integration (if needed) |
| **start-agents.sh** | Script | Batch startup script for all agents |
| **stop-agents.sh** | Script | Batch shutdown script for all agents |

## Current Scout Service Architecture

### Endpoints (Port 8000)
- `GET /health` - Health check
- `POST /search` - GitHub talent search
- `POST /handoff` - Create interview handoff payload

### Current Limitations
❌ No agent discovery mechanism  
❌ No agent routing capability  
❌ No inter-agent communication  
❌ No unified agent registry  
❌ No agent health monitoring  

## Integration Strategy

### Phase 1: Agent Registry System

Create agent registry in scout-service with:
1. **Agent Discovery** - Automatic detection of agents from /agents directory
2. **Health Monitoring** - Periodic health checks for all agents
3. **Agent Registry API** - `/agents/registry` endpoint returning agent metadata
4. **Agent Lookup** - Route requests to appropriate agent by name or capability

### Phase 2: Enhanced Search & Handoff

Update `/search` and `/handoff` endpoints to:
1. Accept agent parameters or auto-select based on search criteria
2. Route to specialized agents (e.g., market-intelligence-agent for market research)
3. Coordinate multi-agent workflows
4. Aggregate results from multiple agents

### Phase 3: Unified Message Bus

Connect to shared message bus for:
1. Inter-agent communication
2. Event propagation
3. Pipeline state management
4. Asynchronous task coordination

## Scout Service Enhancement Plan

### 1. Agent Registry Model
```python
class AgentMetadata(BaseModel):
    name: str  # e.g., "scout-coordinator-agent"
    port: int  # e.g., 8090
    url: str  # e.g., "http://localhost:8090"
    purpose: str  # e.g., "Orchestrates talent sourcing workflow"
    capabilities: List[str]  # e.g., ["search", "analysis", "enrichment"]
    status: str  # "healthy", "unhealthy", "unreachable"
    last_health_check: datetime
    endpoints: List[str]  # Available endpoints
```

### 2. Agent Discovery Module
- Scan `/agents` directory for agent configurations
- Parse agent main.py files for port information
- Build in-memory registry with metadata
- Implement health check mechanism

### 3. Enhanced Endpoints

**GET /agents/registry**
- Returns all available agents
- Includes health status, capabilities, ports
- Enables external agents to discover each other

**POST /agents/route**
- Route requests to appropriate agent
- Load balance across multiple agents if needed
- Handle agent unavailability with fallback

**POST /agents/search**
- Enhanced search with agent routing
- Multi-agent parallel search
- Result aggregation

**POST /agents/handoff**
- Route handoff through appropriate agents
- Coordinate with interviewer-agent
- Maintain pipeline state

### 4. Health Monitoring
- Periodic health checks for all agents
- Circuit breaker pattern for unreachable agents
- Automatic recovery detection
- Health status exposed in `/health` endpoint

## Integration Points with Shared

Scout service will leverage `shared/` module:
- `MessageBus` - Event propagation
- `Topics` - Standard topics for inter-agent communication
- `AgentMessage` - Standardized message format
- `Models` - Common data structures (CandidateProfile, SourcingPipeline, etc.)
- `ServiceClients` - HTTP clients for other microservices

## Environment Configuration

### Scout Service `.env`
```env
# Agent Configuration
AGENT_DISCOVERY_PATH=/home/asif1/open-talent/agents
AGENT_HEALTH_CHECK_INTERVAL=30  # seconds
AGENT_TIMEOUT=30  # seconds
AGENT_RETRY_ATTEMPTS=3

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Service Configuration
SERVICE_NAME=scout-service
SERVICE_VERSION=1.0.0
```

## Dependencies to Add

### Python Packages
```
aiofiles>=24.1.0        # Async file operations for agent discovery
tenacity>=8.2.3         # Retry logic for agent requests
opentelemetry-api>=1.21.0  # Distributed tracing
opentelemetry-sdk>=1.21.0  # Tracing SDK
```

### Current Dependencies
```
aiohttp
python-dotenv
requests
fastapi
uvicorn
pydantic
```

## Implementation Roadmap

### Stage 1: Agent Registry (2 hours)
- [x] Analyze agent structure
- [ ] Create AgentMetadata model
- [ ] Implement agent discovery from `/agents` directory
- [ ] Add `/agents/registry` endpoint
- [ ] Test agent detection

### Stage 2: Health Monitoring (1 hour)
- [ ] Implement health check mechanism
- [ ] Add background health check task
- [ ] Update `/health` with agent statuses
- [ ] Implement circuit breaker pattern

### Stage 3: Search Enhancement (2 hours)
- [ ] Add agent parameter to `/search` endpoint
- [ ] Implement agent routing logic
- [ ] Add multi-agent coordination
- [ ] Result aggregation from multiple agents

### Stage 4: Handoff Coordination (1 hour)
- [ ] Route `/handoff` through agents
- [ ] Coordinate with interviewer-agent
- [ ] Maintain pipeline state
- [ ] Error handling for missing agents

### Stage 5: Testing & Documentation (1 hour)
- [ ] Unit tests for agent discovery
- [ ] Integration tests with real agents
- [ ] API documentation update
- [ ] Troubleshooting guide

## Success Criteria

✅ All 9 agents discoverable from scout-service  
✅ Agent health monitoring operational  
✅ `/agents/registry` returning all agents with status  
✅ Search requests routed to appropriate agents  
✅ Handoff coordination working with interviewer-agent  
✅ Message bus integration operational  
✅ Documentation complete  

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Agent unavailability | Health checks + circuit breaker |
| Port conflicts | Configuration validation on startup |
| Shared module imports | Virtual env isolation + explicit paths |
| Inter-agent latency | Async/parallel agent calls |
| Message bus failures | Graceful degradation + fallback |

## Next Steps

1. ✅ **Analysis Complete** - Agent structure mapped
2. **Implement Agent Registry** - Create discovery mechanism
3. **Add Health Monitoring** - Periodic agent checks
4. **Enhance Search Endpoint** - Route to agents
5. **Test Integration** - Verify all agents operational
6. **Documentation** - API docs, deployment guide

---

## Files to Create/Modify

### New Files
- `/home/asif1/open-talent/microservices/scout-service/agent_registry.py`
- `/home/asif1/open-talent/microservices/scout-service/agent_health.py`
- `/home/asif1/open-talent/microservices/scout-service/agent_routes.py`

### Files to Modify
- `/home/asif1/open-talent/microservices/scout-service/main.py`
- `/home/asif1/open-talent/microservices/scout-service/requirements.txt`

### Updated Environment
- `/home/asif1/open-talent/microservices/scout-service/.env`

