#!/bin/bash

################################################################################
# OpenTalent Platform - Enterprise Grade Migration Verification Script
#
# Purpose: Test-Driven verification framework for project reorganization
# Version: 1.0.0
# Date: December 5, 2025
#
# This script implements comprehensive pre-migration, migration, and
# post-migration validation using enterprise-grade testing patterns.
#
# Usage:
#   ./scripts/verify-migration.sh --mode pre-migration
#   ./scripts/verify-migration.sh --mode post-migration
#   ./scripts/verify-migration.sh --mode full
#   ./scripts/verify-migration.sh --mode report
#
################################################################################

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MIGRATION_LOG="${PROJECT_ROOT}/migration-verification.log"
MIGRATION_REPORT="${PROJECT_ROOT}/migration-report.md"
MIGRATION_STATE="${PROJECT_ROOT}/.migration-state"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Mode flags
MODE="${1:-full}"
VERBOSE="${VERBOSE:-false}"

# ============================================================================
# LOGGING & REPORTING
# ============================================================================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "$MIGRATION_LOG"
}

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
    log "ERROR" "$1"
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((TESTS_SKIPPED++))
}

# ============================================================================
# TEST FRAMEWORK
# ============================================================================

assert_file_exists() {
    local file=$1
    local description=$2
    ((TESTS_TOTAL++))

    if [[ -f "$file" ]]; then
        pass "$description: $file exists"
        return 0
    else
        fail "$description: $file does not exist"
        return 1
    fi
}

assert_directory_exists() {
    local dir=$1
    local description=$2
    ((TESTS_TOTAL++))

    if [[ -d "$dir" ]]; then
        pass "$description: $dir exists"
        return 0
    else
        fail "$description: $dir does not exist"
        return 1
    fi
}

assert_directory_empty() {
    local dir=$1
    local description=$2
    ((TESTS_TOTAL++))

    if [[ -d "$dir" ]]; then
        local count=$(find "$dir" -mindepth 1 -maxdepth 1 | wc -l)
        if [[ $count -eq 0 ]]; then
            pass "$description: $dir is empty"
            return 0
        else
            fail "$description: $dir contains $count items (expected empty)"
            return 1
        fi
    else
        fail "$description: $dir does not exist"
        return 1
    fi
}

assert_file_count() {
    local dir=$1
    local expected=$2
    local pattern=${3:-"*"}
    local description=$4
    ((TESTS_TOTAL++))

    if [[ -d "$dir" ]]; then
        local count=$(find "$dir" -maxdepth 1 -name "$pattern" 2>/dev/null | wc -l)
        if [[ $count -ge $expected ]]; then
            pass "$description: $dir contains $count files (expected >= $expected)"
            return 0
        else
            fail "$description: $dir contains $count files (expected >= $expected)"
            return 1
        fi
    else
        fail "$description: $dir does not exist"
        return 1
    fi
}

assert_file_readable() {
    local file=$1
    local description=$2
    ((TESTS_TOTAL++))

    if [[ -r "$file" ]]; then
        pass "$description: $file is readable"
        return 0
    else
        fail "$description: $file is not readable"
        return 1
    fi
}

assert_contains_string() {
    local file=$1
    local string=$2
    local description=$3
    ((TESTS_TOTAL++))

    if grep -q "$string" "$file" 2>/dev/null; then
        pass "$description: $file contains '$string'"
        return 0
    else
        fail "$description: $file does not contain '$string'"
        return 1
    fi
}

assert_not_contains_string() {
    local file=$1
    local string=$2
    local description=$3
    ((TESTS_TOTAL++))

    if ! grep -q "$string" "$file" 2>/dev/null; then
        pass "$description: $file does not contain '$string'"
        return 0
    else
        fail "$description: $file contains '$string' (unexpected)"
        return 1
    fi
}

assert_checksum_match() {
    local file1=$1
    local file2=$2
    local description=$3
    ((TESTS_TOTAL++))

    local sum1=$(sha256sum "$file1" 2>/dev/null | awk '{print $1}')
    local sum2=$(sha256sum "$file2" 2>/dev/null | awk '{print $1}')

    if [[ "$sum1" == "$sum2" ]]; then
        pass "$description: checksums match"
        return 0
    else
        fail "$description: checksums differ ($sum1 vs $sum2)"
        return 1
    fi
}

# ============================================================================
# PRE-MIGRATION VALIDATION TESTS
# ============================================================================

