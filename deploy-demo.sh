#!/bin/bash

# OpenTalent MVP Demo Deployment Script
# This script deploys all services for client demos

set -e

echo "🎯 OpenTalent MVP Demo Deployment"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Check available resources
check_resources() {
    # Check available memory (need at least 2GB)
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available_mem" -lt 2048 ]; then
        print_warning "Available memory: ${available_mem}MB (recommended: 2048MB+)"
    else
        print_success "Available memory: ${available_mem}MB"
    fi

    # Check available disk space (need at least 5GB)
    local available_disk=$(df / | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    if [ "$available_disk" -lt 5 ]; then
        print_warning "Available disk space: ${available_disk}GB (recommended: 5GB+)"
    else
        print_success "Available disk space: ${available_disk}GB"
    fi
}

# Clean up existing containers
cleanup() {
    print_status "Cleaning up existing containers..."

    # Stop and remove existing containers
    docker compose -f docker-compose.prod.yml down --volumes --remove-orphans 2>/dev/null || true

    # Remove specific containers if they exist
    docker rm -f open-talent-postgres open-talent-avatar-renderer open-talent-interview-service open-talent-voice-service open-talent-conversation-service open-talent-ollama 2>/dev/null || true

    print_success "Cleanup completed"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."

    # Build all services
    docker compose -f docker-compose.prod.yml build

    # Start services
    docker compose -f docker-compose.prod.yml up -d

    print_success "Services started"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."

    local max_attempts=60
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo -n "."

        # Check if all services are healthy
        if docker compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
            local healthy_count=$(docker compose -f docker-compose.prod.yml ps | grep -c "healthy")
            local total_count=$(docker compose -f docker-compose.prod.yml ps | grep -c "Up")

            if [ "$healthy_count" -eq "$total_count" ] && [ "$total_count" -gt 0 ]; then
                echo ""
                print_success "All services are healthy!"
                return 0
            fi
        fi

        sleep 5
        attempt=$((attempt + 1))
    done

    echo ""
    print_error "Services failed to become healthy within 5 minutes"
    docker compose -f docker-compose.prod.yml logs
    return 1
}

# Run integration test
run_integration_test() {
    print_status "Running integration test..."

    # Wait a bit more for services to fully initialize
    sleep 10

    # Run the test
    if python microservices/test_complete_interview_flow.py; then
        print_success "Integration test passed!"
        return 0
    else
        print_error "Integration test failed!"
        return 1
    fi
}

# Display service status
show_status() {
    echo ""
    echo "📊 Service Status"
    echo "=================="

    docker compose -f docker-compose.prod.yml ps

    echo ""
    echo "🌐 Service Endpoints"
    echo "===================="
    echo "Avatar Renderer:    http://localhost:3001"
    echo "Interview Service:  http://localhost:8004"
    echo "Voice Service:      http://localhost:8002"
    echo "Conversation Service: http://localhost:8003"
    echo "PostgreSQL:         localhost:5432"
    echo "Ollama:            localhost:11434"

    echo ""
    echo "🩺 Health Checks"
    echo "================"
    for port in 3001 8004 8002 8003; do
        if curl -s -f http://localhost:$port/health >/dev/null 2>&1; then
            echo -e "Port $port: ${GREEN}✓ Healthy${NC}"
        else
            echo -e "Port $port: ${RED}✗ Unhealthy${NC}"
        fi
    done
}

# Main deployment function
main() {
    echo "Starting OpenTalent MVP deployment..."

    check_docker
    check_resources
    cleanup
    deploy_services

    if wait_for_services; then
        if run_integration_test; then
            show_status
            echo ""
            print_success "🎉 MVP deployment completed successfully!"
            echo ""
            echo "Ready for client demos! 🚀"
            echo ""
            echo "Quick demo commands:"
            echo "  docker compose -f docker-compose.prod.yml logs -f"
            echo "  docker compose -f docker-compose.prod.yml down"
        else
            print_error "Integration test failed. Check logs above."
            exit 1
        fi
    else
        print_error "Services failed to start properly."
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "test")
        run_integration_test
        ;;
    "logs")
        docker compose -f docker-compose.prod.yml logs -f
        ;;
    "stop")
        docker compose -f docker-compose.prod.yml down
        ;;
    *)
        main
        ;;
esac
