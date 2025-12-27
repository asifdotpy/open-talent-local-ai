#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  OpenTalent Production Deployment - vLLM + Conversation Service          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

echo "🚀 Deploying OpenTalent Production Stack with vLLM"
echo "================================================="

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VLLM_DIR="$PROJECT_ROOT/infrastructure/vllm-server"
CONVERSATION_DIR="$PROJECT_ROOT/microservices/conversation-service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check NVIDIA GPU support
    if ! nvidia-smi &> /dev/null; then
        log_warn "NVIDIA GPU not detected. vLLM will run on CPU (much slower)."
        GPU_AVAILABLE=false
    else
        log_info "NVIDIA GPU detected - optimal for vLLM performance"
        GPU_AVAILABLE=true
    fi
}

setup_environment() {
    log_info "Setting up environment variables..."

    # Create .env files if they don't exist
    if [ ! -f "$CONVERSATION_DIR/.env" ]; then
        cp "$CONVERSATION_DIR/.env.example" "$CONVERSATION_DIR/.env"
        log_info "Created conversation service .env file"
    fi

    # Update conversation service to use vLLM
    sed -i 's/LLM_PROVIDER=.*/LLM_PROVIDER=vllm/' "$CONVERSATION_DIR/.env"
    sed -i 's/LLM_BASE_URL=.*/LLM_BASE_URL=http:\/\/vllm-server:8000\/v1/' "$CONVERSATION_DIR/.env"
    sed -i 's/LLM_LORA_ADAPTER=.*/LLM_LORA_ADAPTER=technical/' "$CONVERSATION_DIR/.env"

    log_info "Updated conversation service configuration for vLLM"
}

build_vllm_server() {
    log_info "Building vLLM server..."

    cd "$VLLM_DIR"

    # Build the Docker image
    docker build -t OpenTalent-vllm-server .

    log_info "vLLM server image built successfully"
}

start_services() {
    log_info "Starting production services..."

    cd "$PROJECT_ROOT"

    # Create docker-compose override for production
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  vllm-server:
    extends:
      file: infrastructure/vllm-server/docker-compose.yml
      service: vllm-server
    environment:
      - HF_TOKEN=\${HF_TOKEN}
    volumes:
      - vllm-models:/models
      - ./infrastructure/vllm-server/vllm-config.yaml:/app/vllm-config.yaml:ro
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  conversation-service:
    build:
      context: ./microservices/conversation-service
      dockerfile: Dockerfile
    ports:
      - "8003:8003"
    environment:
      - SERVICE_PORT=8003
      - HOST=0.0.0.0
    env_file:
      - ./microservices/conversation-service/.env
    depends_on:
      - vllm-server
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped

volumes:
  vllm-models:
    driver: local

networks:
  default:
    name: OpenTalent-network
EOF

    # Start services
    if [ "$GPU_AVAILABLE" = true ]; then
        log_info "Starting services with GPU support..."
        docker-compose -f docker-compose.prod.yml up -d
    else
        log_warn "Starting services without GPU (CPU mode)..."
        docker-compose -f docker-compose.prod.yml up -d
    fi
}

wait_for_services() {
    log_info "Waiting for services to be ready..."

    # Wait for vLLM server
    log_info "Waiting for vLLM server..."
    timeout=300
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_info "✅ vLLM server is ready"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
    done

    if [ $elapsed -ge $timeout ]; then
        log_error "vLLM server failed to start within $timeout seconds"
        exit 1
    fi

    # Wait for conversation service
    log_info "Waiting for conversation service..."
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -f http://localhost:8003/health &> /dev/null; then
            log_info "✅ Conversation service is ready"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
    done

    if [ $elapsed -ge $timeout ]; then
        log_error "Conversation service failed to start within $timeout seconds"
        exit 1
    fi
}

test_deployment() {
    log_info "Testing deployment..."

    # Test conversation service health
    if curl -f http://localhost:8003/health &> /dev/null; then
        log_info "✅ Conversation service health check passed"
    else
        log_error "❌ Conversation service health check failed"
        exit 1
    fi

    # Test generate-questions endpoint
    response=$(curl -s -X POST http://localhost:8003/api/v1/conversation/generate-questions \
        -H 'Content-Type: application/json' \
        -d '{"job_requirements": "Python, Django, React", "num_questions": 2}')

    if [ $? -eq 0 ] && [ -n "$response" ]; then
        log_info "✅ Question generation test passed"
        echo "Sample response: ${response:0:100}..."
    else
        log_error "❌ Question generation test failed"
        exit 1
    fi
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    echo "📊 Services:"
    docker-compose -f docker-compose.prod.yml ps

    echo ""
    echo "🔍 Service URLs:"
    echo "  • vLLM Server: http://localhost:8000"
    echo "  • Conversation Service: http://localhost:8003"
    echo "  • API Docs: http://localhost:8003/docs"

    echo ""
    echo "🧪 Test Commands:"
    echo "  curl http://localhost:8003/health"
    echo "  curl -X POST http://localhost:8003/api/v1/conversation/generate-questions \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"job_requirements\": \"Python, Django\", \"num_questions\": 3}'"

    echo ""
    echo "🎭 Switch Interviewer Personas:"
    echo "  1. Technical:  sed -i 's/LLM_LORA_ADAPTER=.*/LLM_LORA_ADAPTER=technical/' .env"
    echo "  2. Behavioral: sed -i 's/LLM_LORA_ADAPTER=.*/LLM_LORA_ADAPTER=behavioral/' .env"
    echo "  3. HR:         sed -i 's/LLM_LORA_ADAPTER=.*/LLM_LORA_ADAPTER=hr/' .env"
    echo "  Then restart: docker-compose -f docker-compose.prod.yml restart conversation-service"
}

# Main deployment flow
main() {
    log_info "Starting OpenTalent production deployment..."

    check_dependencies
    setup_environment
    build_vllm_server
    start_services
    wait_for_services
    test_deployment
    show_status

    log_info "🎉 OpenTalent production deployment completed successfully!"
    log_info "Your AI interviewer platform is now running with vLLM!"
}

# Run main function
main "$@"