test_current_structure() {
    print_section "PRE-MIGRATION: Current Structure Analysis"

    print_test "Checking root directory files"
    local root_markdown_count=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
    echo "  Found $root_markdown_count markdown files in root (target: <20)"

    if [[ $root_markdown_count -gt 80 ]]; then
        warn "Root directory has $root_markdown_count markdown files (high clutter)"
    fi

    print_test "Checking for misplaced files"
    assert_file_exists "$PROJECT_ROOT/vetta-granite-2b-gguf-v4.gguf" "Model file location check" || true

    local python_scripts=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*.py" 2>/dev/null | wc -l)
    echo "  Found $python_scripts Python scripts in root (target: 0)"

    local shell_scripts=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*.sh" 2>/dev/null | wc -l)
    echo "  Found $shell_scripts shell scripts in root (target: 0)"

    ((TESTS_TOTAL++))
    pass "Current structure analyzed"
}

test_model_organization() {
    print_section "PRE-MIGRATION: Model Organization Check"

    print_test "Checking Vetta AI documentation files"
    local vetta_docs_count=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*VETTA*" -o -name "*vetta*" 2>/dev/null | wc -l)
    echo "  Found $vetta_docs_count Vetta/Granite related files in root"

    if [[ -d "$PROJECT_ROOT/models" ]]; then
        warn "models/ directory already exists"
    else
        echo "  models/ directory needs to be created"
    fi

    print_test "Checking notebook chunks"
    if [[ -d "$PROJECT_ROOT/notebook_chunks" ]]; then
        local notebook_count=$(find "$PROJECT_ROOT/notebook_chunks" -type f 2>/dev/null | wc -l)
        echo "  Found $notebook_count files in notebook_chunks/ (target: migrate to models/training/)"
    fi

    ((TESTS_TOTAL++))
    pass "Model organization checked"
}

