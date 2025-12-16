#!/bin/bash

# TalentAI - Start AI Services (vLLM + Qdrant)
# This script starts the vLLM inference server and Qdrant vector database

set -e

echo "🚀 Starting TalentAI AI Services (vLLM + Qdrant)"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is already in use (possibly $service)${NC}"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    echo -e "${BLUE}⏳ Waiting for $service_name to be ready...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        echo -e "${BLUE}   Attempt $attempt/$max_attempts...${NC}"
        sleep 2
        ((attempt++))
    done

    echo -e "${RED}❌ $service_name failed to start within expected time${NC}"
    return 1
}

# Check available ports
echo "🔍 Checking port availability..."
check_port 8000 "vLLM" || VLLM_PORT_CONFLICT=true
check_port 6333 "Qdrant" || QDRANT_PORT_CONFLICT=true

if [ "$VLLM_PORT_CONFLICT" = true ] || [ "$QDRANT_PORT_CONFLICT" = true ]; then
    echo -e "${YELLOW}⚠️  Some ports are in use. Services might already be running.${NC}"
    echo -e "${YELLOW}   Run 'docker ps' to check running containers.${NC}"
fi

# Detect GPU availability
if command -v nvidia-smi &> /dev/null && nvidia-smi > /dev/null 2>&1; then
    echo -e "${GREEN}🎮 NVIDIA GPU detected - using GPU acceleration${NC}"
    GPU_AVAILABLE=true
    VLLM_COMMAND="docker run --gpus all --shm-size 1g -d --name talentai-vllm -p 8000:8000 -v \$HOME/.cache/huggingface:/root/.cache/huggingface vllm/vllm-openai:latest --model ibm/granite-3.1-2b-instruct --host 0.0.0.0 --port 8000 --dtype float16 --max-model-len 2048"
else
    echo -e "${YELLOW}💻 No NVIDIA GPU detected - using CPU mode (slower)${NC}"
    GPU_AVAILABLE=false
    VLLM_COMMAND="docker run --shm-size 1g -d --name talentai-vllm -p 8000:8000 vllm/vllm-openai:latest --model ibm/granite-3.1-2b-instruct --host 0.0.0.0 --port 8000 --dtype float16 --max-model-len 2048"
fi

# Start Qdrant (lightweight, always works)
echo -e "${BLUE}🗄️  Starting Qdrant vector database...${NC}"
if docker ps -a --format 'table {{.Names}}' | grep -q "^talentai-qdrant$"; then
    echo -e "${YELLOW}📦 Qdrant container already exists, restarting...${NC}"
    docker restart talentai-qdrant
else
    docker run -d --name talentai-qdrant \
        -p 6333:6333 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant:latest
fi

# Wait for Qdrant to be ready
wait_for_service "http://localhost:6333/health" "Qdrant"

# Start vLLM
echo -e "${BLUE}🤖 Starting vLLM inference server...${NC}"
if docker ps -a --format 'table {{.Names}}' | grep -q "^talentai-vllm$"; then
    echo -e "${YELLOW}🚀 vLLM container already exists, restarting...${NC}"
    docker restart talentai-vllm
else
    eval $VLLM_COMMAND
fi

# Wait for vLLM to be ready (takes longer to load model)
echo -e "${BLUE}⏳ Loading Granite model (this may take 2-5 minutes on first run)...${NC}"
wait_for_service "http://localhost:8000/v1/models" "vLLM"

# Final status check
echo ""
echo -e "${GREEN}🎉 AI Services Started Successfully!${NC}"
echo "========================================"
echo -e "${GREEN}✅ vLLM Server:${NC} http://localhost:8000"
echo -e "${GREEN}✅ Qdrant DB:${NC} http://localhost:6333"
echo -e "${GREEN}✅ Model:${NC} ibm/granite-3.1-2b-instruct"
echo -e "${GREEN}✅ GPU:${NC} $( [ "$GPU_AVAILABLE" = true ] && echo "Enabled" || echo "CPU Mode")"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Test services: python test_question_builder_vllm.py"
echo "2. Start interview service: uvicorn app.main:app --reload --host 0.0.0.0 --port 8004"
echo "3. Check API docs: http://localhost:8004/api/v1/docs"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "Stop services: docker stop talentai-vllm talentai-qdrant"
echo "View logs: docker logs talentai-vllm"
echo "Cleanup: docker rm talentai-vllm talentai-qdrant"