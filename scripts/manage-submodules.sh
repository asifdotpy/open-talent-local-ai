#!/bin/bash

# TALENT AI Platform - Submodule Management Helper Script
# This script helps manage Git submodules for the TALENT AI Platform

set -e

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f ".gitmodules" ]; then
        print_error "Not in the root of a Git repository with submodules"
        print_error "Please run this script from the open-talent-platform root directory"
        exit 1
    fi
    print_success "Found .gitmodules file"
}

# Function to display submodule status
show_submodule_status() {
    print_status "Current submodule status:"
    git submodule status
    echo
}

# Function to initialize all submodules
init_all_submodules() {
    print_status "Initializing all submodules..."
    git submodule update --init --recursive
    print_success "All submodules initialized"
}

# Function to update all submodules
update_all_submodules() {
    print_status "Updating all submodules to latest commits..."
    git submodule update --remote --merge
    print_success "All submodules updated"
}

# Function to check for uncommitted changes
check_uncommitted_changes() {
    print_status "Checking for uncommitted changes in submodules..."

    local has_changes=false

    git submodule foreach --quiet '
        if [ -n "$(git status --porcelain)" ]; then
            echo "Uncommitted changes in: $name"
            git status --short
            exit 1
        fi
    ' || has_changes=true

    if [ "$has_changes" = "true" ]; then
        print_warning "Found uncommitted changes in submodules"
        echo
        print_status "You can stash them with: ./scripts/manage-submodules.sh stash-all"
        return 1
    else
        print_success "No uncommitted changes found"
        return 0
    fi
}

# Function to stash all changes in submodules
stash_all_changes() {
    print_status "Stashing changes in all submodules..."
    git submodule foreach 'git stash push -m "Auto-stash from manage-submodules script"'
    print_success "All changes stashed"
}

# Function to open specific submodule in VS Code
open_submodule_in_vscode() {
    local submodule=$1
    if [ -z "$submodule" ]; then
        print_error "Please specify a submodule name"
        list_submodules
        return 1
    fi

    if [ -d "$submodule" ]; then
        print_status "Opening $submodule in VS Code..."
        code "$submodule"
        print_success "Opened $submodule in VS Code"
    else
        print_error "Submodule '$submodule' not found"
        list_submodules
    fi
}

# Function to list available submodules
list_submodules() {
    print_status "Available submodules:"
    git submodule foreach --quiet 'echo "  - $name"'
}

# Function to create VS Code workspace
create_vscode_workspace() {
    if [ -f "open-talent-platform.code-workspace" ]; then
        print_success "VS Code workspace file already exists"
    else
        print_error "VS Code workspace file not found"
        print_status "Please create open-talent-platform.code-workspace file first"
    fi

    print_status "To use the workspace:"
    echo "  code open-talent-platform.code-workspace"
}

# Function to show help
show_help() {
    echo "TALENT AI Platform - Submodule Management Helper"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  status          Show current submodule status"
    echo "  init            Initialize all submodules"
    echo "  update          Update all submodules to latest"
    echo "  check           Check for uncommitted changes"
    echo "  stash-all       Stash all changes in submodules"
    echo "  list            List available submodules"
    echo "  open <name>     Open specific submodule in VS Code"
    echo "  workspace       Information about VS Code workspace"
    echo "  help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 status                              # Show submodule status"
    echo "  $0 open open-talent-microservices         # Open microservices in VS Code"
    echo "  $0 update                              # Update all submodules"
}

# Main script logic
main() {
    check_directory

    case "${1:-help}" in
        "status")
            show_submodule_status
            ;;
        "init")
            init_all_submodules
            ;;
        "update")
            update_all_submodules
            ;;
        "check")
            check_uncommitted_changes
            ;;
        "stash-all")
            stash_all_changes
            ;;
        "list")
            list_submodules
            ;;
        "open")
            open_submodule_in_vscode "$2"
            ;;
        "workspace")
            create_vscode_workspace
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