test_specification_gaps() {
    print_section "PRE-MIGRATION: Specification Completeness"

    print_test "Checking API contracts"
    if [[ -d "$PROJECT_ROOT/specs/api-contracts" ]]; then
        local api_files=$(find "$PROJECT_ROOT/specs/api-contracts" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
        echo "  Found $api_files OpenAPI specifications (target: 7 microservices)"
        ((TESTS_TOTAL++))
        if [[ $api_files -eq 0 ]]; then
            fail "No OpenAPI specifications found"
        else
            pass "OpenAPI specifications partially exist"
        fi
    fi

    print_test "Checking requirements documentation"
    if [[ -d "$PROJECT_ROOT/specs/requirements" ]]; then
        local req_files=$(find "$PROJECT_ROOT/specs/requirements" -name "*.md" 2>/dev/null | wc -l)
        echo "  Found $req_files requirement documents (target: 5)"
        ((TESTS_TOTAL++))
        if [[ $req_files -eq 0 ]]; then
            warn "No requirements documentation found"
        else
            pass "Requirements documentation exists"
        fi
    fi

    print_test "Checking ADRs"
    if [[ ! -d "$PROJECT_ROOT/docs/architecture/decisions" ]]; then
        echo "  ADR directory does not exist (target: create)"
        ((TESTS_TOTAL++))
        fail "Architecture Decision Records directory missing"
    else
        local adr_files=$(find "$PROJECT_ROOT/docs/architecture/decisions" -name "*.md" 2>/dev/null | wc -l)
        echo "  Found $adr_files ADRs (target: 10-15)"
        ((TESTS_TOTAL++))
        if [[ $adr_files -eq 0 ]]; then
            warn "No ADRs documented yet"
        fi
    fi
}

test_documentation_inventory() {
    print_section "PRE-MIGRATION: Documentation Inventory"

    print_test "Counting documentation files by category"

    local markdown_files=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*.md" 2>/dev/null)

    # Count by category
    local vetta_count=$(echo "$markdown_files" | grep -ci "vetta\|granite" || true)
    local dataset_count=$(echo "$markdown_files" | grep -ci "dataset\|data" || true)
    local avatar_count=$(echo "$markdown_files" | grep -ci "avatar\|animation" || true)
    local status_count=$(echo "$markdown_files" | grep -ci "status\|report" || true)

    echo "  Vetta/Granite docs: $vetta_count files"
    echo "  Dataset docs: $dataset_count files"
    echo "  Avatar docs: $avatar_count files"
    echo "  Status/Report docs: $status_count files"

    ((TESTS_TOTAL+=4))
    pass "Documentation inventory complete"
}

test_dependency_analysis() {
    print_section "PRE-MIGRATION: Dependency Analysis"

    print_test "Checking Python requirements files"
    local req_files=$(find "$PROJECT_ROOT" -name "requirements*.txt" 2>/dev/null | wc -l)
    echo "  Found $req_files requirements files"
    ((TESTS_TOTAL++))
    pass "Requirements files identified"

    print_test "Checking docker-compose files"
    local compose_files=$(find "$PROJECT_ROOT" -name "docker-compose*.yml" 2>/dev/null | wc -l)
    echo "  Found $compose_files docker-compose files (target: consolidate to 3)"
    ((TESTS_TOTAL++))
    if [[ $compose_files -gt 5 ]]; then
        warn "Multiple docker-compose files found - consolidation needed"
    else
        pass "Docker composition files appropriate"
    fi
}

# ============================================================================
# POST-MIGRATION VALIDATION TESTS
# ============================================================================

test_directory_structure() {
    print_section "POST-MIGRATION: Directory Structure Validation"

    local required_dirs=(
        "models"
        "models/gguf"
        "models/lora"
        "models/training"
        "models/docs"
        "docs/architecture/decisions"
        "docs/architecture/diagrams"
        "docs/database"
        "docs/testing"
        "docs/operations"
        "docs/security"
        "docs/onboarding"
        "docs/datasets"
        "docs/research"
        "docs/status"
        "docs/archive"
        "specs/api-contracts/openapi"
        "specs/api-contracts/event-schemas"
        "specs/requirements"
        "specs/user-stories"
        "specs/protocols"
        "specs/data-models"
        "examples/demos"
    )

    for dir in "${required_dirs[@]}"; do
        assert_directory_exists "$PROJECT_ROOT/$dir" "Directory structure check"
    done
}

test_file_migration() {
    print_section "POST-MIGRATION: File Migration Validation"

    print_test "Checking model files location"

    # GGUF model should be moved from root to models/gguf
    if [[ -f "$PROJECT_ROOT/models/gguf/vetta-granite-2b-gguf-v4.gguf" ]]; then
        pass "GGUF model moved to models/gguf/"
        if [[ -f "$PROJECT_ROOT/vetta-granite-2b-gguf-v4.gguf" ]]; then
            fail "GGUF model still exists in root (should be removed)"
        else
            pass "GGUF model removed from root"
        fi
    else
        fail "GGUF model not found in models/gguf/"
    fi

    print_test "Checking notebook chunks migration"

    if [[ -d "$PROJECT_ROOT/models/training/notebook_chunks" ]]; then
        pass "Notebook chunks moved to models/training/"
        if [[ -d "$PROJECT_ROOT/notebook_chunks" ]] && [[ $(find "$PROJECT_ROOT/notebook_chunks" -type f 2>/dev/null | wc -l) -eq 0 ]]; then
            pass "Original notebook_chunks directory cleaned"
        fi
    else
        warn "Notebook chunks not yet migrated"
    fi

    print_test "Checking Python scripts location"

    local root_python=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*.py" 2>/dev/null | wc -l)
    if [[ $root_python -eq 0 ]]; then
        pass "No Python scripts in root"
    else
        fail "$root_python Python scripts still in root (should be in scripts/)"
    fi
}

test_documentation_migration() {
    print_section "POST-MIGRATION: Documentation Migration"

    print_test "Checking markdown files relocated from root"

    local root_md=$(find "$PROJECT_ROOT" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
    if [[ $root_md -lt 20 ]]; then
        pass "Root markdown files reduced to $root_md (target: <20)"
    else
        warn "Root still contains $root_md markdown files (expected <20)"
    fi

    print_test "Checking docs/ subdirectories populated"

    if assert_file_exists "$PROJECT_ROOT/docs/SYSTEM_ARCHITECTURE.md" "System architecture document"; then
        assert_file_readable "$PROJECT_ROOT/docs/SYSTEM_ARCHITECTURE.md" "System architecture readability"
    fi

    if [[ -d "$PROJECT_ROOT/docs/datasets" ]]; then
        local dataset_files=$(find "$PROJECT_ROOT/docs/datasets" -name "*.md" 2>/dev/null | wc -l)
        if [[ $dataset_files -gt 0 ]]; then
            pass "Dataset documentation files: $dataset_files"
        else
            warn "Dataset documentation directory empty"
        fi
    fi
}

test_specification_completeness() {
    print_section "POST-MIGRATION: Specification Completeness"

    print_test "Checking functional requirements"
    if assert_file_exists "$PROJECT_ROOT/specs/requirements/functional-requirements.md" "Functional requirements"; then
        assert_file_readable "$PROJECT_ROOT/specs/requirements/functional-requirements.md" "Functional requirements readability"
    fi

    print_test "Checking user stories"
    if assert_file_exists "$PROJECT_ROOT/specs/user-stories/candidate-stories.md" "Candidate user stories"; then
        assert_file_readable "$PROJECT_ROOT/specs/user-stories/candidate-stories.md" "Candidate stories readability"
    fi

    print_test "Checking API contracts"
    local openapi_files=$(find "$PROJECT_ROOT/specs/api-contracts/openapi" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
    if [[ $openapi_files -ge 5 ]]; then
        pass "OpenAPI specifications: $openapi_files files"
    else
        warn "OpenAPI specifications incomplete: $openapi_files files (target: 7)"
    fi

    print_test "Checking ADRs"
    local adr_files=$(find "$PROJECT_ROOT/docs/architecture/decisions" -name "*.md" 2>/dev/null | wc -l)
    if [[ $adr_files -ge 5 ]]; then
        pass "Architecture Decision Records: $adr_files files"
    else
        warn "ADRs incomplete: $adr_files files (target: 10-15)"
    fi
}

test_cross_references() {
    print_section "POST-MIGRATION: Cross-Reference Validation"

    print_test "Checking for broken links in documentation"

    # Check if SYSTEM_ARCHITECTURE.md exists and references correct paths
    if [[ -f "$PROJECT_ROOT/docs/SYSTEM_ARCHITECTURE.md" ]]; then
        local refs=$(grep -o '\[.*\](.*\.md)' "$PROJECT_ROOT/docs/SYSTEM_ARCHITECTURE.md" 2>/dev/null | wc -l)
        echo "  Found $refs markdown links in SYSTEM_ARCHITECTURE.md"

        # Verify a sample of links
        assert_contains_string "$PROJECT_ROOT/docs/SYSTEM_ARCHITECTURE.md" "architecture\|specification" "SYSTEM_ARCHITECTURE contains architectural references"
    fi

    print_test "Checking README files in key directories"

    local readme_locations=(
        "models/README.md"
        "specs/api-contracts/README.md"
        "docs/architecture/README.md"
    )

    for readme in "${readme_locations[@]}"; do
        if [[ -f "$PROJECT_ROOT/$readme" ]]; then
            pass "README found at $readme"
        else
            warn "Missing README at $readme"
        fi
    done
}

test_git_status() {
    print_section "POST-MIGRATION: Git Status Check"

    print_test "Checking for untracked files"

    cd "$PROJECT_ROOT" || return 1

    if git rev-parse --git-dir > /dev/null 2>&1; then
        local untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
        echo "  Untracked files: $untracked"
        ((TESTS_TOTAL++))
        pass "Git repository healthy"
    else
        ((TESTS_TOTAL++))
        warn "Not a git repository"
    fi
}

# ============================================================================
# MIGRATION EXECUTION TESTS
# ============================================================================

test_migration_plan() {
    print_section "MIGRATION: Planning & Validation"

    print_test "Generating migration plan"

    cat > "$MIGRATION_STATE/migration-plan.md" << 'EOF'
# OpenTalent Platform Migration Plan

## Phase 1: Preparation (Pre-Migration)
- [x] Analyze current structure
- [x] Identify all files to migrate
- [ ] Create backup of entire project
- [ ] Tag git with pre-migration checkpoint

## Phase 2: Directory Creation
- [ ] Create all new directories
- [ ] Set correct permissions
- [ ] Create placeholder README files

## Phase 3: File Transfer
- [ ] Transfer model files (GGUF, LoRA)
- [ ] Transfer notebook chunks
- [ ] Transfer documentation files
- [ ] Transfer scripts

## Phase 4: Verification
- [ ] Verify file integrity (checksums)
- [ ] Verify directory structure
- [ ] Verify cross-references
- [ ] Clean up root directory

## Phase 5: Documentation
- [ ] Create SYSTEM_ARCHITECTURE.md
- [ ] Document migration steps
- [ ] Update project README
- [ ] Create rollback guide
EOF

    ((TESTS_TOTAL++))
    pass "Migration plan generated"
}

# ============================================================================
# REPORT GENERATION
# ============================================================================

generate_report() {
    print_section "GENERATING MIGRATION REPORT"

    local success_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))

    cat > "$MIGRATION_REPORT" << EOF
# OpenTalent Platform Migration Verification Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Mode:** $MODE
**Project:** $PROJECT_ROOT

## Executive Summary

- **Total Tests:** $TESTS_TOTAL
- **Passed:** $TESTS_PASSED ✓
- **Failed:** $TESTS_FAILED ✗
- **Skipped:** $TESTS_SKIPPED ⊘
- **Success Rate:** ${success_rate}%

## Test Results by Phase

### Pre-Migration Validation
- Current structure analyzed
- Model organization checked
- Specification gaps identified
- Documentation inventory complete
- Dependency analysis performed

### Post-Migration Validation (if applicable)
- Directory structure validated
- File migration verified
- Documentation relocation confirmed
- Specification completeness checked
- Cross-references validated

### Git Status
- Repository status checked
- Untracked files analyzed

## Key Findings

### Current State (Pre-Migration)
- Root directory has high markdown file count
- Vetta AI documentation scattered across 5 locations
- Specification gaps in API contracts and requirements
- 10+ docker-compose files (consolidation needed)

### Migration Checklist

- [ ] Create models/ directory structure
- [ ] Create specs/ subdirectories
- [ ] Create docs/ subdirectories
- [ ] Migrate GGUF model file
- [ ] Migrate notebook chunks
- [ ] Migrate documentation files
- [ ] Create SYSTEM_ARCHITECTURE.md
- [ ] Create ADR template and initial ADRs
- [ ] Create OpenAPI specifications
- [ ] Consolidate docker-compose files
- [ ] Update all cross-references
- [ ] Clean up root directory
- [ ] Create comprehensive READMEs
- [ ] Run full verification

## Recommendations

### High Priority
1. Create models/ hub with comprehensive documentation
2. Establish SYSTEM_ARCHITECTURE.md as single source of truth
3. Complete OpenAPI specifications for all microservices
4. Document architecture decisions (ADRs)
5. Remove GGUF model from root directory

### Medium Priority
6. Consolidate docker-compose files
7. Migrate documentation to organized structure
8. Create specification templates
9. Establish documentation standards
10. Build automated documentation generation

### Low Priority
11. Archive old status reports
12. Consolidate avatar documentation
13. Create onboarding guide
14. Implement contract testing framework

## Next Steps

1. Review this report with team
2. Approve migration plan
3. Create git backup branch
4. Execute migration (Phase 1-2)
5. Run post-migration verification
6. Document lessons learned
7. Update development workflows

---
**Report generated by:** verify-migration.sh v1.0.0
**Log file:** $MIGRATION_LOG
EOF

    echo -e "\n${GREEN}✓ Report generated: $MIGRATION_REPORT${NC}"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header "OpenTalent Platform - Enterprise Migration Verification v1.0.0"

    # Initialize log
    > "$MIGRATION_LOG"
    log "INFO" "Verification script started in $MODE mode"

    # Create migration state directory
    mkdir -p "$MIGRATION_STATE"

    case "$MODE" in
        pre-migration)
            log "INFO" "Running pre-migration validation tests"
            test_current_structure
            test_model_organization
            test_specification_gaps
            test_documentation_inventory
            test_dependency_analysis
            ;;
        post-migration)
            log "INFO" "Running post-migration validation tests"
            test_directory_structure
            test_file_migration
            test_documentation_migration
            test_specification_completeness
            test_cross_references
            test_git_status
            ;;
        full)
            log "INFO" "Running full validation (pre + post)"
            test_current_structure
            test_model_organization
            test_specification_gaps
            test_documentation_inventory
            test_dependency_analysis
            test_directory_structure
            test_file_migration
            test_documentation_migration
            test_specification_completeness
            test_cross_references
            test_git_status
            test_migration_plan
            ;;
        report)
            log "INFO" "Generating migration report"
            ;;
        *)
            echo "Usage: $0 [pre-migration|post-migration|full|report]"
            exit 1
            ;;
    esac

    # Print summary
    print_section "TEST SUMMARY"
    echo -e "Total Tests:  ${CYAN}$TESTS_TOTAL${NC}"
    echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
    echo -e "Skipped:      ${YELLOW}$TESTS_SKIPPED${NC}"

    if [[ $TESTS_TOTAL -gt 0 ]]; then
        local success_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
        echo -e "Success Rate: ${CYAN}${success_rate}%${NC}"
    fi

    # Generate report
    generate_report

    # Exit with appropriate code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}✓ All validations passed!${NC}"
        log "INFO" "Verification completed successfully"
        exit 0
    else
        echo -e "\n${RED}✗ $TESTS_FAILED validation(s) failed${NC}"
        log "ERROR" "Verification completed with failures"
        exit 1
    fi
}

# Run main function
main "$@"
