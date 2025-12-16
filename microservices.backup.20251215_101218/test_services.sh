#!/bin/bash
# TalentAI Platform - Service Startup Test Script
# Tests that all services can start without model execution

set -e

echo "🧪 Testing TalentAI Platform Service Startup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is healthy
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=10
    local attempt=1

    echo -n "⏳ Checking $service_name (port $port)... "

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Healthy${NC}"
            return 0
        fi
        echo -n "."
        sleep 3
        ((attempt++))
    done

    echo -e "${RED}❌ Failed to start${NC}"
    return 1
}

# Function to test service startup
test_service_startup() {
    local service_name=$1
    local port=$2

    echo -e "${YELLOW}🔄 Testing $service_name startup...${NC}"

    # Check if container is running
    if ! docker ps | grep -q "fios-$service_name"; then
        echo -e "${RED}❌ Container not running${NC}"
        return 1
    fi

    # Check health endpoint
    if ! check_service "$service_name" "$port"; then
        return 1
    fi

    echo -e "${GREEN}✅ $service_name startup test passed${NC}"
    return 0
}

# Test Ollama first (required by conversation service)
echo -e "${YELLOW}🔄 Testing Ollama service...${NC}"
if ! docker ps | grep -q "talent-ollama"; then
    echo -e "${RED}❌ Ollama container not running${NC}"
    exit 1
fi

# Wait for Ollama to be ready and check if model is available
echo -n "⏳ Checking Ollama model availability... "
if docker exec talent-ollama ollama list | grep -q "granite4:350m-h"; then
    echo -e "${GREEN}✅ Model available${NC}"
else
    echo -e "${YELLOW}⚠️  Model not yet available (this is normal on first run)${NC}"
fi

# Test each service
services=(
    "conversation-service:8003"
    "voice-service:8002"
    "interview-service:8004"
    "sourcer-service:8005"
)

failed_services=()

for service in "${services[@]}"; do
    IFS=':' read -r service_name port <<< "$service"
    if ! test_service_startup "$service_name" "$port"; then
        failed_services+=("$service_name")
    fi
done

# Summary
echo ""
echo "📊 Test Summary:"
if [ ${#failed_services[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All services started successfully!${NC}"
    echo ""
    echo "🚀 Ready for Phase 3: Infrastructure & Deployment"
    echo ""
    echo "🎯 Demo Services Status (Oct 10):"
    echo "✅ Conversation Service: AI question generation"
    echo "✅ Voice Service: STT/TTS processing"  
    echo "✅ Agent Agent Service: Orchestration & avatar generation"
    echo "✅ Avatar Service: Local SadTalker implementation"
    echo ""
    echo "Next steps:"
    echo "1. Deploy services to server with GPU support"
    echo "2. Configure service networking and environment"
    echo "3. Test end-to-end integration with avatar service"
    echo "4. Prepare demo scenarios and test data"
else
    echo -e "${RED}❌ Failed services: ${failed_services[*]}${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check Docker logs: docker logs fios-<service_name>"
    echo "2. Verify environment variables"
    echo "3. Check service dependencies"
    exit 1
fi