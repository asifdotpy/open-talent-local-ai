#!/bin/bash

# Service Testing Assessment Script
# This script checks test infrastructure and runs all service tests to get baseline status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICES_DIR="$ROOT_DIR/services"
REPORT_FILE="$ROOT_DIR/service_test_status_$(date +%Y%m%d_%H%M%S).md"

echo "# Service Test Status Report" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Activate virtual environment
if [ -d "$ROOT_DIR/.venv-1" ]; then
    source "$ROOT_DIR/.venv-1/bin/activate"
elif [ -d "$ROOT_DIR/.venv" ]; then
    source "$ROOT_DIR/.venv/bin/activate"
else
    echo "No virtual environment found. Please create one first."
    exit 1
fi

# List of all services
SERVICES=(
    "ai-auditing-service"
    "analytics-service"
    "avatar-service"
    "candidate-service"
    "conversation-service"
    "desktop-integration-service"
    "explainability-service"
    "granite-interview-service"
    "interview-service"
    "notification-service"
    "project-service"
    "scout-service"
    "security-service"
    "user-service"
    "voice-service"
)

echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Service | Tests Found | Test Count | Status |" >> "$REPORT_FILE"
echo "|---------|-------------|------------|--------|" >> "$REPORT_FILE"

for service in "${SERVICES[@]}"; do
    echo ""
    echo "========================================="
    echo "Analyzing: $service"
    echo "========================================="

    SERVICE_PATH="$SERVICES_DIR/$service"
    TESTS_PATH="$SERVICE_PATH/tests"

    if [ ! -d "$TESTS_PATH" ]; then
        echo "| $service | ❌ | 0 | No tests directory |" >> "$REPORT_FILE"
        continue
    fi

    # Count test files
    TEST_COUNT=$(find "$TESTS_PATH" -name "test_*.py" -type f | wc -l)

    echo "| $service | ✅ | $TEST_COUNT | Checking... |" >> "$REPORT_FILE"

    # Try to run tests
    echo "" >> "$REPORT_FILE"
    echo "### $service" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Test files: $TEST_COUNT" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    cd "$ROOT_DIR"

    # Run pytest for this service
    echo '```' >> "$REPORT_FILE"
    if python3 -m pytest "$SERVICE_PATH/tests" -v --tb=short --maxfail=5 2>&1 | tee -a "$REPORT_FILE"; then
        echo "✅ $service: TESTS PASSED"
    else
        echo "❌ $service: TESTS FAILED"
    fi
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
done

echo ""
echo "========================================="
echo "Report saved to: $REPORT_FILE"
echo "========================================="
cat "$REPORT_FILE"
