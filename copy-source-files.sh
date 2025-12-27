#!/bin/bash

################################################################################
# OpenTalent Project - Selective Source Files Copy
# Date: December 5, 2025
# Purpose: Copy only source code files (no unnecessary markdown)
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directories
SOURCE_DIR="/home/asif1/open-talent-platform"
TARGET_DIR="/home/asif1/open-talent"
COPY_LOG="${TARGET_DIR}/migration-copy.log"

# Counters
FILES_COPIED=0
DIRS_CREATED=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $1" >> "$COPY_LOG"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    echo "[SUCCESS] $1" >> "$COPY_LOG"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    echo "[ERROR] $1" >> "$COPY_LOG"
}

log_skip() {
    echo -e "${YELLOW}[⊘]${NC} $1"
    echo "[SKIP] $1" >> "$COPY_LOG"
}

# Initialize log
cat > "$COPY_LOG" << EOF
OpenTalent Selective File Copy Log
Generated: $(date)
Source: $SOURCE_DIR
Target: $TARGET_DIR
Strategy: Copy source code files, skip unnecessary markdown
========================================

EOF

echo ""
log_info "════════════════════════════════════════════════════"
log_info "Starting Selective File Copy"
log_info "════════════════════════════════════════════════════"
echo ""

# Create directories structure
log_info "Creating directory structure..."

DIRS_TO_CREATE=(
    "agents"
    "agents/shared"
    "agents/genkit-service"
    "agents/interviewer-agent"
    "agents/scout-coordinator-agent"
    "agents/proactive-scanning-agent"
    "agents/boolean-mastery-agent"
    "agents/personalized-engagement-agent"
    "agents/market-intelligence-agent"
    "agents/tool-leverage-agent"
    "agents/quality-focused-agent"
    "microservices"
    "microservices/voice-service"
    "microservices/avatar-service"
    "microservices/conversation-service"
    "microservices/interview-service"
    "microservices/integration-service"
    "frontend"
    "frontend/landing-page"
    "frontend/admin-panel"
    "frontend/dashboard"
    "infrastructure"
    "infrastructure/docker-compose"
    "infrastructure/docker-compose/nginx"
    "infrastructure/docker-compose/scripts"
    "infrastructure/vllm-server"
    "specs"
    "specs/api-contracts"
    "specs/architectural-specs"
    "specs/protocols"
    "specs/requirements"
    "specs/user-stories"
    "docs"
    "docs/api-specs"
    "docs/development"
    "docs/plans"
    "docs/updates"
    "docs/progress"
    "scripts"
    "research"
    "assets"
    ".github"
    ".github/workflows"
    ".github/ISSUE_TEMPLATE"
)

for dir in "${DIRS_TO_CREATE[@]}"; do
    if mkdir -p "$TARGET_DIR/$dir" 2>/dev/null; then
        ((DIRS_CREATED++))
    fi
done

log_success "Created $DIRS_CREATED directories"
echo ""

