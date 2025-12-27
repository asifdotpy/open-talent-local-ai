#!/bin/bash

# OpenTalent Agents - Quick Start Script
# Starts all agents in development mode

set -e

echo "🚀 Starting OpenTalent Agents..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -e "${YELLOW}Checking Redis...${NC}"
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}Redis CLI not found. Please install Redis.${NC}"
    exit 1
fi

if ! redis-cli ping &> /dev/null; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    docker run -d -p 6379:6379 --name open-talent-redis redis:7-alpine
    sleep 2
fi

if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis failed to start${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your API keys before continuing${NC}"
    exit 1
fi

# Source environment
set -a
source .env
set +a

# Start Genkit service
echo -e "${YELLOW}Starting Genkit service...${NC}"
cd genkit-service
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Genkit dependencies...${NC}"
    npm install
fi
npm run dev &
GENKIT_PID=$!
cd ..
sleep 3
echo -e "${GREEN}✓ Genkit service started (PID: $GENKIT_PID)${NC}"

# Function to start a Python agent
start_agent() {
    local agent_dir=$1
    local agent_name=$2
    local port=$3

    echo -e "${YELLOW}Starting $agent_name...${NC}"
    cd "$agent_dir"

    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi

    # Activate virtual environment and install dependencies
    source .venv/bin/activate
    pip install -q -r requirements.txt

    # Start agent in background
    python main.py &
    local pid=$!
    echo "$pid" > "/tmp/open-talent-$agent_name.pid"

    cd ..
    sleep 1

    # Check if agent started successfully
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $agent_name started on port $port (PID: $pid)${NC}"
    else
        echo -e "${YELLOW}⚠ $agent_name starting... (check logs if not ready in 10s)${NC}"
    fi
}

# Start all agents
start_agent "scout-coordinator-agent" "Scout Coordinator" 8090
start_agent "proactive-scanning-agent" "Proactive Scanning" 8091
start_agent "boolean-mastery-agent" "Boolean Mastery" 8092
start_agent "personalized-engagement-agent" "Personalized Engagement" 8093
start_agent "market-intelligence-agent" "Market Intelligence" 8094
start_agent "tool-leverage-agent" "Tool Leverage" 8095
start_agent "quality-focused-agent" "Quality Focused" 8096

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✅ All agents started successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Agent URLs:"
echo "  - Scout Coordinator:        http://localhost:8090"
echo "  - Proactive Scanning:       http://localhost:8091"
echo "  - Boolean Mastery:          http://localhost:8092"
echo "  - Personalized Engagement:  http://localhost:8093"
echo "  - Market Intelligence:      http://localhost:8094"
echo "  - Tool Leverage:            http://localhost:8095"
echo "  - Quality Focused:          http://localhost:8096"
echo "  - Genkit Service:           http://localhost:3400"
echo ""
echo "To stop all agents, run: ./stop-agents.sh"
echo ""
echo "Example usage:"
echo "  curl -X POST http://localhost:8090/pipelines/start \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"project_id\": \"test\", \"job_description\": \"Python Developer\"}'"
