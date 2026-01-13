#!/bin/bash
# Quick test script for Voice Service Docker deployment
# Tests: Build, Run, Health Check, OpenAPI access

set -e

echo "🚀 Voice Service Docker Deployment Test"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="voice-service"
IMAGE_TAG="latest"
CONTAINER_NAME="voice-service-test"
PORT=8002

echo "📋 Step 1: Building Docker image..."
if docker build -t ${IMAGE_NAME}:${IMAGE_TAG} --target production . > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

echo ""
echo "📋 Step 2: Stopping existing container (if any)..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo ""
echo "📋 Step 3: Starting container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:${PORT} \
    -e USE_MOCK_SERVICES=true \
    -e ENABLE_WEBRTC=false \
    ${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Container started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start container${NC}"
    exit 1
fi

echo ""
echo "📋 Step 4: Waiting for service to be ready (max 30s)..."
for i in {1..30}; do
    if curl -s http://localhost:${PORT}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Service is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Service failed to start within 30 seconds${NC}"
        echo ""
        echo "Container logs:"
        docker logs ${CONTAINER_NAME}
        docker stop ${CONTAINER_NAME}
        docker rm ${CONTAINER_NAME}
        exit 1
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "📋 Step 5: Testing endpoints..."

# Test 1: Root endpoint
echo -n "  - Testing root endpoint... "
if curl -s http://localhost:${PORT}/ | grep -q "Voice Service"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 2: Health endpoint
echo -n "  - Testing health endpoint... "
if curl -s http://localhost:${PORT}/health | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 3: OpenAPI schema
echo -n "  - Testing OpenAPI schema... "
if curl -s http://localhost:${PORT}/openapi.json | grep -q "Voice Service API"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 4: API docs endpoint
echo -n "  - Testing API docs endpoint... "
if curl -s http://localhost:${PORT}/api-docs | grep -q "voice-processing"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "📋 Step 6: Displaying service info..."
echo ""
curl -s http://localhost:${PORT}/ | python3 -m json.tool
echo ""

echo "📋 Step 7: OpenAPI Documentation URLs"
echo "========================================"
echo -e "  ${GREEN}Swagger UI:${NC}      http://localhost:${PORT}/docs"
echo -e "  ${GREEN}ReDoc:${NC}           http://localhost:${PORT}/redoc"
echo -e "  ${GREEN}OpenAPI JSON:${NC}    http://localhost:${PORT}/openapi.json"
echo -e "  ${GREEN}API Summary:${NC}     http://localhost:${PORT}/api-docs"
echo ""

echo -e "${YELLOW}📝 Note: Container is running in MOCK mode for testing${NC}"
echo -e "${YELLOW}   To use real services, mount models directory and set USE_MOCK_SERVICES=false${NC}"
echo ""

# Ask user if they want to keep the container running
read -p "Keep container running? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📋 Step 8: Cleanup..."
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
    echo -e "${GREEN}✓ Container stopped and removed${NC}"
else
    echo ""
    echo -e "${GREEN}✓ Container is still running${NC}"
    echo "  Stop with: docker stop ${CONTAINER_NAME}"
    echo "  View logs: docker logs -f ${CONTAINER_NAME}"
    echo "  Remove: docker rm -f ${CONTAINER_NAME}"
fi

echo ""
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "========================================"
