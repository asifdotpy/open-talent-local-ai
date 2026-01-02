#!/bin/bash

#
# Test Runner Script for AI Orchestra Simulation
# Coordinates execution of all test suites
#
# Usage:
#   ./tests/run-all-tests.sh              # Run all tests
#   ./tests/run-all-tests.sh --quick      # Quick tests only
#   ./tests/run-all-tests.sh --unit       # Unit tests only
#   ./tests/run-all-tests.sh --integration # Integration tests only
#

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_SKIPPED=0

print_header() {
  echo ""
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
  echo ""
}

print_section() {
  echo -e "${YELLOW}📋 $1${NC}"
}

run_test() {
  local test_file=$1
  local test_name=$2

  print_section "$test_name"

  if node "$test_file" 2>&1 | tee /tmp/test_output.txt; then
    TOTAL_PASSED=$((TOTAL_PASSED + 1))
    echo -e "${GREEN}✅ $test_name passed${NC}\n"
  else
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
    echo -e "${RED}❌ $test_name failed${NC}\n"
  fi
}

# Check arguments
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_E2E=true

case "${1:-all}" in
  --unit)
    RUN_INTEGRATION=false
    RUN_E2E=false
    ;;
  --integration)
    RUN_UNIT=false
    RUN_E2E=false
    ;;
  --e2e)
    RUN_UNIT=false
    RUN_INTEGRATION=false
    ;;
  --quick)
    RUN_E2E=false
    ;;
  all|--all)
    # Run everything
    ;;
  *)
    echo "Usage: $0 [--unit|--integration|--e2e|--quick|all]"
    exit 1
    ;;
esac

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

print_header "🧪 AI Orchestra Simulation - Test Suite"

# ============================================================================
# Unit Tests
# ============================================================================
if [ "$RUN_UNIT" = true ]; then
  print_header "UNIT TESTS"

  if [ -f "$SCRIPT_DIR/unit-core.test.js" ]; then
    run_test "$SCRIPT_DIR/unit-core.test.js" "Core Components"
  fi

  if [ -f "$SCRIPT_DIR/unit-animation.test.js" ]; then
    run_test "$SCRIPT_DIR/unit-animation.test.js" "Animation System"
  fi

  if [ -f "$SCRIPT_DIR/svg-math.test.js" ]; then
    run_test "$SCRIPT_DIR/svg-math.test.js" "SVG Math Utilities"
  fi
fi

# ============================================================================
# Integration Tests
# ============================================================================
if [ "$RUN_INTEGRATION" = true ]; then
  print_header "INTEGRATION TESTS"

  if [ -f "$SCRIPT_DIR/integration-config.test.js" ]; then
    run_test "$SCRIPT_DIR/integration-config.test.js" "Configuration System"
  fi

  if [ -f "$SCRIPT_DIR/integration-server.test.js" ]; then
    # Check if server is running
    if curl -s http://localhost:3001/health > /dev/null 2>&1; then
      run_test "$SCRIPT_DIR/integration-server.test.js" "Server API"
    else
      echo -e "${YELLOW}⏭️  Server API tests skipped (server not running on port 3001)${NC}"
      echo -e "   Start with: npm start\n"
    fi
  fi

  if [ -f "$SCRIPT_DIR/phase1-integration.test.js" ]; then
    run_test "$SCRIPT_DIR/phase1-integration.test.js" "Phase 1 Integration"
  fi

  if [ -f "$SCRIPT_DIR/live-streaming.test.js" ]; then
    run_test "$SCRIPT_DIR/live-streaming.test.js" "Live Streaming"
  fi
fi

# ============================================================================
# E2E Tests
# ============================================================================
if [ "$RUN_E2E" = true ]; then
  print_header "END-TO-END TESTS"

  if [ -f "$SCRIPT_DIR/e2e-face-glb.test.js" ] || [ -f "$SCRIPT_DIR/e2e-face-glb.js" ]; then
    TEST_FILE="${SCRIPT_DIR}/e2e-face-glb.js"
    [ ! -f "$TEST_FILE" ] && TEST_FILE="${SCRIPT_DIR}/e2e-face-glb.test.js"
    run_test "$TEST_FILE" "face.glb Integration"
  fi

  if [ -f "$SCRIPT_DIR/test-complete-pipeline.html" ]; then
    echo -e "${YELLOW}📋 Complete Pipeline (Browser)${NC}"
    echo -e "${YELLOW}   ℹ️  Open in browser: tests/test-complete-pipeline.html${NC}\n"
  fi
fi

# ============================================================================
# Summary
# ============================================================================
print_header "📊 Test Summary"

TOTAL_TESTS=$((TOTAL_PASSED + TOTAL_FAILED))

if [ $TOTAL_FAILED -eq 0 ] && [ $TOTAL_PASSED -gt 0 ]; then
  echo -e "${GREEN}✅ All tests passed!${NC}"
else
  echo -e "${RED}❌ Some tests failed${NC}"
fi

echo ""
echo "Results:"
echo "  ${GREEN}Passed:${NC} $TOTAL_PASSED"
echo "  ${RED}Failed:${NC} $TOTAL_FAILED"
echo "  ${YELLOW}Skipped:${NC} $TOTAL_SKIPPED"
echo ""

# Exit with appropriate code
if [ $TOTAL_FAILED -gt 0 ]; then
  exit 1
else
  exit 0
fi
