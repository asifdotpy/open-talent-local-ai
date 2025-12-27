#!/bin/bash

################################################################################
# OpenTalent Platform - Safe Migration Execution Script
#
# Purpose: Execute project reorganization with rollback capability
# Version: 1.0.0
# Date: December 5, 2025
#
# This script safely migrates files from old structure to new structure
# with checksums, backups, and atomic operations.
#
# Usage:
#   ./scripts/execute-migration.sh --dry-run
#   ./scripts/execute-migration.sh --backup-only
#   ./scripts/execute-migration.sh --execute
#   ./scripts/execute-migration.sh --rollback
#
################################################################################

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MIGRATION_LOG="${PROJECT_ROOT}/migration-execution.log"
BACKUP_DIR="${PROJECT_ROOT}/.migration-backup-$(date +%Y%m%d-%H%M%S)"
STATE_DIR="${PROJECT_ROOT}/.migration-state"
MANIFEST="${STATE_DIR}/migration-manifest.txt"
CHECKSUMS="${STATE_DIR}/migration-checksums.sha256"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
FILES_MIGRATED=0
FILES_FAILED=0
BYTES_MIGRATED=0

# Flags
DRY_RUN="${DRY_RUN:-false}"
BACKUP_ONLY="${BACKUP_ONLY:-false}"
EXECUTE="${EXECUTE:-false}"
ROLLBACK="${ROLLBACK:-false}"

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

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    log "ERROR" "$1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    log "WARN" "$1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
    log "INFO" "$1"
}

# ============================================================================
# DIRECTORY CREATION
# ============================================================================

create_directory_structure() {
    print_section "CREATING DIRECTORY STRUCTURE"

    local dirs=(
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

    for dir in "${dirs[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            info "[DRY-RUN] Would create: $PROJECT_ROOT/$dir"
        else
            if mkdir -p "$PROJECT_ROOT/$dir"; then
                pass "Created: $dir"
                echo "mkdir:$dir" >> "$MANIFEST"
            else
                fail "Failed to create: $dir"
                return 1
            fi
        fi
    done

    log "INFO" "Directory structure creation complete"
}

# ============================================================================
# FILE OPERATIONS
# ============================================================================

safe_move_file() {
    local source=$1
    local dest=$2
    local description=$3

    if [[ ! -f "$source" ]]; then
        warn "Source does not exist: $source"
        return 1
    fi

    # Create destination directory if needed
    local dest_dir=$(dirname "$dest")
    if [[ ! -d "$dest_dir" ]]; then
        mkdir -p "$dest_dir"
    fi

    # Calculate checksum before migration
    local source_checksum=$(sha256sum "$source" | awk '{print $1}')

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY-RUN] Would move: $source → $dest"
    else
        # Backup file
        if mkdir -p "$BACKUP_DIR"; then
            local backup_path="$BACKUP_DIR/$(basename "$source")"
            cp "$source" "$backup_path"
            echo "backup:$source:$backup_path:$source_checksum" >> "$MANIFEST"
        fi

        # Move file
        if mv "$source" "$dest"; then
            pass "Migrated: $description"
            echo "move:$source:$dest:$source_checksum" >> "$MANIFEST"

            # Verify checksum after move
            local dest_checksum=$(sha256sum "$dest" | awk '{print $1}')
            if [[ "$source_checksum" == "$dest_checksum" ]]; then
                echo "$source_checksum  $dest" >> "$CHECKSUMS"
                pass "  Checksum verified: $source_checksum"
                ((FILES_MIGRATED++))
                BYTES_MIGRATED=$((BYTES_MIGRATED + $(stat -f%z "$dest" 2>/dev/null || stat -c%s "$dest" 2>/dev/null || echo 0)))
            else
                fail "  Checksum mismatch!"
                ((FILES_FAILED++))
                return 1
            fi
        else
            fail "Failed to move: $source"
            ((FILES_FAILED++))
            return 1
        fi
    fi
}

safe_copy_directory() {
    local source=$1
    local dest=$2
    local description=$3

    if [[ ! -d "$source" ]]; then
        warn "Source directory does not exist: $source"
        return 1
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY-RUN] Would copy directory: $source → $dest"
    else
        if cp -r "$source" "$dest"; then
            pass "Migrated: $description"
            echo "copy-dir:$source:$dest" >> "$MANIFEST"
            ((FILES_MIGRATED++))
        else
            fail "Failed to copy directory: $source"
            ((FILES_FAILED++))
            return 1
        fi
    fi
}

# ============================================================================
# MIGRATION OPERATIONS
# ============================================================================

