#!/bin/bash

# OpenTalent Agents - Stop Script
# Stops all running agents

set -e

echo "🛑 Stopping OpenTalent Agents..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop Genkit service
echo -e "${YELLOW}Stopping Genkit service...${NC}"
pkill -f "npm run dev" || echo -e "${YELLOW}Genkit service not running${NC}"

# Function to stop an agent
stop_agent() {
    local agent_name=$1
    local pid_file="/tmp/open-talent-$agent_name.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping $agent_name (PID: $pid)...${NC}"
            kill "$pid"
            rm "$pid_file"
            echo -e "${GREEN}✓ $agent_name stopped${NC}"
        else
            echo -e "${YELLOW}$agent_name not running${NC}"
            rm "$pid_file"
        fi
    else
        echo -e "${YELLOW}$agent_name PID file not found${NC}"
    fi
}

# Stop all agents
stop_agent "Scout Coordinator"
stop_agent "Proactive Scanning"
stop_agent "Boolean Mastery"
stop_agent "Personalized Engagement"
stop_agent "Market Intelligence"
stop_agent "Tool Leverage"
stop_agent "Quality Focused"

# Kill any remaining Python processes
pkill -f "uvicorn main:app" || echo -e "${YELLOW}No uvicorn processes found${NC}"

# Optionally stop Redis (commented out by default)
# echo -e "${YELLOW}Stopping Redis...${NC}"
# docker stop open-talent-redis || echo -e "${YELLOW}Redis container not running${NC}"
# docker rm open-talent-redis || echo -e "${YELLOW}Redis container not found${NC}"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✅ All agents stopped successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
