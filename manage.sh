#!/bin/bash

################################################################################
# OpenTalent Production Management Script
# Version: 1.0.0
#
# Usage:
#   ./manage.sh start    - Start all services
#   ./manage.sh stop     - Stop all services gracefully
#   ./manage.sh restart  - Restart all services
#   ./manage.sh status   - Check service health
################################################################################

set -e

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/.opentalent.pids"
VENV_PATH="$SCRIPT_DIR/.venv"

# Create necessary directories
mkdir -p "$LOG_DIR"

# Color codes for beautiful output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# Service definitions
declare -A SERVICES=(
    ["scout-service"]="8000"
    ["voice-service"]="8003"
    ["analytics-service"]="8007"
    ["gateway"]="8009"
)

DESKTOP_PORT="3000"

################################################################################
# Logging Functions
################################################################################

log_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║  $1${NC}"
    echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_progress() {
    echo -e "${MAGENTA}⏳ $1${NC}"
}

################################################################################
# Service Management Functions
################################################################################

check_prerequisites() {
    log_progress "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi

    # Check virtual environment
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        log_info "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi

    log_success "All prerequisites met"
}

start_microservice() {
    local service_name=$1
    local port=$2
    local service_dir=""

    # Find service directory
    if [ -d "services/$service_name" ]; then
        service_dir="services/$service_name"
    elif [ -d "microservices/$service_name" ]; then
        service_dir="microservices/$service_name"
    else
        log_error "Service directory not found for $service_name"
        return 1
    fi

    log_progress "Starting $service_name on port $port..."

    # Determine main module
    local uvicorn_app=""
    if [ -f "$service_dir/main.py" ]; then
        uvicorn_app="main:app"
    elif [ -f "$service_dir/app/main.py" ]; then
        uvicorn_app="app.main:app"
    else
        log_error "main.py not found for $service_name"
        return 1
    fi

    # Start service
    (
        cd "$service_dir"
        source "$VENV_PATH/bin/activate"
        python -m uvicorn "$uvicorn_app" \
            --host 0.0.0.0 \
            --port "$port" \
            --log-level warning \
            >> "$LOG_DIR/${service_name}.log" 2>&1
    ) &

    local pid=$!
    echo "$service_name:$pid:$port" >> "$PID_FILE"

    # Wait and verify
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        log_success "$service_name started (PID: $pid, Port: $port)"
        return 0
    else
        log_error "$service_name failed to start"
        return 1
    fi
}

start_desktop() {
    log_progress "Starting Desktop Application..."

    (
        cd desktop-app
        npm run dev >> "$LOG_DIR/desktop-app.log" 2>&1
    ) &

    local pid=$!
    echo "desktop-app:$pid:$DESKTOP_PORT" >> "$PID_FILE"

    sleep 3
    if kill -0 $pid 2>/dev/null; then
        log_success "Desktop App started (PID: $pid, Port: $DESKTOP_PORT)"
        return 0
    else
        log_error "Desktop App failed to start"
        return 1
    fi
}

check_service_health() {
    local service_name=$1
    local port=$2
    local max_attempts=15
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/health" &> /dev/null || \
           curl -s "http://localhost:$port/docs" &> /dev/null || \
           curl -s "http://localhost:$port/" &> /dev/null; then
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    return 1
}

################################################################################
# Main Commands
################################################################################

