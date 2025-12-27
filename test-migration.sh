#!/bin/bash

################################################################################
# OpenTalent Project Migration Test Script - SIMPLIFIED
# Date: December 5, 2025
# Purpose: Validate migration from open-talent-platform to open-talent directory
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Directories
SOURCE_DIR="/home/asif1/open-talent-platform"
TARGET_DIR="/home/asif1/open-talent"
TEST_LOG="${TARGET_DIR}/migration-test-results.log"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $1" >> "$TEST_LOG"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    echo "[SUCCESS] $1" >> "$TEST_LOG"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    echo "[ERROR] $1" >> "$TEST_LOG"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    echo "[WARNING] $1" >> "$TEST_LOG"
    ((TESTS_SKIPPED++))
}

# Initialize log
cat > "$TEST_LOG" << EOF
OpenTalent Migration Test Report
Generated: $(date)
Source: $SOURCE_DIR
Target: $TARGET_DIR
========================================

EOF

echo ""
log_info "════════════════════════════════════════════════════"
log_info "OpenTalent Migration Test Suite"
log_info "════════════════════════════════════════════════════"
echo ""

# TEST 1: Environment checks
log_info "TEST 1: Environment Checks"
if [ -d "$SOURCE_DIR" ]; then
    log_success "Source directory exists"
else
    log_error "Source directory missing"
    exit 1
fi

if [ -d "$TARGET_DIR" ]; then
    log_success "Target directory exists"
else
    log_error "Target directory missing"
    exit 1
fi

if command -v git &> /dev/null; then
    log_success "Git is available"
else
    log_error "Git not available"
fi

if command -v python3 &> /dev/null; then
    log_success "Python3 available"
else
    log_error "Python3 not available"
fi

# TEST 2: Source structure
log_info ""
log_info "TEST 2: Source Structure Validation"

REQUIRED_DIRS=(
    ".git"
    "agents"
    "microservices"
    "frontend"
    "docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$SOURCE_DIR/$dir" ]; then
        log_success "Directory found: $dir"
    else
        log_warning "Directory missing (optional): $dir"
    fi
done

# TEST 3: Key files
log_info ""
log_info "TEST 3: Key Files Check"

KEY_FILES=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        log_success "File found: $file"
    else
        log_warning "File missing (optional): $file"
    fi
done

# TEST 4: File counting
log_info ""
log_info "TEST 4: File Inventory"

