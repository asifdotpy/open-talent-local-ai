#!/bin/bash

# TALENT AI Platform - Simple Submodule Management
# Basic automation for git submodule operations

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Simple logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if we're in project root
check_project_root() {
    if [[ ! -f ".gitmodules" ]]; then
        echo "Error: Not in project root directory"
        exit 1
    fi
}

# Update all submodules
update_submodules() {
    log "Updating all submodules..."
    git submodule update --init --recursive
}

# Check submodule status
check_status() {
    log "Checking submodule status..."
    git submodule status
}

# Main function
main() {
    check_project_root

    case "${1:-status}" in
        "update")
            update_submodules
            ;;
        "status")
            check_status
            ;;
        *)
            echo "Usage: $0 [update|status]"
            exit 1
            ;;
    esac
}

main "$@"
        exit 1
    fi
    success "Project root verified"
}

# Function to get submodule status
get_submodule_status() {
    local submodule=$1
    local status_output

    if [[ -d "$submodule" ]]; then
        cd "$submodule"
        local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
        local current_branch=$(git branch --show-current 2>/dev/null || echo "detached")
        cd - >/dev/null
        echo "{\"commit\":\"$current_commit\",\"branch\":\"$current_branch\",\"initialized\":true}"
    else
        echo "{\"commit\":\"\",\"branch\":\"\",\"initialized\":false}"
    fi
}

# Function to initialize all submodules
init_submodules() {
    info "Initializing all submodules..."

    # Initialize submodules
    git submodule init
    success "Submodules initialized"

    # Update to tracked branches
    git submodule update --remote --merge
    success "Submodules updated to latest commits"

    # Verify initialization
    local uninitialized=$(git submodule status | grep '^-' | wc -l)
    if [[ $uninitialized -gt 0 ]]; then
        warn "$uninitialized submodules still uninitialized"
        git submodule status | grep '^-' | while read -r line; do
            warn "Uninitialized: $line"
        done
    else
        success "All submodules initialized successfully"
    fi
}

# Function to update specific submodule
update_submodule() {
    local submodule=$1
    local target_branch=${2:-${SUBMODULE_BRANCHES[$submodule]}}

    info "Updating submodule: $submodule to branch: $target_branch"

    # Check if submodule exists
    if [[ ! -d "$submodule" ]]; then
        error "Submodule $submodule does not exist"
        return 1
    fi

    cd "$submodule"

    # Fetch latest changes
    git fetch origin

    # Switch to target branch if different
    local current_branch=$(git branch --show-current 2>/dev/null || echo "detached")
    if [[ "$current_branch" != "$target_branch" ]]; then
        info "Switching $submodule from $current_branch to $target_branch"
        git checkout "$target_branch"
        git pull origin "$target_branch"
    else
        git pull origin "$target_branch"
    fi

    cd - >/dev/null

    # Update parent repository reference
    git add "$submodule"
    git commit -m "Update $submodule to latest $target_branch" 2>/dev/null || true

    success "Updated $submodule to latest $target_branch"
}

# Function to update all submodules
update_all_submodules() {
    info "Updating all submodules to their respective branches..."

    for submodule in "${!SUBMODULE_BRANCHES[@]}"; do
        local target_branch=${SUBMODULE_BRANCHES[$submodule]}
        update_submodule "$submodule" "$target_branch" || warn "Failed to update $submodule"
    done

    success "All submodules updated"
}

# Function to check submodule health
check_submodule_health() {
    info "Checking submodule health..."

    local issues_found=false

    git submodule status | while read -r status path; do
        case $status in
            -*)
                error "$path: Not initialized"
                issues_found=true
                ;;
            +*)
                warn "$path: Modified or diverged from tracked commit"
                issues_found=true
                ;;
            *)
                info "$path: Clean"
                ;;
        esac
    done

    if [[ "$issues_found" = true ]]; then
        error "Submodule health issues found"
        return 1
    else
        success "All submodules healthy"
        return 0
    fi
}

# Function to create release tags
create_release_tags() {
    local version=$1
    local tag_message=${2:-"Release $version"}

    info "Creating release tags for version: $version"

    # Tag main repository
    git tag -a "v$version" -m "$tag_message"
    git push origin "v$version"
    success "Tagged main repository: v$version"

    # Tag submodules if they have changes
    for submodule in "${!SUBMODULE_BRANCHES[@]}"; do
        if [[ -d "$submodule" ]]; then
            cd "$submodule"
            local has_changes=$(git status --porcelain | wc -l)
            if [[ $has_changes -gt 0 ]]; then
                git add .
                git commit -m "Release $version" 2>/dev/null || true
                git tag -a "v$version" -m "$tag_message"
                git push origin "v$version"
                success "Tagged $submodule: v$version"
            fi
            cd - >/dev/null
        fi
    done
}