cmd_start() {
    log_header "🚀 OpenTalent - Starting Production Environment"

    check_prerequisites

    # Check if already running
    if [ -f "$PID_FILE" ]; then
        log_warning "Services may already be running. Run './manage.sh stop' first."
        log_info "Or remove $PID_FILE if stale"
        exit 1
    fi

    # Create new PID file
    true > "$PID_FILE"

    local failed_services=()

    # Start microservices
    log_info "Starting microservices layer..."
    for service in "${!SERVICES[@]}"; do
        if ! start_microservice "$service" "${SERVICES[$service]}"; then
            failed_services+=("$service")
        fi
    done

    # Wait for services to be fully ready
    log_progress "Waiting for services to be healthy..."
    sleep 3

    # Health check
    log_info "Performing health checks..."
    for service in "${!SERVICES[@]}"; do
        if check_service_health "$service" "${SERVICES[$service]}"; then
            log_success "$service is healthy"
        else
            log_warning "$service health check timed out (may still be starting)"
        fi
    done

    # Start desktop app
    log_info "Starting desktop application..."
    if ! start_desktop; then
        failed_services+=("desktop-app")
    fi

    # Final report
    echo ""
    log_header "📊 Startup Summary"

    if [ ${#failed_services[@]} -eq 0 ]; then
        log_success "All services started successfully! 🎉"
        echo ""
        echo -e "${BOLD}${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${GREEN}║         🌟 OpenTalent is Ready for Demo! 🌟               ║${NC}"
        echo -e "${BOLD}${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${CYAN}📱 Desktop App:${NC}      http://localhost:$DESKTOP_PORT"
        echo -e "${CYAN}🌐 API Gateway:${NC}      http://localhost:8009"
        echo -e "${CYAN}📊 Analytics:${NC}        http://localhost:8007"
        echo ""
        log_info "To stop: ./manage.sh stop"
        log_info "To check status: ./manage.sh status"
        echo ""
    else
        log_error "Some services failed to start: ${failed_services[*]}"
        echo ""
        log_info "Check logs in: $LOG_DIR/"
        exit 1
    fi
}

cmd_stop() {
    log_header "🛑 OpenTalent - Stopping Services"

    if [ ! -f "$PID_FILE" ]; then
        log_warning "No PID file found. Services may not be running."
        exit 0
    fi

    local stopped=0
    local failed=0

    while IFS=':' read -r service_name pid port; do
        if [ -z "$pid" ]; then
            continue
        fi

        if kill -0 "$pid" 2>/dev/null; then
            log_progress "Stopping $service_name (PID: $pid)..."

            # Graceful shutdown - SIGTERM
            kill "$pid" 2>/dev/null || true

            # Wait up to 5 seconds for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 0.5
                count=$((count + 1))
            done

            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                log_warning "Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null || true
            fi

            log_success "$service_name stopped"
            stopped=$((stopped + 1))
        else
            log_info "$service_name (PID: $pid) not running"
        fi
    done < "$PID_FILE"

    # Remove PID file
    rm -f "$PID_FILE"

    echo ""
    log_success "Stopped $stopped service(s)"
    log_success "All services have been shut down gracefully"
}

cmd_status() {
    log_header "📊 OpenTalent - Service Status"

    if [ ! -f "$PID_FILE" ]; then
        log_warning "No PID file found. Services are not running."
        exit 0
    fi

    local running=0
    local stopped=0

    echo ""
    printf "%-25s %-10s %-8s %-10s\n" "SERVICE" "STATUS" "PORT" "HEALTH"
    printf "%-25s %-10s %-8s %-10s\n" "-------" "------" "----" "------"

    while IFS=':' read -r service_name pid port; do
        if [ -z "$pid" ]; then
            continue
        fi

        local status="●"
        local health="N/A"

        if kill -0 "$pid" 2>/dev/null; then
            status="${GREEN}● Running${NC}"
            running=$((running + 1))

            # Check health
            if [ -n "$port" ] && curl -s "http://localhost:$port/health" &> /dev/null; then
                health="${GREEN}✓ Healthy${NC}"
            elif [ -n "$port" ] && curl -s "http://localhost:$port/" &> /dev/null; then
                health="${YELLOW}? Responding${NC}"
            else
                health="${RED}✗ No response${NC}"
            fi
        else
            status="${RED}● Stopped${NC}"
            stopped=$((stopped + 1))
        fi

        printf "%-25s %-20s %-8s %-20s\n" "$service_name" "$(echo -e $status)" "$port" "$(echo -e $health)"
    done < "$PID_FILE"

    echo ""
    log_info "Running: $running | Stopped: $stopped"
    echo ""
}

cmd_restart() {
    log_header "🔄 OpenTalent - Restarting Services"

    cmd_stop
    sleep 2
    cmd_start
}

cmd_logs() {
    local service=${1:-""}

    if [ -z "$service" ]; then
        log_info "Available logs:"
        ls -lh "$LOG_DIR"/*.log 2>/dev/null || log_warning "No log files found"
        echo ""
        log_info "Usage: ./manage.sh logs <service-name>"
        log_info "Example: ./manage.sh logs gateway"
    else
        local log_file="$LOG_DIR/${service}.log"
        if [ -f "$log_file" ]; then
            tail -f "$log_file"
        else
            log_error "Log file not found: $log_file"
        fi
    fi
}

################################################################################
# Main Entry Point
################################################################################

main() {
    local command=${1:-""}

    case "$command" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        logs)
            cmd_logs "${2:-}"
            ;;
        *)
            echo ""
            log_header "OpenTalent Management Script"
            echo "Usage: $0 {start|stop|restart|status|logs}"
            echo ""
            echo "Commands:"
            echo "  start    - Start all OpenTalent services"
            echo "  stop     - Stop all services gracefully"
            echo "  restart  - Restart all services"
            echo "  status   - Check service health and status"
            echo "  logs     - View service logs (specify service name)"
            echo ""
            echo "Examples:"
            echo "  $0 start"
            echo "  $0 status"
            echo "  $0 logs gateway"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