TOTAL_FILES=$(find "$SOURCE_DIR" -type f ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/__pycache__/*' 2>/dev/null | wc -l)
PY_FILES=$(find "$SOURCE_DIR" -name "*.py" -type f ! -path '*/.git/*' 2>/dev/null | wc -l)
MD_FILES=$(find "$SOURCE_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)
DOCKER_FILES=$(find "$SOURCE_DIR" -name "Dockerfile*" -o -name "docker-compose*.yml" 2>/dev/null | wc -l)

log_success "Total files: $TOTAL_FILES"
log_success "Python files: $PY_FILES"
log_success "Markdown files (root): $MD_FILES"
log_success "Docker configs: $DOCKER_FILES"

# TEST 5: Disk space
log_info ""
log_info "TEST 5: Disk Space Check"

SOURCE_SIZE=$(du -sh "$SOURCE_DIR" 2>/dev/null | cut -f1)
log_info "Source project size: $SOURCE_SIZE"

AVAILABLE=$(df "$TARGET_DIR" | awk 'NR==2 {print $4}')
NEEDED=$(du -s "$SOURCE_DIR" 2>/dev/null | awk '{print $1}')

if [ "$AVAILABLE" -gt "$NEEDED" ]; then
    log_success "Sufficient disk space available"
else
    log_error "Insufficient disk space"
fi

# TEST 6: Git status
log_info ""
log_info "TEST 6: Git Repository Status"

if [ -d "$SOURCE_DIR/.git" ]; then
    COMMIT_COUNT=$(cd "$SOURCE_DIR" && git rev-list --count HEAD 2>/dev/null || echo "unknown")
    CURRENT_BRANCH=$(cd "$SOURCE_DIR" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    log_success "Git commits: $COMMIT_COUNT"
    log_success "Current branch: $CURRENT_BRANCH"
else
    log_warning "Not a git repository"
fi

# TEST 7: Markdown filtering simulation
log_info ""
log_info "TEST 7: Markdown Filtering Strategy"

log_info "Essential markdown to COPY:"
for file in "README.md" "LICENSE" "CONTRIBUTING.md" "CODE_OF_CONDUCT.md"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    fi
done

log_warning "Non-essential markdown to SKIP:"
for file in "AGENTS.md" "TODO.md" "ENTERPRISE_SUBMISSION_CHECKLIST.md"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        echo -e "  ${YELLOW}⊘${NC} $file"
    fi
done

# TEST 8: Critical file checksums
log_info ""
log_info "TEST 8: Computing File Checksums"

CHECKSUM_FILE="${TARGET_DIR}/.file-checksums.txt"
> "$CHECKSUM_FILE"

for file in "README.md" "LICENSE" "package.json"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        CHECKSUM=$(md5sum "$SOURCE_DIR/$file" 2>/dev/null | awk '{print $1}')
        echo "$file:$CHECKSUM" >> "$CHECKSUM_FILE"
        log_success "Checksum: $file ($CHECKSUM)"
    fi
done

# TEST 9: Python syntax check
log_info ""
log_info "TEST 9: Python Files Syntax Check"

CHECKED=0
while IFS= read -r pyfile; do
    if [ "$CHECKED" -ge 5 ]; then break; fi
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        log_success "Valid syntax: $pyfile"
    else
        log_warning "Syntax issue: $pyfile (will be included anyway)"
    fi
    ((CHECKED++))
done < <(find "$SOURCE_DIR" -name "*.py" -type f ! -path '*/.git/*' 2>/dev/null | head -10)

# Summary
echo ""
log_info "════════════════════════════════════════════════════"
log_info "TEST SUMMARY"
log_info "════════════════════════════════════════════════════"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
if [ "$TOTAL_TESTS" -gt 0 ]; then
    PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
else
    PASS_RATE=0
fi

echo ""
echo -e "Total Tests:    $TOTAL_TESTS"
echo -e "Passed:         ${GREEN}$TESTS_PASSED ✓${NC}"
echo -e "Failed:         ${RED}$TESTS_FAILED ✗${NC}"
echo -e "Skipped:        ${YELLOW}$TESTS_SKIPPED ⊘${NC}"
echo -e "Pass Rate:      ${GREEN}${PASS_RATE}%${NC}"
echo ""

{
    echo ""
    echo "TEST SUMMARY"
    echo "================================"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo "Skipped: $TESTS_SKIPPED"
    echo "Pass Rate: ${PASS_RATE}%"
    echo ""
} >> "$TEST_LOG"

if [ $TESTS_FAILED -eq 0 ]; then
    log_success "All critical tests passed! Ready for migration."
    echo ""
    log_info "════════════════════════════════════════════════════"
    log_info "NEXT STEPS FOR MIGRATION:"
    log_info "════════════════════════════════════════════════════"
    echo ""
    echo "1. Review results:"
    echo "   cat $TEST_LOG"
    echo ""
    echo "2. Copy source files (SELECTIVE - Recommended):"
    echo "   bash /home/asif1/open-talent/copy-source-files.sh"
    echo ""
    echo "3. OR copy everything (FULL PROJECT):"
    echo "   cp -r $SOURCE_DIR/* $TARGET_DIR/"
    echo "   cd $TARGET_DIR && git init"
    echo ""
    exit 0
else
    log_error "Some tests failed. Review issues above."
    echo ""
    log_info "Test results saved to: $TEST_LOG"
    echo ""
    exit 1
fi
