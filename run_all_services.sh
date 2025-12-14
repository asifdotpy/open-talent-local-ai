#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# OpenTalent Microservices Startup Script
# ═══════════════════════════════════════════════════════════════════════════
# This script starts all required microservices for testing
# Services:
#   - Avatar Service (port 8001)
#   - Voice Service (port 8002)
#   - Conversation Service (port 8003)
#   - Interview Service (port 8004)
#   - Granite Interview Service (port 8005)
#   - Analytics Service (port 8007)
# ═══════════════════════════════════════════════════════════════════════════

WORKSPACE="/home/asif1/open-talent"
MICROSERVICES_DIR="$WORKSPACE/microservices"
LOG_DIR="/tmp/opentalent-services"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Detect available Python versions
PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_312_BIN=""
if command -v python3.12 &> /dev/null; then
    PY_312_BIN="python3.12"
fi

# Service-specific Python versions
declare -A SERVICE_PY_VERSION=(
    ["avatar-service"]="$PY_312_BIN"
    ["voice-service"]="$PY_312_BIN"
    ["conversation-service"]="python3"
    ["interview-service"]="python3"
    ["analytics-service"]="python3"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$LOG_DIR"

# Main log file for all output
MAIN_LOG_FILE="$LOG_DIR/startup_${TIMESTAMP}.log"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║       OpenTalent - Start All Microservices             ║"
echo "║       Testing Application & Microservice Integration   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "Log file: $MAIN_LOG_FILE" | tee -a "$MAIN_LOG_FILE"

# Service configuration: name, port, directory
# granite-interview-service intentionally skipped for now
# to avoid heavy setup on fresh instances.
declare -a SERVICES=(
    "avatar-service:8001"
    "voice-service:8002"
    "conversation-service:8003"
    "interview-service:8004"
    "analytics-service:8007"
)
# Logging functions
log_info() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ${CYAN}ℹ${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_success() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ${GREEN}✅${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_error() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ${RED}❌${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_warning() {
    local msg="$1"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ${YELLOW}⚠${NC} $msg" | tee -a "$MAIN_LOG_FILE"
}

log_header() {
    local msg="$1"
    echo "" | tee -a "$MAIN_LOG_FILE"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$MAIN_LOG_FILE"
    echo -e "${CYAN}$msg${NC}" | tee -a "$MAIN_LOG_FILE"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$MAIN_LOG_FILE"
}

# Function to detect virtual environment
detect_venv() {
    local service_path="$1"
    
    if [ -d "$service_path/venv" ]; then
        echo "$service_path/venv"
    elif [ -d "$service_path/.venv" ]; then
        echo "$service_path/.venv"
    else
        echo ""
    fi
}

# Check prerequisites
check_prerequisites() {
    log_header "Checking Prerequisites"
    
    local missing_tools=0
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Python 3: $(python3 --version)"
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        log_error "pip not found"
        missing_tools=$((missing_tools + 1))
    else
        log_success "pip: Available"
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

# Function to check if port is already in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    fi
    return 1  # Port is free
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        log_warning "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local service_dir="$MICROSERVICES_DIR/$service_name"
    local log_file="$LOG_DIR/${service_name}_${TIMESTAMP}.log"

    log_info "Starting $service_name (port $port)..."

    if [ ! -d "$service_dir" ]; then
        log_error "$service_name directory not found at $service_dir"
        return 1
    fi

    # Check if port is in use
    if check_port $port; then
        log_warning "Port $port already in use, killing existing process..."
        kill_port $port
    fi

    # Detect virtual environment
    local venv_path=$(detect_venv "$service_dir")
    
    log_info "Service directory: $service_dir"
    
    # Ensure venv exists and has bin directory
    if [ -z "$venv_path" ] || [ ! -d "$venv_path/bin" ]; then
        log_warning "Virtual environment missing or incomplete. Recreating..."
        rm -rf "$service_dir/venv" "$service_dir/.venv"
        cd "$service_dir"
        if ! python3 -m venv venv 2>&1 | tee -a "$MAIN_LOG_FILE"; then
            log_error "Failed to create virtual environment for $service_name"
            return 1
        fi
        venv_path="$service_dir/venv"
    else
        log_info "Using existing venv: $venv_path"
    fi

    # Get Python executable from venv
    local python_exe="$venv_path/bin/python3"
    if [ ! -f "$python_exe" ]; then
        python_exe="$venv_path/bin/python"
    fi
    
    if [ ! -f "$python_exe" ]; then
        log_error "$service_name: Python executable not found in venv"
        return 1
    fi

    # Install requirements with robust fallbacks
    if [ -f "$service_dir/requirements.txt" ]; then
        log_info "Ensuring dependencies for $service_name (Python $PY_VERSION)..."
        "$python_exe" -m pip install --upgrade pip setuptools wheel -q 2>&1 | tee -a "$MAIN_LOG_FILE"

        # Prepare adjusted requirements for Python 3.13 compatibility
        local req_src="$service_dir/requirements.txt"
        local req_adj="$LOG_DIR/${service_name}_requirements_${TIMESTAMP}.txt"
        cp "$req_src" "$req_adj"
        if [[ "$PY_VERSION" == 3.13* ]]; then
            # Bump packages that lack 3.13 wheels
            sed -i -E 's/^moviepy==[0-9.]+/moviepy==2.2.1/' "$req_adj"
            sed -i -E 's/^Pillow==[0-9.]+/Pillow>=11.0.0/' "$req_adj"
            sed -i -E 's/^onnxruntime==[0-9.]+/onnxruntime>=1.23.2/' "$req_adj"
            sed -i -E 's/^psycopg2-binary==[0-9.]+/psycopg2-binary>=2.9.10/' "$req_adj"
            sed -i -E 's/^pydantic-core==[0-9.]+/pydantic-core>=2.41.5/' "$req_adj"
            sed -i -E 's/^pydantic==[0-9.]+/pydantic>=2.9.0/' "$req_adj"
        fi

        # First attempt: wheels only to avoid source builds
        if ! PIP_ONLY_BINARY=:all: "$python_exe" -m pip install -q -r "$req_adj" 2>&1 | tee -a "$MAIN_LOG_FILE"; then
            log_warning "$service_name: wheel-only install failed, retrying with source builds allowed"
            if ! "$python_exe" -m pip install -q -r "$req_adj" 2>&1 | tee -a "$MAIN_LOG_FILE"; then
                log_error "Failed to install requirements for $service_name"
                return 1
            fi
        fi
    fi

    # Determine main module for uvicorn
    local uvicorn_app=""
    if [ -f "$service_dir/main.py" ]; then
        uvicorn_app="main:app"
        log_info "Found main.py at service root"
    elif [ -f "$service_dir/app/main.py" ]; then
        uvicorn_app="app.main:app"
        log_info "Found main.py in app/ subdirectory"
    else
        log_error "$service_name: main.py not found at $service_dir/main.py or $service_dir/app/main.py"
        return 1
    fi

    # Get Python executable from venv
    local python_exe="$venv_path/bin/python3"
    if [ ! -f "$python_exe" ]; then
        python_exe="$venv_path/bin/python"
    fi
    
    if [ ! -f "$python_exe" ]; then
        log_error "$service_name: Python executable not found in venv"
        return 1
    fi
    
    log_info "Using Python: $python_exe"
    
    # Check if uvicorn is installed
    if ! "$python_exe" -m pip list 2>/dev/null | grep -q uvicorn; then
        log_warning "$service_name: uvicorn not installed, installing dependencies..."
        if [ -f "$service_dir/requirements.txt" ]; then
            "$python_exe" -m pip install -q -r "$service_dir/requirements.txt" 2>&1 | tee -a "$MAIN_LOG_FILE" || {
                log_error "Failed to install requirements for $service_name"
                return 1
            }
        else
            log_error "$service_name: requirements.txt not found"
            return 1
        fi
    fi

    # Start the service in background
    (
        cd "$service_dir"
        export PYTHONUNBUFFERED=1
        
        # Start service with uvicorn using full path to python
        "$python_exe" -m uvicorn "$uvicorn_app" --host 0.0.0.0 --port $port >> "$log_file" 2>&1
    ) &
    
    local pid=$!

    # Wait a moment for service to start
    sleep 2

    # Check if process is still running
    if kill -0 $pid 2>/dev/null; then
        log_success "$service_name started (PID: $pid)"
        echo "$service_name:$pid:$port" >> "$LOG_DIR/pids_${TIMESTAMP}.txt"
        return 0
    else
        # Process died, check log for errors
        log_error "$service_name failed to start (PID: $pid)"
        if [ -f "$log_file" ]; then
            log_error "Last 10 lines of $service_name log:"
            tail -n 10 "$log_file" | sed 's/^/  /' | tee -a "$MAIN_LOG_FILE"
        fi
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    log_info "Waiting for $service_name to be ready on port $port..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health &> /dev/null || \
           curl -s http://localhost:$port/docs &> /dev/null || \
           curl -s http://localhost:$port/ &> /dev/null; then
            log_success "$service_name is ready!"
            return 0
        fi

        sleep 1
        attempt=$((attempt + 1))
    done

    log_warning "$service_name did not respond to health check after ${max_attempts}s"
    return 1
}

# Cleanup function
cleanup() {
    log_header "Shutting Down Services"
    
    local pids_file="$LOG_DIR/pids_${TIMESTAMP}.txt"
    if [ -f "$pids_file" ]; then
        while IFS=':' read -r service_name pid port; do
            if kill -0 $pid 2>/dev/null; then
                log_info "Stopping $service_name (PID: $pid)..."
                kill $pid 2>/dev/null || true
            fi
        done < "$pids_file"
        
        sleep 1
        
        # Force kill any remaining processes
        while IFS=':' read -r service_name pid port; do
            if kill -0 $pid 2>/dev/null; then
                log_warning "Force killing $service_name (PID: $pid)..."
                kill -9 $pid 2>/dev/null || true
            fi
        done < "$pids_file"
    fi
    
    log_success "All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main execution
check_prerequisites

log_header "Starting All Microservices"

failed_services=()

for service in "${SERVICES[@]}"; do
    IFS=':' read -r service_name port <<< "$service"
    if ! start_service "$service_name" "$port"; then
        failed_services+=("$service_name")
    fi
done

# Wait a moment for services to start
log_info "Waiting for services to initialize..."
sleep 3

# Check health of all services
log_header "Checking Service Health"

for service in "${SERVICES[@]}"; do
    IFS=':' read -r service_name port <<< "$service"
    wait_for_service "$service_name" "$port"
done

# Print summary
log_header "📊 Service Startup Summary"

local_service_count=${#SERVICES[@]}
failed_count=${#failed_services[@]}
running_count=$((local_service_count - failed_count))

log_success "$running_count of $local_service_count services started successfully"

if [ $failed_count -gt 0 ]; then
    log_error "Failed services:"
    for service in "${failed_services[@]}"; do
        log_error "  - $service"
    done
fi

# Show service information
log_header "📍 Service Endpoints"
echo "Avatar Service:             http://localhost:8001" | tee -a "$MAIN_LOG_FILE"
echo "Voice Service:              http://localhost:8002" | tee -a "$MAIN_LOG_FILE"
echo "Conversation Service:       http://localhost:8003" | tee -a "$MAIN_LOG_FILE"
echo "Interview Service:          http://localhost:8004" | tee -a "$MAIN_LOG_FILE"
echo "Granite Interview Service:  http://localhost:8005" | tee -a "$MAIN_LOG_FILE"
echo "Analytics Service:          http://localhost:8007" | tee -a "$MAIN_LOG_FILE"

log_header "📝 Viewing Logs"
echo "Main startup log:           tail -f $MAIN_LOG_FILE" | tee -a "$MAIN_LOG_FILE"
echo "Specific service log:       tail -f $LOG_DIR/{service-name}_${TIMESTAMP}.log" | tee -a "$MAIN_LOG_FILE"
echo "List all log files:         ls -la $LOG_DIR/" | tee -a "$MAIN_LOG_FILE"

log_header "🛑 Stopping Services"
echo "Stop all services:          kill \$(cat $LOG_DIR/pids_${TIMESTAMP}.txt | cut -d: -f2)" | tee -a "$MAIN_LOG_FILE"
echo "Or press:                   Ctrl+C" | tee -a "$MAIN_LOG_FILE"

echo "" | tee -a "$MAIN_LOG_FILE"

if [ $failed_count -eq 0 ]; then
    log_success "🎉 All services started successfully!"
    echo "" | tee -a "$MAIN_LOG_FILE"
    echo -e "${BLUE}✨ Ready for testing! Use service endpoints above.${NC}" | tee -a "$MAIN_LOG_FILE"
    echo "" | tee -a "$MAIN_LOG_FILE"
    log_info "Press Ctrl+C to stop all services"
    
    # Keep the script running
    wait
else
    log_error "Failed to start: ${failed_services[*]}"
    echo "" | tee -a "$MAIN_LOG_FILE"
    log_header "🔧 Troubleshooting"
    echo "1. Check service logs: tail -f $LOG_DIR/<service_name>_${TIMESTAMP}.log" | tee -a "$MAIN_LOG_FILE"
    echo "2. Verify Python environment: python3 --version" | tee -a "$MAIN_LOG_FILE"
    echo "3. Check dependencies: pip list | grep -E 'fastapi|uvicorn'" | tee -a "$MAIN_LOG_FILE"
    exit 1
fi
