#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# OpenTalent Demo Startup Script
# ═══════════════════════════════════════════════════════════════════════════
# This script starts the complete OpenTalent demo environment:
#   1. Ollama (AI model server) - port 11434
#   2. Analytics Service - port 8007
#   3. Desktop Integration Service (Gateway) - port 8009
#   4. Desktop App (React/Electron) - port 3000
#
# Usage: ./start-demo.sh
# Stop: Ctrl+C or ./stop-demo.sh
# ═══════════════════════════════════════════════════════════════════════════

WORKSPACE="/home/asif1/open-talent"
OLLAMA_MODEL="granite4:350m-h"  # Lightweight model for demo
LOG_DIR="/tmp/opentalent-demo"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$LOG_DIR"

# Main log file
MAIN_LOG_FILE="$LOG_DIR/demo_startup_${TIMESTAMP}.log"

# Service tracking
declare -A PIDS
declare -A PORTS=(
    ["ollama"]="11434"
    ["analytics"]="8007"
    ["gateway"]="8009"
    ["desktop"]="3000"
)

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║           OpenTalent - Complete Demo Startup            ║"
echo "║        AI Interview Platform with Analytics             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "Log file: $MAIN_LOG_FILE" | tee -a "$MAIN_LOG_FILE"
echo "" | tee -a "$MAIN_LOG_FILE"

