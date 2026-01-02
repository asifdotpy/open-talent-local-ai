#!/bin/bash

# Avatar Integration Test Runner
# Starts all services and runs comprehensive integration tests

set -e

echo "🚀 Starting Avatar Integration Test Suite"
echo "=========================================="

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to the correct directory
cd "$(dirname "$0")"

# Stop any existing containers
print_status "Stopping existing containers..."
docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

# Start all services
print_status "Starting all services with docker-compose..."
docker compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    print_status "Checking $service_name at $url..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url/health" > /dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi

        echo -n "."
        sleep 2
        ((attempt++))
    done

    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Check all services
check_service "Voice Service" "http://localhost:8002" || exit 1
check_service "Conversation Service" "http://localhost:8003" || exit 1
check_service "Interview Service" "http://localhost:8004" || exit 1
check_service "Avatar Renderer" "http://localhost:3001" || exit 1
check_service "R3F Frontend" "http://localhost:3000" || exit 1

echo
print_success "All services are running and healthy!"
echo

# Install test dependencies if needed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js to run tests."
    exit 1
fi

# Install test dependencies
print_status "Installing test dependencies..."
npm install axios chai ws --save-dev

# Run integration tests
print_status "Running integration tests..."
if node test-avatar-integration.js; then
    print_success "All integration tests passed!"
    echo
    print_success "🎉 Avatar integration is complete and fully functional!"
    echo
    print_status "Services are still running. You can access:"
    echo "  • R3F Frontend: http://localhost:3000"
    echo "  • Voice Service: http://localhost:8002"
    echo "  • Interview Service: http://localhost:8004"
    echo "  • Avatar Renderer: http://localhost:3001"
    echo
    print_status "To stop all services, run: docker compose -f docker-compose.prod.yml down"
else
    print_error "Integration tests failed!"
    echo
    print_status "Checking service logs..."
    docker compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi
