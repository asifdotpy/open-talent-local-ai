#!/bin/bash
# OpenTalent Workspace Access Configuration
# This file provides easy access to OpenTalent project from any workspace
# Source this file in your shell: source /path/to/open-talent/WORKSPACE_ACCESS.sh

# Project Configuration
export OPENTALENT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export OPENTALENT_NAME="OpenTalent"
export OPENTALENT_VERSION="1.0.0-alpha"

# Quick Navigation Aliases
alias cd-ot="cd $OPENTALENT_ROOT"
alias cd-desktop="cd $OPENTALENT_ROOT/desktop-app"
alias cd-services="cd $OPENTALENT_ROOT/services"
alias cd-docs="cd $OPENTALENT_ROOT"

# Development Commands
alias ot-status="cd $OPENTALENT_ROOT && git status"
alias ot-pull="cd $OPENTALENT_ROOT && git pull origin master"
alias ot-push="cd $OPENTALENT_ROOT && git push origin master"
alias ot-dev="cd $OPENTALENT_ROOT/desktop-app && npm run dev"
alias ot-build="cd $OPENTALENT_ROOT/desktop-app && npm run build"
alias ot-test="cd $OPENTALENT_ROOT/desktop-app && npm test"

# Service Management
alias ot-start-demo="cd $OPENTALENT_ROOT && ./start-demo.sh"
alias ot-stop-demo="cd $OPENTALENT_ROOT && ./stop-demo.sh"
alias ot-verify-gateway="cd $OPENTALENT_ROOT && ./scripts/verify-gateway.sh"

# Environment Setup
alias ot-venv="source $OPENTALENT_ROOT/.venv-1/bin/activate"
alias ot-setup="cd $OPENTALENT_ROOT && pip install -r requirements.txt && cd desktop-app && npm install"

# Quick Info Functions
ot-info() {
    echo "=== OpenTalent Project Info ==="
    echo "Root: $OPENTALENT_ROOT"
    echo "Version: $OPENTALENT_VERSION"
    echo "Git Status:"
    cd $OPENTALENT_ROOT && git status --short
    echo ""
    echo "Available commands:"
    echo "  cd-ot, cd-desktop, cd-services, cd-docs"
    echo "  ot-status, ot-pull, ot-push"
    echo "  ot-dev, ot-build, ot-test"
    echo "  ot-start-demo, ot-stop-demo"
    echo "  ot-venv, ot-setup"
    echo "  ot-info (this message)"
}

ot-services() {
    echo "=== OpenTalent Services ==="
    echo "Available Services:"
    ls -1 $OPENTALENT_ROOT/services/
    echo ""
    echo "Microservices:"
    ls -1 $OPENTALENT_ROOT/microservices/
}

# Export for use in other scripts
export OPENTALENT_CONFIG_LOADED=1

echo "OpenTalent workspace access loaded. Type 'ot-info' for help."