# Logging functions
log_info() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${CYAN}ℹ${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_success() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${GREEN}✅${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_error() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${RED}❌${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_warning() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} ${YELLOW}⚠${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_header() {
    local msg="$1"
    echo "" | tee -a "$MAIN_LOG_FILE"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$MAIN_LOG_FILE"
    echo -e "${MAGENTA}$msg${NC}" | tee -a "$MAIN_LOG_FILE"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$MAIN_LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log_header "🔍 Checking Prerequisites"

    local missing_tools=0

    # Check Node.js and npm
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Node.js: $(node --version)"
    fi

    if ! command -v npm &> /dev/null; then
        log_error "npm not found"
        missing_tools=$((missing_tools + 1))
    else
        log_success "npm: $(npm --version)"
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Python 3: $(python3 --version)"
    fi

    # Check Ollama
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama not found. Install from: https://ollama.ai/download"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Ollama: $(ollama --version)"
    fi

    # Check curl
    if ! command -v curl &> /dev/null; then
        log_warning "curl not found (needed for health checks)"
    else
        log_success "curl: Available"
    fi

    if [ $missing_tools -gt 0 ]; then
        log_error "Missing $missing_tools prerequisite(s). Please install and try again."
        exit 1
    fi
}

# Check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    fi
    return 1  # Port is free
}

# Kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        log_warning "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Start Ollama service
start_ollama() {
    log_header "🤖 Starting Ollama AI Service"

    local port=${PORTS["ollama"]}

    # Check if already running
    if check_port $port; then
        log_success "Ollama already running on port $port"
        return 0
    fi

    # Start Ollama in background
    log_info "Starting Ollama service..."
    ollama serve > "$LOG_DIR/ollama_${TIMESTAMP}.log" 2>&1 &
    PIDS["ollama"]=$!

    # Wait for Ollama to start
    local attempts=0
    while [ $attempts -lt 10 ]; do
        if curl -s http://localhost:$port/api/tags &> /dev/null; then
            log_success "Ollama started successfully (PID: ${PIDS["ollama"]})"
            return 0
        fi
        sleep 2
        attempts=$((attempts + 1))
    done

    log_error "Ollama failed to start"
    return 1
}

# Ensure AI model is available
ensure_model() {
    log_info "Ensuring AI model '$OLLAMA_MODEL' is available..."

    # Check if model exists
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        log_success "Model '$OLLAMA_MODEL' already available"
        return 0
    fi

    # Pull model
    log_info "Downloading model '$OLLAMA_MODEL' (this may take a few minutes)..."
    if ollama pull "$OLLAMA_MODEL" >> "$LOG_DIR/ollama_${TIMESTAMP}.log" 2>&1; then
        log_success "Model '$OLLAMA_MODEL' downloaded successfully"
        return 0
    else
        log_error "Failed to download model '$OLLAMA_MODEL'"
        return 1
    fi
}

# Start Analytics Service
start_analytics() {
    log_header "📊 Starting Analytics Service"

    local port=${PORTS["analytics"]}
    local service_dir="$WORKSPACE/microservices/analytics-service"
    local log_file="$LOG_DIR/analytics_${TIMESTAMP}.log"

    if [ ! -d "$service_dir" ]; then
        log_error "Analytics service directory not found: $service_dir"
        return 1
    fi

    # Kill any existing process
    if check_port $port; then
        kill_port $port
    fi

    # Start analytics service
    log_info "Starting analytics service on port $port..."
    (
        cd "$service_dir"
        ./start.sh >> "$log_file" 2>&1
    ) &
    PIDS["analytics"]=$!

    # Wait for service to be ready
    local attempts=0
    while [ $attempts -lt 15 ]; do
        if curl -s http://localhost:$port/health &> /dev/null; then
            log_success "Analytics service ready (PID: ${PIDS["analytics"]})"
            return 0
        fi
        sleep 2
        attempts=$((attempts + 1))
    done

    log_error "Analytics service failed to start"
    if [ -f "$log_file" ]; then
        log_error "Last 5 lines of analytics log:"
        tail -n 5 "$log_file" | sed 's/^/  /' | tee -a "$MAIN_LOG_FILE"
    fi
    return 1
}

# Start Desktop Integration Service (Gateway)
start_gateway() {
    log_header "🌐 Starting Desktop Integration Gateway"

    local port=${PORTS["gateway"]}
    local service_dir="$WORKSPACE/microservices/desktop-integration-service"
    local log_file="$LOG_DIR/gateway_${TIMESTAMP}.log"

    if [ ! -d "$service_dir" ]; then
        log_error "Gateway service directory not found: $service_dir"
        return 1
    fi

    # Kill any existing process
    if check_port $port; then
        kill_port $port
    fi

    # Start gateway service
    log_info "Starting gateway service on port $port..."
    (
        cd "$service_dir"
        ./start.sh >> "$log_file" 2>&1
    ) &
    PIDS["gateway"]=$!

    # Wait for service to be ready
    local attempts=0
    while [ $attempts -lt 15 ]; do
        if curl -s http://localhost:$port/health &> /dev/null; then
            log_success "Gateway service ready (PID: ${PIDS["gateway"]})"
            return 0
        fi
        sleep 2
        attempts=$((attempts + 1))
    done

    log_error "Gateway service failed to start"
    if [ -f "$log_file" ]; then
        log_error "Last 5 lines of gateway log:"
        tail -n 5 "$log_file" | sed 's/^/  /' | tee -a "$MAIN_LOG_FILE"
    fi
    return 1
}

# Start Desktop App
start_desktop_app() {
    log_header "💻 Starting Desktop Application"

    local port=${PORTS["desktop"]}
    local app_dir="$WORKSPACE/desktop-app"
    local log_file="$LOG_DIR/desktop_${TIMESTAMP}.log"

    if [ ! -d "$app_dir" ]; then
        log_error "Desktop app directory not found: $app_dir"
        return 1
    fi

    # Kill any existing process on port 3000
    if check_port $port; then
        kill_port $port
    fi

    # Start desktop app
    log_info "Starting desktop app (React dev server + Electron)..."
    (
        cd "$app_dir"
        npm run dev >> "$log_file" 2>&1
    ) &
    PIDS["desktop"]=$!

    # Wait for React dev server to be ready
    local attempts=0
    while [ $attempts -lt 20 ]; do
        if curl -s http://localhost:$port &> /dev/null; then
            log_success "Desktop app ready at http://localhost:$port (PID: ${PIDS["desktop"]})"
            return 0
        fi
        sleep 3
        attempts=$((attempts + 1))
    done

    log_error "Desktop app failed to start"
    if [ -f "$log_file" ]; then
        log_error "Last 5 lines of desktop app log:"
        tail -n 5 "$log_file" | sed 's/^/  /' | tee -a "$MAIN_LOG_FILE"
    fi
    return 1
}

# Health check all services
check_all_services() {
    log_header "🔍 Checking All Services Health"

    local all_healthy=true

    # Check Ollama
    if curl -s http://localhost:${PORTS["ollama"]}/api/tags &> /dev/null; then
        log_success "Ollama: ✅ Online"
    else
        log_error "Ollama: ❌ Offline"
        all_healthy=false
    fi

    # Check Analytics
    if curl -s http://localhost:${PORTS["analytics"]}/health &> /dev/null; then
        log_success "Analytics Service: ✅ Online"
    else
        log_error "Analytics Service: ❌ Offline"
        all_healthy=false
    fi

    # Check Gateway
    if curl -s http://localhost:${PORTS["gateway"]}/health &> /dev/null; then
        log_success "Gateway Service: ✅ Online"
    else
        log_error "Gateway Service: ❌ Offline"
        all_healthy=false
    fi

    # Check Desktop App
    if curl -s http://localhost:${PORTS["desktop"]} &> /dev/null; then
        log_success "Desktop App: ✅ Online"
    else
        log_error "Desktop App: ❌ Offline"
        all_healthy=false
    fi

    return $([ "$all_healthy" = true ] && echo 0 || echo 1)
}

# Cleanup function
cleanup() {
    log_header "🛑 Shutting Down Demo Environment"

    # Kill all tracked processes
    for service in "${!PIDS[@]}"; do
        local pid=${PIDS[$service]}
        if kill -0 $pid 2>/dev/null; then
            log_info "Stopping $service (PID: $pid)..."
            kill $pid 2>/dev/null || true
        fi
    done

    sleep 2

    # Force kill if needed
    for service in "${!PIDS[@]}"; do
        local pid=${PIDS[$service]}
        if kill -0 $pid 2>/dev/null; then
            log_warning "Force killing $service (PID: $pid)..."
            kill -9 $pid 2>/dev/null || true
        fi
    done

    log_success "Demo environment stopped"
    exit 0
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Main execution
check_prerequisites

log_header "🚀 Starting OpenTalent Demo Environment"

failed_services=()

# 1. Start Ollama
if ! start_ollama; then
    failed_services+=("ollama")
fi

# 2. Ensure AI model
if ! ensure_model; then
    failed_services+=("model_download")
fi

# 3. Start Analytics Service
if ! start_analytics; then
    failed_services+=("analytics")
fi

# 4. Start Gateway
if ! start_gateway; then
    failed_services+=("gateway")
fi

# 5. Start Desktop App
if ! start_desktop_app; then
    failed_services+=("desktop")
fi

# Final health check
sleep 3
if check_all_services; then
    log_header "🎉 Demo Environment Ready!"

    echo "" | tee -a "$MAIN_LOG_FILE"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}" | tee -a "$MAIN_LOG_FILE"
    echo -e "${GREEN}║                    🌟 DEMO READY! 🌟                   ║${NC}" | tee -a "$MAIN_LOG_FILE"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}" | tee -a "$MAIN_LOG_FILE"
    echo "" | tee -a "$MAIN_LOG_FILE"

    echo -e "${CYAN}📱 Desktop App:${NC} http://localhost:3000" | tee -a "$MAIN_LOG_FILE"
    echo -e "${CYAN}🤖 Ollama API:${NC} http://localhost:11434" | tee -a "$MAIN_LOG_FILE"
    echo -e "${CYAN}📊 Analytics:${NC} http://localhost:8007" | tee -a "$MAIN_LOG_FILE"
    echo -e "${CYAN}🌐 Gateway:${NC} http://localhost:8009" | tee -a "$MAIN_LOG_FILE"
    echo "" | tee -a "$MAIN_LOG_FILE"

    echo -e "${YELLOW}📋 Demo Instructions:${NC}" | tee -a "$MAIN_LOG_FILE"
    echo "1. Open http://localhost:3000 in your browser" | tee -a "$MAIN_LOG_FILE"
    echo "2. Fill in candidate details (use 'test-001')" | tee -a "$MAIN_LOG_FILE"
    echo "3. Select role and AI model" | tee -a "$MAIN_LOG_FILE"
    echo "4. Click 'Start AI Interview'" | tee -a "$MAIN_LOG_FILE"
    echo "5. Answer questions to see analytics-enhanced results!" | tee -a "$MAIN_LOG_FILE"
    echo "" | tee -a "$MAIN_LOG_FILE"

    echo -e "${YELLOW}📝 Viewing Logs:${NC}" | tee -a "$MAIN_LOG_FILE"
    echo "tail -f $MAIN_LOG_FILE" | tee -a "$MAIN_LOG_FILE"
    echo "tail -f $LOG_DIR/*_${TIMESTAMP}.log" | tee -a "$MAIN_LOG_FILE"
    echo "" | tee -a "$MAIN_LOG_FILE"

    echo -e "${RED}🛑 Stop Demo:${NC} Press Ctrl+C" | tee -a "$MAIN_LOG_FILE"
    echo "" | tee -a "$MAIN_LOG_FILE"

    # Keep running
    wait
else
    log_error "Some services failed to start: ${failed_services[*]}"
    echo "" | tee -a "$MAIN_LOG_FILE"
    log_header "🔧 Troubleshooting"
    echo "1. Check logs: tail -f $LOG_DIR/*_${TIMESTAMP}.log" | tee -a "$MAIN_LOG_FILE"
    echo "2. Restart individual services manually" | tee -a "$MAIN_LOG_FILE"
    echo "3. Check port conflicts: lsof -i :8007,8009,3000,11434" | tee -a "$MAIN_LOG_FILE"
    exit 1
fi
<parameter name="filePath">/home/asif1/open-talent/start-demo.sh