migrate_model_files() {
    print_section "MIGRATING MODEL FILES"

    info "Moving GGUF model from root to models/gguf/"
    safe_move_file \
        "$PROJECT_ROOT/vetta-granite-2b-gguf-v4.gguf" \
        "$PROJECT_ROOT/models/gguf/vetta-granite-2b-gguf-v4.gguf" \
        "GGUF model file"

    info "Migrating LoRA adapters"
    if [[ -d "$PROJECT_ROOT/models/lora" ]]; then
        find "$PROJECT_ROOT" -maxdepth 1 -name "*.gguf" -o -name "*.safetensors" | while read -r file; do
            if [[ "$file" != "$PROJECT_ROOT/models/gguf/vetta-granite-2b-gguf-v4.gguf" ]]; then
                safe_move_file "$file" "$PROJECT_ROOT/models/lora/$(basename "$file")" "LoRA adapter"
            fi
        done
    fi

    info "Migrating notebook chunks"
    if [[ -d "$PROJECT_ROOT/notebook_chunks" ]]; then
        safe_copy_directory \
            "$PROJECT_ROOT/notebook_chunks" \
            "$PROJECT_ROOT/models/training/notebook_chunks" \
            "Notebook chunks directory"
    fi

    log "INFO" "Model files migration complete"
}

migrate_documentation() {
    print_section "MIGRATING DOCUMENTATION FILES"

    local root_dir="$PROJECT_ROOT"

    # Migrate Vetta/Granite docs to models/docs/
    info "Migrating Vetta AI documentation"
    find "$root_dir" -maxdepth 1 -type f -name "*VETTA*" -o -name "*GRANITE*" 2>/dev/null | while read -r file; do
        safe_move_file "$file" "$root_dir/models/docs/$(basename "$file")" "Vetta AI doc: $(basename "$file")"
    done

    # Migrate dataset docs to docs/datasets/
    info "Migrating dataset documentation"
    find "$root_dir" -maxdepth 1 -type f -name "*DATASET*" -o -name "*DATA*" 2>/dev/null | while read -r file; do
        if [[ "$file" != *".env"* ]]; then
            safe_move_file "$file" "$root_dir/docs/datasets/$(basename "$file")" "Dataset doc: $(basename "$file")"
        fi
    done

    # Migrate status reports to docs/status/ or archive
    info "Migrating status reports"
    find "$root_dir" -maxdepth 1 -type f \( -name "*STATUS*" -o -name "*REPORT*" -o -name "*PROGRESS*" \) 2>/dev/null | while read -r file; do
        safe_move_file "$file" "$root_dir/docs/status/$(basename "$file")" "Status report: $(basename "$file")"
    done

    log "INFO" "Documentation migration complete"
}

migrate_scripts() {
    print_section "MIGRATING SCRIPTS"

    local root_dir="$PROJECT_ROOT"

    # Move Python scripts (except setup/migration related)
    info "Migrating Python scripts"
    find "$root_dir" -maxdepth 1 -type f -name "*.py" 2>/dev/null | while read -r file; do
        if [[ ! "$file" =~ (setup|migration|verify) ]]; then
            safe_move_file "$file" "$root_dir/scripts/$(basename "$file")" "Python script: $(basename "$file")"
        fi
    done

    # Move shell scripts
    info "Migrating shell scripts"
    find "$root_dir" -maxdepth 1 -type f -name "*.sh" 2>/dev/null | while read -r file; do
        if [[ ! "$file" =~ (setup|migration|verify|start|stop) ]]; then
            safe_move_file "$file" "$root_dir/scripts/$(basename "$file")" "Shell script: $(basename "$file")"
        fi
    done

    log "INFO" "Scripts migration complete"
}

migrate_assets() {
    print_section "MIGRATING ASSETS"

    local root_dir="$PROJECT_ROOT"

    # Move audio files to examples/demos
    info "Migrating audio/media files"
    find "$root_dir" -maxdepth 1 -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.mp4" \) 2>/dev/null | while read -r file; do
        safe_move_file "$file" "$root_dir/examples/demos/$(basename "$file")" "Media file: $(basename "$file")"
    done

    log "INFO" "Assets migration complete"
}

