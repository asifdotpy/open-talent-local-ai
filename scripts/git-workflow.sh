#!/bin/bash

# TalentAI Platform - Git Workflow Helper
# This script provides shortcuts for common Git operations

set -e

REPO_URL="https://github.com/asifdotpy/talent-ai-platform"
MAIN_BRANCH="main"
DEVELOP_BRANCH="develop"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a Git repository"
        exit 1
    fi
}

# Get current branch
get_current_branch() {
    git branch --show-current
}

# Check if branch is clean
is_branch_clean() {
    [ -z "$(git status --porcelain)" ]
}

# Sync with remote
sync_remote() {
    log_info "Syncing with remote..."
    git fetch --all --prune
    log_success "Remote synced"
}

# Create feature branch
create_feature_branch() {
    read -p "Enter feature name: " feature_name
    if [ -z "$feature_name" ]; then
        log_error "Feature name cannot be empty"
        exit 1
    fi

    branch_name="feature/${feature_name// /_}"
    log_info "Creating branch: $branch_name"
    git checkout -b "$branch_name"
    log_success "Branch created and checked out"
}

# Push and create PR
push_and_pr() {
    current_branch=$(get_current_branch)

    if [ "$current_branch" = "$MAIN_BRANCH" ] || [ "$current_branch" = "$DEVELOP_BRANCH" ]; then
        log_error "Cannot push directly to $current_branch. Create a feature branch first."
        exit 1
    fi

    if ! is_branch_clean; then
        log_warning "Branch has uncommitted changes. Commit or stash them first."
        exit 1
    fi

    log_info "Pushing branch: $current_branch"
    git push -u origin "$current_branch"

    pr_url="$REPO_URL/compare/$current_branch?expand=1"
    log_success "Branch pushed!"
    echo -e "${BLUE}🔗 Create PR at: $pr_url${NC}"
}

# Rebase from main
rebase_main() {
    current_branch=$(get_current_branch)

    if [ "$current_branch" = "$MAIN_BRANCH" ]; then
        log_error "Cannot rebase main onto itself"
        exit 1
    fi

    if ! is_branch_clean; then
        log_warning "Branch has uncommitted changes. Commit or stash them first."
        read -p "Stash changes? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash
            log_info "Changes stashed"
        else
            exit 1
        fi
    fi

    log_info "Rebasing $current_branch from origin/$MAIN_BRANCH"
    git fetch origin "$MAIN_BRANCH"
    git rebase "origin/$MAIN_BRANCH"
    log_success "Rebase completed"
}

# Check branch status
check_status() {
    current_branch=$(get_current_branch)
    echo -e "${BLUE}📍 Current branch:${NC} $current_branch"

    echo -e "${BLUE}📊 Status:${NC}"
    git status --short

    echo -e "${BLUE}🔄 Remote status:${NC}"
    git status -b --ahead-behind
}

# Clean workspace (dangerous!)
clean_workspace() {
    log_warning "This will remove all uncommitted changes and untracked files!"
    read -p "Are you sure? (type 'yes' to confirm): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Operation cancelled"
        exit 0
    fi

    log_info "Cleaning workspace..."
    git clean -fd
    git reset --hard HEAD
    log_success "Workspace cleaned"
}

# Show usage
usage() {
    echo "TalentAI Platform - Git Workflow Helper"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  sync          Sync with remote repository"
    echo "  feature       Create a new feature branch"
    echo "  push          Push current branch and show PR link"
    echo "  rebase        Rebase current branch from main"
    echo "  status        Show current branch status"
    echo "  clean         Clean workspace (removes uncommitted changes!)"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 sync"
    echo "  $0 feature"
    echo "  $0 push"
}

# Main script
main() {
    check_git_repo

    case "${1:-help}" in
        sync)
            sync_remote
            ;;
        feature)
            create_feature_branch
            ;;
        push)
            push_and_pr
            ;;
        rebase)
            rebase_main
            ;;
        status)
            check_status
            ;;
        clean)
            clean_workspace
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"