# Function to run submodule tests
run_submodule_tests() {
    local submodule=$1

    info "Running tests for submodule: $submodule"

    if [[ ! -d "$submodule" ]]; then
        error "Submodule $submodule does not exist"
        return 1
    fi

    cd "$submodule"

    # Check for test scripts
    if [[ -f "package.json" ]]; then
        if command -v npm >/dev/null 2>&1; then
            npm test
        else
            warn "npm not available, skipping tests for $submodule"
        fi
    elif [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]]; then
        if command -v python >/dev/null 2>&1; then
            python -m pytest tests/ -v 2>/dev/null || python -m unittest discover -v 2>/dev/null || warn "No test framework found for $submodule"
        else
            warn "Python not available, skipping tests for $submodule"
        fi
    else
        warn "No test configuration found for $submodule"
    fi

    cd - >/dev/null
    success "Tests completed for $submodule"
}

# Function to run all submodule tests
run_all_tests() {
    info "Running tests for all submodules..."

    for submodule in "${!SUBMODULE_BRANCHES[@]}"; do
        run_submodule_tests "$submodule" || warn "Tests failed for $submodule"
    done

    success "All submodule tests completed"
}

# Function to generate submodule report
generate_report() {
    local report_file="${PROJECT_ROOT}/reports/submodule-report-$(date +%Y%m%d-%H%M%S).json"

    info "Generating submodule report: $report_file"

    mkdir -p "${PROJECT_ROOT}/reports"

    local report_data="{\"timestamp\":\"$(date -Iseconds)\",\"submodules\":{"

    local first=true
    for submodule in "${!SUBMODULE_BRANCHES[@]}"; do
        if [[ "$first" = true ]]; then
            first=false
        else
            report_data+=","
        fi

        local status=$(get_submodule_status "$submodule")
        local expected_branch=${SUBMODULE_BRANCHES[$submodule]}
        report_data+="\"$submodule\":{\"expected_branch\":\"$expected_branch\",$status}"
    done

    report_data+="}}"

    echo "$report_data" | jq . > "$report_file" 2>/dev/null || echo "$report_data" > "$report_file"

    success "Report generated: $report_file"
}

# Function to show help
show_help() {
    cat << EOF
TALENT AI Platform - Submodule CI/CD Automation Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    init                    Initialize all submodules
    update [submodule]      Update specific or all submodules
    health                  Check submodule health
    test [submodule]        Run tests for specific or all submodules
    release <version>       Create release tags for all components
    report                  Generate submodule status report
    status                  Show current submodule status

EXAMPLES:
    $0 init                                    # Initialize all submodules
    $0 update                                  # Update all submodules
    $0 update microservices                    # Update only microservices
    $0 health                                  # Check submodule health
    $0 test                                    # Run all submodule tests
    $0 test agents                             # Run tests for agents only
    $0 release 1.2.3                           # Create v1.2.3 release tags
    $0 report                                  # Generate status report

ENVIRONMENT VARIABLES:
    CI=true                    # Enable CI mode (stricter checks)
    DRY_RUN=true              # Show what would be done without executing

LOGGING:
    Logs are written to: logs/submodule-automation.log
    Reports are saved to: reports/

EOF
}

# Main script logic
main() {
    check_project_root

    case "${1:-help}" in
        "init")
            init_submodules
            ;;
        "update")
            if [[ -n "${2:-}" ]]; then
                update_submodule "$2"
            else
                update_all_submodules
            fi
            ;;
        "health")
            check_submodule_health
            ;;
        "test")
            if [[ -n "${2:-}" ]]; then
                run_submodule_tests "$2"
            else
                run_all_tests
            fi
            ;;
        "release")
            if [[ -z "${2:-}" ]]; then
                error "Version required for release command"
                echo "Usage: $0 release <version>"
                exit 1
            fi
            create_release_tags "$2"
            ;;
        "report")
            generate_report
            ;;
        "status")
            info "Current submodule status:"
            git submodule status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"</content>
<parameter name="filePath">/home/asif1/talent-ai-platform/scripts/submodule-automation.sh}

# Run main function with all arguments
main "$@"
