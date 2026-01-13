#!/bin/bash

# Test runner script for User Service
# Runs unit and integration tests with coverage reporting

set -e

cd "$(dirname "$0")"

echo "========================================"
echo "User Service Test Suite"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker Compose is running
echo "Checking Docker Compose services..."
if ! docker ps | grep -q user_service_db; then
    echo -e "${YELLOW}Warning: user_service_db container not running${NC}"
    echo "Starting Docker Compose..."
    docker-compose up -d
    sleep 5
fi

# Activate virtual environment
if [ -d "/home/asif1/open-talent/.venv-1" ]; then
    source /home/asif1/open-talent/.venv-1/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    exit 1
fi

# Set PYTHONPATH to include current directory
export PYTHONPATH=.

# Run unit tests (fast, no DB required)
echo ""
echo "========================================"
echo "Running Unit Tests (JWT & Utils)"
echo "========================================"
PYTHONPATH=. pytest tests/test_jwt_utils.py -v --tb=short --cov=app --cov-report=term-missing

# Run integration tests (require DB)
echo ""
echo "========================================"
echo "Running Integration Tests (RLS Policies)"
echo "========================================"
PYTHONPATH=. pytest tests/test_rls_policies.py -v --tb=short -m integration

echo ""
echo "========================================"
echo "Running Integration Tests (API Endpoints)"
echo "========================================"
PYTHONPATH=. pytest tests/test_api_endpoints.py -v --tb=short -m integration

# Run all tests with coverage report
echo ""
echo "========================================"
echo "Full Test Suite with Coverage"
echo "========================================"
PYTHONPATH=. pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo -e "${GREEN}========================================"
echo "Test Suite Complete!"
echo "========================================"
echo ""
echo "Coverage report generated: htmlcov/index.html"
echo ""
echo "Test Summary:"
echo "- Unit tests: JWT verification, claims extraction, RBAC"
echo "- Integration tests: PostgreSQL RLS policies"
echo "- Integration tests: API endpoints with authentication"
echo ""
echo "To view coverage report:"
echo "  python -m http.server 8000 -d htmlcov"
echo "  Then open: http://localhost:8000"
echo -e "${NC}"
