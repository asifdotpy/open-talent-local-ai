#!/bin/bash

# Deployment script for Avatar Service with Local LLM Support
# This script sets up both production and dev modes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_MODEL="granite4:350m-h"
PRODUCTION_MODEL="granite4:350m-h"
OLLAMA_DATA_PATH="/mnt/d/ollama-models"  # Use D: drive for models

print_step() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."

    # Check if running on the production server
    if [ ! -f "/proc/version" ] || ! grep -q "WSL2\|Linux" /proc/version; then
        print_warning "This script is designed for Linux/WSL2 environment"
    fi

    # Check for required directories
    if [ ! -d "/mnt/d" ]; then
        print_error "D: drive mount not found. Please ensure D: drive is accessible."
        exit 1
    fi

    # Check Docker availability
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

setup_ollama() {
    print_step "Setting up Ollama for production..."

    # Set environment variable for model storage
    export OLLAMA_MODELS="/mnt/d/ollama-models"

    # Create models directory if it doesn't exist
    mkdir -p "$OLLAMA_DATA_PATH"

    # Check if Ollama is running
    if ! pgrep -f "ollama" > /dev/null; then
        print_step "Starting Ollama service..."
        # Start Ollama in background
        nohup ollama serve > /var/log/ollama.log 2>&1 &
        sleep 5  # Wait for service to start
    fi

    # Check if current model is available
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "Model $OLLAMA_MODEL is available"
    else
        print_error "Model $OLLAMA_MODEL not found. Please run 'ollama pull $OLLAMA_MODEL' first"
        exit 1
    fi

    # If on production server with sufficient resources, suggest 70B model
    local available_memory=$(free -g | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available_memory" -gt 32 ]; then
        print_step "Production server detected. Checking for 70B model availability..."
        if ! ollama list | grep -q "$PRODUCTION_MODEL"; then
            print_warning "Consider upgrading to $PRODUCTION_MODEL for better performance"
            print_warning "Run: ollama pull $PRODUCTION_MODEL (requires ~40GB+ free space)"
        else
            print_success "$PRODUCTION_MODEL available for production use"
            OLLAMA_MODEL="$PRODUCTION_MODEL"
        fi
    fi
}

update_service_configuration() {
    print_step "Updating service configuration..."

    local deployment_mode=${1:-"production"}
    local env_file="open-talent-avatar-service/.env.${deployment_mode}"

    if [ "$deployment_mode" = "dev" ]; then
        print_info "Configuring for LOCAL LLM mode"
        cat > "$env_file" << EOF
# Local LLM Configuration
USE_LOCAL_LLM=true
OLLAMA_MODEL=$OLLAMA_MODEL
OLLAMA_BASE_URL=http://localhost:11434

# Service Configuration
ENVIRONMENT=dev
LOG_LEVEL=debug
EOF
    else
        print_info "Configuring for PRODUCTION mode"
        cat > "$env_file" << EOF
# Production Configuration
USE_LOCAL_LLM=false

# Service Configuration
ENVIRONMENT=production
LOG_LEVEL=info
EOF
    fi

    print_success "Environment configuration updated for $deployment_mode mode"
}

build_services() {
    print_step "Building services with hybrid integration..."

    # Build avatar service with new dependencies
    cd open-talent-avatar-service

    # Update requirements.txt if needed
    if ! grep -q "httpx" requirements.txt; then
        echo "httpx[http2]>=0.24.0" >> requirements.txt
        echo "python-dotenv>=0.19.0" >> requirements.txt
    fi

    # Build Docker image
    docker build -t open-talent-avatar-service:hybrid-latest .

    # Build other related services
    cd ../open-talent-interview-service
    docker build -t open-talent-interview-service:latest .

    print_success "Services built successfully"
}

run_tests() {
    print_step "Running integration tests..."

    cd open-talent-avatar-service

    # Make test script executable
    chmod +x test_hybrid_integration.py

    # Run tests
    if python test_hybrid_integration.py; then
        print_success "All integration tests passed"
    else
        print_error "Integration tests failed. Please check the logs."
        exit 1
    fi
}

deploy_services() {
    print_step "Deploying services..."

    # Create docker-compose override for production
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  avatar-service:
    image: open-talent-avatar-service:hybrid-latest
    environment:
      - OLLAMA_MODEL=$OLLAMA_MODEL
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - ENVIRONMENT=production
    volumes:
      - /mnt/d/ollama-models:/ollama-models:ro
    networks:
      - open-talent-network

  interview-service:
    image: open-talent-interview-service:latest
    depends_on:
      - avatar-service
    networks:
      - open-talent-network

networks:
  open-talent-network:
    external: true
EOF

    # Start services
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    print_success "Services deployed"
}

health_checks() {
    print_step "Performing health checks..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        print_step "Health check attempt $attempt/$max_attempts..."

        # Check Ollama
        if curl -s http://localhost:11434/api/tags > /dev/null; then
            print_success "Ollama service is healthy"
        else
            print_warning "Ollama service not responding"
        fi

        # Check Avatar service
        if docker ps | grep -q "avatar-service.*Up"; then
            print_success "Avatar service is running"
        else
            print_warning "Avatar service not running"
        fi

        # Check if services are responding
        sleep 5
        if curl -s http://localhost:8001/health > /dev/null; then  # Adjust port as needed
            print_success "All services are healthy and responding"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 10
    done

    print_error "Health checks failed after $max_attempts attempts"
    return 1
}

cleanup_old_deployments() {
    print_step "Cleaning up old deployments..."

    # Remove old containers
    docker container prune -f

    # Remove old images
    docker image prune -f

    print_success "Cleanup completed"
}

main() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "   TALENT AI HYBRID LLM DEPLOYMENT"
    echo "======================================"
    echo -e "${NC}"
    echo "Deploying Ollama + Anam hybrid system..."
    echo ""

    check_prerequisites
    setup_ollama
    update_service_configuration
    build_services
    run_tests
    deploy_services

    if health_checks; then
        cleanup_old_deployments

        echo ""
        echo -e "${GREEN}======================================"
        echo "   DEPLOYMENT COMPLETED SUCCESSFULLY"
        echo "======================================${NC}"
        echo ""
        echo "🚀 Hybrid LLM system is now running!"
        echo "📊 Current model: $OLLAMA_MODEL"
        echo "🔧 Local LLM: Ollama (localhost:11434)"
        echo "🎤 Voice: Local implementation (planned)"
        echo ""
        echo "Next steps:"
        echo "  • Test interview flow through frontend"
        echo "  • Monitor performance and response quality"
        echo "  • Consider upgrading to 70B model if resources allow"

    else
        print_error "Deployment completed but health checks failed"
        exit 1
    fi
}

# Run deployment if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
