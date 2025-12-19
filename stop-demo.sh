#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# OpenTalent Demo Stop Script
# ═══════════════════════════════════════════════════════════════════════════
# This script stops all OpenTalent demo services
# ═══════════════════════════════════════════════════════════════════════════

WORKSPACE="/home/asif1/open-talent"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Service ports
declare -A PORTS=(
    ["ollama"]="11434"
    ["analytics"]="8007"
    ["gateway"]="8009"
    ["desktop"]="3000"
)

echo -e "${RED}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║           OpenTalent - Stop Demo Environment           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Logging functions
log_info() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${CYAN}ℹ${NC} $msg"
}

log_success() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${GREEN}✅${NC} $msg"
}

log_warning() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${YELLOW}⚠${NC} $msg"
}

# Kill process on port
kill_port() {
    local port=$1
    local service_name=$2
    local pid=$(lsof -t -i :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        log_info "Stopping $service_name on port $port (PID: $pid)"
        kill $pid 2>/dev/null || true
        sleep 1
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            log_warning "Force killing $service_name (PID: $pid)"
            kill -9 $pid 2>/dev/null || true
        fi
        log_success "$service_name stopped"
    else
        log_info "$service_name not running on port $port"
    fi
}

# Stop Ollama
stop_ollama() {
    log_info "Stopping Ollama..."
    pkill -f "ollama serve" 2>/dev/null || true
    sleep 1
    log_success "Ollama stopped"
}

# Stop Python services
stop_python_services() {
    log_info "Stopping Python microservices..."
    pkill -f "uvicorn.*analytics-service" 2>/dev/null || true
    pkill -f "uvicorn.*desktop-integration-service" 2>/dev/null || true
    sleep 1
    log_success "Python services stopped"
}

# Stop Node.js processes
stop_node_processes() {
    log_info "Stopping Node.js processes..."
    pkill -f "react-scripts start" 2>/dev/null || true
    pkill -f "electron.*main.js" 2>/dev/null || true
    pkill -f "concurrently.*npm run dev" 2>/dev/null || true
    sleep 1
    log_success "Node.js processes stopped"
}

# Main stop function
main() {
    echo "Stopping OpenTalent Demo Environment..."
    echo ""

    # Stop by port
    kill_port ${PORTS["desktop"]} "Desktop App"
    kill_port ${PORTS["gateway"]} "Gateway Service"
    kill_port ${PORTS["analytics"]} "Analytics Service"

    # Stop Ollama
    stop_ollama

    # Stop any remaining Python/Node processes
    stop_python_services
    stop_node_processes

    echo ""
    log_success "All OpenTalent demo services stopped!"
    echo ""
    echo -e "${GREEN}🧹 Demo environment cleaned up successfully${NC}"
}

main "$@"