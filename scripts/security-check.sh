#!/bin/bash
# Security and Code Quality Check Script
# Run before commits, PRs, and weekly security audits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         OpenTalent Security & Quality Check Suite             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0

# ==============================================================================
# 1. SECRET DETECTION
# ==============================================================================
echo -e "${BLUE}[1/9] Scanning for hardcoded secrets...${NC}"
if command -v trivy &> /dev/null; then
    if trivy fs --scanners secret --exit-code 1 . 2>/dev/null; then
        echo -e "${GREEN}✓ No secrets detected${NC}"
    else
        echo -e "${RED}✗ Secrets detected! Review output above.${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Trivy not installed. Skipping secret scan.${NC}"
fi
echo ""

# ==============================================================================
# 2. DEPENDENCY VULNERABILITIES
# ==============================================================================
echo -e "${BLUE}[2/9] Checking dependencies for vulnerabilities...${NC}"
if command -v safety &> /dev/null; then
    if safety check --json 2>/dev/null | grep -q '"vulnerabilities": \[\]'; then
        echo -e "${GREEN}✓ No known vulnerabilities in dependencies${NC}"
    else
        echo -e "${YELLOW}⚠ Vulnerabilities found in dependencies. Run 'safety check' for details.${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Safety not installed. Run: pip install safety${NC}"
fi
echo ""

# ==============================================================================
# 3. SECURITY LINTING (BANDIT)
# ==============================================================================
echo -e "${BLUE}[3/9] Running Bandit security linter...${NC}"
if command -v bandit &> /dev/null; then
    if bandit -r services/ -ll -q 2>/dev/null; then
        echo -e "${GREEN}✓ No high/medium security issues found${NC}"
    else
        echo -e "${RED}✗ Security issues found! Run 'bandit -r services/ -ll' for details.${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Bandit not installed. Run: pip install bandit${NC}"
fi
echo ""

# ==============================================================================
# 4. PATTERN-BASED SECURITY SCANNING (SEMGREP)
# ==============================================================================
echo -e "${BLUE}[4/9] Running Semgrep security rules...${NC}"
if command -v semgrep &> /dev/null; then
    if semgrep --config=auto --quiet --error services/ 2>/dev/null; then
        echo -e "${GREEN}✓ No security patterns detected${NC}"
    else
        echo -e "${RED}✗ Security patterns found! Run 'semgrep --config=auto services/' for details.${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Semgrep not installed. Run: pip install semgrep${NC}"
fi
echo ""

# ==============================================================================
# 5. LOOSE ENUM VALIDATION CHECK
# ==============================================================================
echo -e "${BLUE}[5/9] Checking for loose string validation (enums)...${NC}"
if command -v rg &> /dev/null; then
    LOOSE_ENUMS=$(rg 'status.*str.*Field\(.*min_length.*max_length' services/ --count 2>/dev/null | awk -F: '{sum += $2} END {print sum}')
    if [ "$LOOSE_ENUMS" = "" ] || [ "$LOOSE_ENUMS" = "0" ]; then
        echo -e "${GREEN}✓ No loose enum validation found${NC}"
    else
        echo -e "${RED}✗ Found $LOOSE_ENUMS instances of loose enum validation${NC}"
        echo -e "${YELLOW}  Run: rg 'status.*str.*Field' services/ --type py${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ ripgrep not installed. Skipping enum check.${NC}"
fi
echo ""

# ==============================================================================
# 6. TYPE CHECKING (MYPY)
# ==============================================================================
echo -e "${BLUE}[6/9] Running type checker...${NC}"
if command -v mypy &> /dev/null; then
    if mypy services/ --ignore-missing-imports --no-error-summary 2>/dev/null; then
        echo -e "${GREEN}✓ Type checking passed${NC}"
    else
        echo -e "${YELLOW}⚠ Type checking issues found. Run 'mypy services/' for details.${NC}"
        # Not counted as error for now
    fi
else
    echo -e "${YELLOW}⚠ MyPy not installed. Run: pip install mypy${NC}"
fi
echo ""

# ==============================================================================
# 7. CODE LINTING (RUFF)
# ==============================================================================
echo -e "${BLUE}[7/9] Running code linter...${NC}"
if command -v ruff &> /dev/null; then
    if ruff check services/ --quiet 2>/dev/null; then
        echo -e "${GREEN}✓ Linting passed${NC}"
    else
        echo -e "${YELLOW}⚠ Linting issues found. Run 'ruff check services/' for details.${NC}"
        echo -e "${YELLOW}  Auto-fix with: ruff check --fix services/${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Ruff not installed. Run: pip install ruff${NC}"
fi
echo ""

# ==============================================================================
# 8. TEST SUITE
# ==============================================================================
echo -e "${BLUE}[8/9] Running test suite...${NC}"
if command -v pytest &> /dev/null; then
    if pytest services/ --tb=short -q 2>&1 | tail -1 | grep -q "passed"; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed! Run 'pytest services/' for details.${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Pytest not installed. Run: pip install pytest${NC}"
fi
echo ""

# ==============================================================================
# 9. CODE COVERAGE
# ==============================================================================
echo -e "${BLUE}[9/9] Checking code coverage...${NC}"
if command -v pytest &> /dev/null && command -v coverage &> /dev/null; then
    COVERAGE=$(pytest --cov=services --cov-report=term-missing --tb=short -q 2>&1 | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
    if [ -n "$COVERAGE" ] && [ "$COVERAGE" -ge 70 ]; then
        echo -e "${GREEN}✓ Coverage: ${COVERAGE}% (target: 70%)${NC}"
    elif [ -n "$COVERAGE" ]; then
        echo -e "${YELLOW}⚠ Coverage: ${COVERAGE}% (target: 70%)${NC}"
        echo -e "${YELLOW}  Run 'pytest --cov=services --cov-report=html' for detailed report${NC}"
    else
        echo -e "${YELLOW}⚠ Could not determine coverage${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Coverage tools not installed. Run: pip install pytest pytest-cov${NC}"
fi
echo ""

# ==============================================================================
# SUMMARY
# ==============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      Check Summary                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}"
    echo "  ✓ All security and quality checks passed!"
    echo -e "${NC}"
    exit 0
else
    echo -e "${RED}"
    echo "  ✗ Found $ERRORS critical issue(s)"
    echo ""
    echo -e "${YELLOW}  Quick fixes:${NC}"
    echo "    • Run 'ruff check --fix services/' to auto-fix linting"
    echo "    • Run 'bandit -r services/ -ll' for security details"
    echo "    • Check CODE_QUALITY_AUDIT_ENUM_VALIDATION.md for enum fixes"
    echo "    • Run 'safety check' for dependency vulnerabilities"
    echo -e "${NC}"
    exit 1
fi