cleanup_root_directory() {
    print_section "CLEANING ROOT DIRECTORY"

    info "Removing empty directories from root"

    if [[ -d "$PROJECT_ROOT/notebook_chunks" ]] && [[ -z "$(find "$PROJECT_ROOT/notebook_chunks" -type f 2>/dev/null)" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            info "[DRY-RUN] Would remove: notebook_chunks/"
        else
            rmdir "$PROJECT_ROOT/notebook_chunks" 2>/dev/null || true
            pass "Removed empty directory: notebook_chunks/"
            echo "rmdir:notebook_chunks" >> "$MANIFEST"
        fi
    fi

    log "INFO" "Root directory cleanup complete"
}

# ============================================================================
# BACKUP OPERATIONS
# ============================================================================

create_git_checkpoint() {
    print_section "CREATING GIT CHECKPOINT"

    cd "$PROJECT_ROOT" || return 1

    if git rev-parse --git-dir > /dev/null 2>&1; then
        if [[ "$DRY_RUN" == "false" ]]; then
            local tag="pre-migration-$(date +%Y%m%d-%H%M%S)"
            git tag "$tag"
            pass "Created git tag: $tag"
            log "INFO" "Git checkpoint created: $tag"
        else
            info "[DRY-RUN] Would create git tag for checkpoint"
        fi
    else
        warn "Not a git repository - skipping git checkpoint"
    fi
}

create_file_manifest() {
    print_section "CREATING MIGRATION MANIFEST"

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY-RUN] Would create manifest: $MANIFEST"
    else
        mkdir -p "$STATE_DIR"
        > "$MANIFEST"
        echo "# Migration Manifest" > "$MANIFEST"
        echo "# Generated: $(date)" >> "$MANIFEST"
        echo "# This file tracks all migration operations" >> "$MANIFEST"
        pass "Created manifest: $MANIFEST"
    fi
}

# ============================================================================
# ROLLBACK OPERATIONS
# ============================================================================

rollback_migration() {
    print_section "ROLLING BACK MIGRATION"

    if [[ ! -f "$MANIFEST" ]]; then
        fail "No migration manifest found - cannot rollback"
        return 1
    fi

    info "Reading migration manifest from: $MANIFEST"

    # Process manifest in reverse
    tac "$MANIFEST" | while read -r line; do
        if [[ "$line" =~ ^move: ]]; then
            local source=$(echo "$line" | cut -d: -f2)
            local dest=$(echo "$line" | cut -d: -f3)

            if [[ -f "$dest" ]]; then
                if mv "$dest" "$source"; then
                    pass "Restored: $source"
                else
                    fail "Failed to restore: $source"
                fi
            fi
        elif [[ "$line" =~ ^copy-dir: ]]; then
            local dest=$(echo "$line" | cut -d: -f3)
            if [[ -d "$dest" ]]; then
                rm -rf "$dest" 2>/dev/null || true
                pass "Removed copied directory: $dest"
            fi
        elif [[ "$line" =~ ^rmdir: ]]; then
            local dir=$(echo "$line" | cut -d: -f2)
            # Restore would require backup
            warn "Cannot restore directory: $dir (requires backup restoration)"
        fi
    done

    pass "Rollback complete"
    log "INFO" "Migration rollback completed"
}

# ============================================================================
# VERIFICATION
# ============================================================================

verify_migration() {
    print_section "VERIFYING MIGRATION"

    info "Verifying checksums"
    if [[ -f "$CHECKSUMS" ]]; then
        if sha256sum -c "$CHECKSUMS" > /dev/null 2>&1; then
            pass "All file checksums verified"
        else
            fail "Checksum verification failed"
            return 1
        fi
    fi

    info "Checking for orphaned files"
    local orphaned_count=$(find "$PROJECT_ROOT" -maxdepth 1 -type f -name "*.py" -o -name "*.wav" 2>/dev/null | wc -l)
    if [[ $orphaned_count -eq 0 ]]; then
        pass "No orphaned files found"
    else
        warn "Found $orphaned_count orphaned files"
    fi

    log "INFO" "Migration verification complete"
}

# ============================================================================
# REPORTING
# ============================================================================

print_summary() {
    print_section "MIGRATION SUMMARY"

    echo -e "Files Migrated:  ${GREEN}$FILES_MIGRATED${NC}"
    echo -e "Failed:          ${RED}$FILES_FAILED${NC}"
    echo -e "Bytes Migrated:  ${CYAN}$BYTES_MIGRATED${NC}"
    echo -e "Backup Created:  ${CYAN}$BACKUP_DIR${NC}"
    echo -e "Manifest:        ${CYAN}$MANIFEST${NC}"
    echo -e "Checksums:       ${CYAN}$CHECKSUMS${NC}"

    log "INFO" "Migration: Files=$FILES_MIGRATED Failed=$FILES_FAILED Bytes=$BYTES_MIGRATED"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                info "Running in DRY-RUN mode (no changes will be made)"
                ;;
            --backup-only)
                BACKUP_ONLY=true
                ;;
            --execute)
                EXECUTE=true
                ;;
            --rollback)
                ROLLBACK=true
                ;;
            *)
                echo "Usage: $0 [--dry-run|--backup-only|--execute|--rollback]"
                exit 1
                ;;
        esac
        shift
    done
}

main() {
    parse_args "$@"

    print_header "OpenTalent Platform - Safe Migration Execution v1.0.0"

    # Initialize log
    > "$MIGRATION_LOG"
    log "INFO" "Migration execution started"
    log "INFO" "Dry run: $DRY_RUN"

    if [[ "$ROLLBACK" == "true" ]]; then
        rollback_migration
        print_summary
        exit 0
    fi

    # Create git checkpoint
    create_git_checkpoint

    # Create manifest
    create_file_manifest

    if [[ "$BACKUP_ONLY" == "false" ]]; then
        # Create directory structure
        create_directory_structure

        # Migrate files
        migrate_model_files
        migrate_documentation
        migrate_scripts
        migrate_assets

        # Cleanup
        cleanup_root_directory

        # Verify
        verify_migration
    fi

    # Print summary
    print_summary

    if [[ "$DRY_RUN" == "true" ]]; then
        warn "This was a DRY-RUN - no changes were made"
        warn "Run with --execute to perform the migration"
    fi

    if [[ $FILES_FAILED -eq 0 ]]; then
        pass "Migration completed successfully"
        log "INFO" "Migration execution completed successfully"
        exit 0
    else
        fail "Migration completed with $FILES_FAILED error(s)"
        log "ERROR" "Migration execution completed with errors"
        exit 1
    fi
}

main "$@"
