#!/bin/bash
# Voice Service Test Runner
# Quick reference for running different test types following TDD workflow

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Print usage
usage() {
    echo -e "${BLUE}Voice Service Test Runner${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  unit          - Run unit tests (fast, isolated, 90%+ coverage)"
    echo "  integration   - Run integration tests (services, 80%+ coverage)"
    echo "  business      - Run business value tests (user outcomes, 100% critical)"
    echo "  all           - Run all tests in sequence"
    echo "  coverage      - Generate detailed coverage report"
    echo "  watch         - Watch mode for TDD red-green-refactor cycle"
    echo "  tdd           - Run tests in TDD mode (fail fast, verbose)"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 unit                    # Quick validation (<30s)"
    echo "  $0 integration             # Full integration tests (<5min)"
    echo "  $0 business                # Business value validation (<30min)"
    echo "  $0 all                     # Complete test suite"
    echo "  $0 watch unit              # TDD mode for unit tests"
    echo ""
}

# Run unit tests (fast, isolated)
run_unit() {
    echo -e "${GREEN}Running Unit Tests (90%+ coverage goal, <30s)${NC}"
    pytest tests/unit/ \
        -v \
        --cov=services \
        --cov-report=term-missing \
        --cov-fail-under=90 \
        --tb=short \
        --strict-markers \
        -m unit \
        "$@"
}

# Run integration tests (service interactions)
run_integration() {
    echo -e "${BLUE}Running Integration Tests (API validation, <5min)${NC}"
    
    # Check if service is running
    if ! curl -f http://localhost:8002/health &>/dev/null; then
        echo -e "${YELLOW}Warning: Voice service not running on port 8002${NC}"
        echo "Start with: docker-compose up -d voice-service"
        echo "Or run locally: python -m uvicorn app.main:app --port 8002"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    pytest tests/integration/ \
        -v \
        --tb=short \
        --strict-markers \
        -m integration \
        "$@"
}

# Run business value tests (user journeys)
run_business() {
    echo -e "${YELLOW}Running Business Value Tests (100% critical paths, <30min)${NC}"
    
    # Check if all services are running
    echo "Checking required services..."
    services_ok=true
    
    if ! curl -f http://localhost:8002/health &>/dev/null; then
        echo -e "${RED}✗ Voice service not running (port 8002)${NC}"
        services_ok=false
    else
        echo -e "${GREEN}✓ Voice service running${NC}"
    fi
    
    if ! curl -f http://localhost:8003/health &>/dev/null; then
        echo -e "${RED}✗ Conversation service not running (port 8003)${NC}"
        services_ok=false
    else
        echo -e "${GREEN}✓ Conversation service running${NC}"
    fi
    
    if ! curl -f http://localhost:8001/health &>/dev/null; then
        echo -e "${RED}✗ Avatar service not running (port 8001)${NC}"
        services_ok=false
    else
        echo -e "${GREEN}✓ Avatar service running${NC}"
    fi
    
    if [ "$services_ok" = false ]; then
        echo ""
        echo "Start all services with: docker-compose up -d"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    pytest tests/business/ \
        -v \
        --tb=long \
        --strict-markers \
        -m business \
        "$@"
}

# Run all tests
run_all() {
    echo -e "${BLUE}Running Complete Test Suite${NC}"
    echo ""
    
    echo -e "${GREEN}Phase 1: Unit Tests${NC}"
    run_unit
    echo ""
    
    echo -e "${BLUE}Phase 2: Integration Tests${NC}"
    run_integration
    echo ""
    
    echo -e "${YELLOW}Phase 3: Business Value Tests${NC}"
    run_business
    echo ""
    
    echo -e "${GREEN}✓ All tests completed successfully!${NC}"
}

# Generate coverage report
run_coverage() {
    echo -e "${BLUE}Generating Coverage Report${NC}"
    pytest tests/ \
        --cov=services \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-report=xml \
        -v
    
    echo ""
    echo -e "${GREEN}Coverage report generated:${NC}"
    echo "  HTML: file://$(pwd)/htmlcov/index.html"
    echo "  XML:  $(pwd)/coverage.xml"
    echo ""
    
    # Open in browser if available
    if command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    elif command -v open &> /dev/null; then
        open htmlcov/index.html
    fi
}

# TDD watch mode
run_watch() {
    test_type="${1:-unit}"
    echo -e "${GREEN}TDD Watch Mode: $test_type tests${NC}"
    echo "Watching for changes... (Ctrl+C to stop)"
    echo ""
    
    if ! command -v pytest-watch &> /dev/null; then
        echo -e "${YELLOW}Installing pytest-watch...${NC}"
        pip install pytest-watch
    fi
    
    case $test_type in
        unit)
            ptw tests/unit/ -- -v --tb=short -m unit
            ;;
        integration)
            ptw tests/integration/ -- -v --tb=short -m integration
            ;;
        business)
            ptw tests/business/ -- -v --tb=long -m business
            ;;
        *)
            echo -e "${RED}Invalid test type: $test_type${NC}"
            echo "Use: unit, integration, or business"
            exit 1
            ;;
    esac
}

# TDD mode (fail fast, verbose)
run_tdd() {
    echo -e "${GREEN}TDD Mode: Red-Green-Refactor Cycle${NC}"
    pytest tests/unit/ \
        -v \
        --tb=short \
        --strict-markers \
        -x \
        --ff \
        -m unit \
        "$@"
}

# Main command dispatcher
case "${1:-help}" in
    unit)
        shift
        run_unit "$@"
        ;;
    integration)
        shift
        run_integration "$@"
        ;;
    business)
        shift
        run_business "$@"
        ;;
    all)
        shift
        run_all "$@"
        ;;
    coverage)
        shift
        run_coverage "$@"
        ;;
    watch)
        shift
        run_watch "$@"
        ;;
    tdd)
        shift
        run_tdd "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        usage
        exit 1
        ;;
esac