# Copy function - copies matching files with exclusions
copy_files_by_extension() {
    local ext=$1
    local desc=$2
    local count=0

    log_info "Copying $desc files..."
    while IFS= read -r file; do
        mkdir -p "$(dirname "${TARGET_DIR}/${file#$SOURCE_DIR/}")"
        cp "$file" "${TARGET_DIR}/${file#$SOURCE_DIR/}" 2>/dev/null || true
        ((count++))
    done < <(find "$SOURCE_DIR" -name "*$ext" -type f ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.pytest_cache/*' ! -path '*/build/*' ! -path '*/dist/*' ! -path '*/.egg-info/*')

    log_success "Copied $count $desc files"
}

# Copy Python files
copy_files_by_extension ".py" "Python"

# Copy JavaScript/TypeScript
copy_files_by_extension ".js" "JavaScript"
copy_files_by_extension ".ts" "TypeScript"
copy_files_by_extension ".tsx" "TypeScript/React"
copy_files_by_extension ".jsx" "JavaScript/React"

# Copy configuration files
copy_files_by_extension ".json" "JSON config"
copy_files_by_extension ".yaml" "YAML config"
copy_files_by_extension ".yml" "YAML config"
copy_files_by_extension ".toml" "TOML config"
copy_files_by_extension ".ini" "INI config"

# Copy Docker files
log_info "Copying Docker files..."
find "$SOURCE_DIR" \( -name "Dockerfile*" -o -name "docker-compose*.yml" \) ! -path '*/.git/*' -type f | while read -r file; do
    mkdir -p "$(dirname "${TARGET_DIR}/${file#$SOURCE_DIR/}")"
    cp "$file" "${TARGET_DIR}/${file#$SOURCE_DIR/}" 2>/dev/null || true
done
log_success "Docker files copied"

# Copy shell scripts
copy_files_by_extension ".sh" "Shell scripts"

# Copy environment templates
log_info "Copying .env templates..."
find "$SOURCE_DIR" -name ".env*" ! -name ".env" ! -path '*/.git/*' -type f | while read -r file; do
    cp "$file" "${TARGET_DIR}/${file#$SOURCE_DIR/}" 2>/dev/null || true
done
log_success ".env templates copied"

# Copy requirements files
log_info "Copying dependency files..."
find "$SOURCE_DIR" -name "requirements*.txt" ! -path '*/.git/*' -type f | while read -r file; do
    mkdir -p "$(dirname "${TARGET_DIR}/${file#$SOURCE_DIR/}")"
    cp "$file" "${TARGET_DIR}/${file#$SOURCE_DIR/}" 2>/dev/null || true
done
log_success "Dependency files copied"

# Copy package.json/package-lock.json
find "$SOURCE_DIR" -name "package*.json" ! -path '*/.git/*' ! -path '*/node_modules/*' -type f | while read -r file; do
    mkdir -p "$(dirname "${TARGET_DIR}/${file#$SOURCE_DIR/}")"
    cp "$file" "${TARGET_DIR}/${file#$SOURCE_DIR/}" 2>/dev/null || true
done

# Copy git config files
log_info "Copying git configuration..."
[ -f "$SOURCE_DIR/.gitignore" ] && cp "$SOURCE_DIR/.gitignore" "$TARGET_DIR/.gitignore" || true
[ -f "$SOURCE_DIR/.gitmodules" ] && cp "$SOURCE_DIR/.gitmodules" "$TARGET_DIR/.gitmodules" || true
[ -f "$SOURCE_DIR/.gitattributes" ] && cp "$SOURCE_DIR/.gitattributes" "$TARGET_DIR/.gitattributes" || true
log_success "Git config files copied"

# Copy essential markdown
log_info "Copying essential markdown files..."
ESSENTIAL_MD=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    "CODE_OF_CONDUCT.md"
    ".gitignore"
)

for file in "${ESSENTIAL_MD[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$TARGET_DIR/$file" 2>/dev/null || true
        log_success "Copied: $file"
    fi
done

# Skip non-essential markdown
log_skip "Skipping AGENTS.md (non-essential)"
log_skip "Skipping TODO.md (non-essential)"
log_skip "Skipping enterprise docs (non-essential)"

echo ""
log_info "════════════════════════════════════════════════════"
log_info "File copy complete!"
log_info "════════════════════════════════════════════════════"
echo ""

# Count files in target
TARGET_FILE_COUNT=$(find "$TARGET_DIR" -type f ! -path '*/.git/*' 2>/dev/null | wc -l)
log_info "Total files in target: $TARGET_FILE_COUNT"

{
    echo ""
    echo "COPY SUMMARY"
    echo "================================"
    echo "Directories created: $DIRS_CREATED"
    echo "Total files copied: $TARGET_FILE_COUNT"
    echo "Completed: $(date)"
} >> "$COPY_LOG"

echo ""
log_info "Copy log saved to: $COPY_LOG"
echo ""
log_info "Next step: Initialize git repository"
echo "   cd $TARGET_DIR && git init && git add . && git commit -m 'init: OpenTalent project migration'"
echo ""
