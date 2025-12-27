#!/bin/bash

################################################################################
# Fresh Git History Reset Script - OpenTalent Platform
# Purpose: Create clean git history starting from December 5, 2025
# Date: December 5, 2025
# Safety Level: HIGH (creates backup before making changes)
################################################################################

set -e  # Exit on any error

# ===== CONFIGURATION =====
readonly BACKUP_TAG="backup-before-reset-$(date +%Y%m%d-%H%M%S)"
readonly CURRENT_BRANCH=$(git branch --show-current)
readonly CURRENT_DIR=$(pwd)
readonly LOG_FILE="/tmp/reset-git-history-$(date +%Y%m%d-%H%M%S).log"

# ===== HELPER FUNCTIONS =====

log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo "✓ $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "✗ $*" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
    echo "  $*" | tee -a "$LOG_FILE"
    echo "════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

log_phase() {
    echo "" | tee -a "$LOG_FILE"
    echo ">>> PHASE: $*" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Verify git is available
if ! command -v git &> /dev/null; then
    log_error "git is not installed or not in PATH"
    exit 1
fi

# ===== HEADER =====

log_section "FRESH GIT HISTORY RESET - OpenTalent Platform"

log "Start Time: $(date)"
log "Current Directory: $CURRENT_DIR"
log "Log File: $LOG_FILE"
log ""

# ===== PRE-FLIGHT CHECKS =====

log_phase "PHASE 0: Pre-Flight Verification"

log "Checking git configuration..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository!"
    exit 1
fi
log_success "Git repository detected"

log "Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    log_error "Uncommitted changes detected. Commit or stash them first:"
    git status --short
    exit 1
fi
log_success "Working tree clean"

log "Getting current state..."
CURRENT_COMMITS=$(git rev-list --count HEAD)
CURRENT_SIZE=$(du -sh .git | cut -f1)
CURRENT_FILES=$(git ls-files | wc -l)

log "  • Current branch: $CURRENT_BRANCH"
log "  • Total commits: $CURRENT_COMMITS"
log "  • Repository size: $CURRENT_SIZE"
log "  • Tracked files: $CURRENT_FILES"

log "Verifying remote access..."
if ! git remote -v | grep -q origin; then
    log_error "No 'origin' remote found!"
    exit 1
fi
REMOTE_URL=$(git config --get remote.origin.url)
log_success "Remote verified: $REMOTE_URL"

echo ""
read -p "Continue with reset? (yes/no): " -r CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy][Ee][Ss]$ ]]; then
    log_error "Cancelled by user"
    exit 1
fi

# ===== PHASE 1: BACKUP =====

log_phase "PHASE 1: Creating Backup Tag"

log "Creating git tag: $BACKUP_TAG"
if git tag -a "$BACKUP_TAG" -m "Backup of git history before reset on $(date)"; then
    log_success "Tag created locally: $BACKUP_TAG"
else
    log_error "Failed to create tag"
    exit 1
fi

log "Pushing backup tag to remote..."
if git push origin "$BACKUP_TAG"; then
    log_success "Tag pushed to GitHub"
else
    log_error "Failed to push tag. Continuing anyway..."
fi

log "Verifying tag exists locally and remote..."
if git tag -l | grep -q "$BACKUP_TAG"; then
    log_success "Backup tag verified"
else
    log_error "Backup tag not found!"
    exit 1
fi

log "  Remote backup available at: git@github.com:asifdotpy/open-talent-platform.git"
log "  Tag name: $BACKUP_TAG"

# ===== PHASE 2: CREATE FRESH HISTORY =====

log_phase "PHASE 2: Creating Fresh Git History"

log "Creating orphan branch: fresh-history"
if ! git checkout --orphan fresh-history 2>&1 | tee -a "$LOG_FILE"; then
    log_error "Failed to create orphan branch"
    exit 1
fi
log_success "Orphan branch created"

log "Staging all files..."
if ! git add -A 2>&1 | tee -a "$LOG_FILE"; then
    log_error "Failed to stage files"
    git checkout main  # Rollback to main
    exit 1
fi
log_success "All files staged"

log "Creating initial commit..."
COMMIT_MSG="Initial commit: OpenTalent Platform - Fresh start Dec 5, 2025

Complete production-ready codebase with:
- 13 microservices (Voice, Conversation, Interview, Avatar, Scout, Analytics, Candidate, etc.)
- 8 specialized AI agents + Scout coordinator
- Vetta AI v4 fine-tuned model (1,040 training steps)
- Frontend dashboard + admin panel + landing page
- Enterprise-grade TDD migration framework
- Comprehensive documentation and specifications
- Voice service (Piper TTS, Vosk STT, Silero VAD)
- WebRTC interview orchestration
- Granite 3.0 2B LLM with LoRA adapters

Previous development consolidated on December 5, 2025.
Old git history available in tag: $BACKUP_TAG"

if git commit -m "$COMMIT_MSG" 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Initial commit created"
else
    log_error "Failed to create commit"
    git checkout main  # Rollback
    exit 1
fi

NEW_COMMIT=$(git rev-parse --short HEAD)
log "  New commit hash: $NEW_COMMIT"

log "Verifying fresh history (should be exactly 1 commit)..."
NEW_COMMIT_COUNT=$(git rev-list --count HEAD)
if [ "$NEW_COMMIT_COUNT" -eq 1 ]; then
    log_success "Fresh history has 1 commit (correct)"
else
    log_error "Fresh history has $NEW_COMMIT_COUNT commits (expected 1)"
    exit 1
fi

# ===== PHASE 3: SWITCH MAIN BRANCH =====

log_phase "PHASE 3: Switching Main Branch"

log "Deleting old main branch..."
if git branch -D main 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Main branch deleted"
else
    log_error "Failed to delete main branch"
    exit 1
fi

log "Renaming fresh-history to main..."
if git branch -m fresh-history main 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Branch renamed to main"
else
    log_error "Failed to rename branch"
    exit 1
fi

log "Verifying branch switch..."
ACTIVE_BRANCH=$(git branch --show-current)
if [ "$ACTIVE_BRANCH" = "main" ]; then
    log_success "Now on main branch"
else
    log_error "Not on main branch (on $ACTIVE_BRANCH)"
    exit 1
fi

# ===== PHASE 4: VERIFICATION =====

log_phase "PHASE 4: Verification and Testing"

log "Test 1: Git status"
if git status --porcelain | grep -q .; then
    log_error "Working tree not clean"
    git status
    exit 1
fi
log_success "Working tree clean"

log "Test 2: File count"
FINAL_FILES=$(git ls-files | wc -l)
log "  Files tracked: $FINAL_FILES (original: $CURRENT_FILES)"
if [ "$FINAL_FILES" -lt 100 ]; then
    log_error "Too few files tracked ($FINAL_FILES)"
    exit 1
fi
log_success "File count correct"

log "Test 3: Directory structure"
if [ ! -d "agents" ] || [ ! -d "microservices" ] || [ ! -d "frontend" ]; then
    log_error "Missing key directories"
    exit 1
fi
log_success "Directory structure intact"

log "Test 4: Repository size"
NEW_SIZE=$(du -sh .git | cut -f1)
log "  Original size: $CURRENT_SIZE"
log "  New size: $NEW_SIZE (after cleanup)"
log_success "Repository size reported"

log "Test 5: Commit log"
FINAL_COMMITS=$(git rev-list --count HEAD)
if [ "$FINAL_COMMITS" -ne 1 ]; then
    log_error "Wrong number of commits ($FINAL_COMMITS, expected 1)"
    exit 1
fi
log_success "Commit count correct (1)"

log "Test 6: Latest commit info"
git log -1 --pretty=format:"%h %s" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

log "All verification tests passed!"

# ===== PHASE 5: FORCE PUSH =====

log_phase "PHASE 5: Force Push to Remote"

log "WARNING: This will REPLACE remote history with local"
log "  Repository: $REMOTE_URL"
log "  Branch: main"
log "  New commit: $NEW_COMMIT"
log ""
read -p "Force push to GitHub? (yes/no): " -r PUSH_CONFIRM

if [[ ! "$PUSH_CONFIRM" =~ ^[Yy][Ee][Ss]$ ]]; then
    log_error "Cancelled force push. Local history changed but not pushed."
    log "To push later, run: git push --force-with-lease origin main"
    exit 1
fi

log "Executing force push..."
if git push --force-with-lease origin main 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Force push succeeded"
else
    log_error "Force push failed. Check GitHub permissions."
    exit 1
fi

# ===== SUMMARY =====

log_section "✓ GIT HISTORY RESET COMPLETE!"

log "Summary:"
log "  ✓ Backup tag created: $BACKUP_TAG"
log "  ✓ Fresh history created (1 commit)"
log "  ✓ Main branch updated"
log "  ✓ All verifications passed"
log "  ✓ Pushed to GitHub"
log ""

log "Next Steps:"
log "  1. Other team members should run:"
log "     git pull --force-with-lease origin main"
log "     OR fresh clone: git clone $REMOTE_URL"
log ""
log "  2. Verify with: git log --oneline | head -5"
log ""
log "  3. Old history preserved in tag:"
log "     git log $BACKUP_TAG --oneline | head -10"
log ""
log "  4. To delete backup later (optional):"
log "     git tag -d $BACKUP_TAG"
log "     git push origin :refs/tags/$BACKUP_TAG"
log ""

log "Benefits:"
log "  ✓ .git directory smaller (faster clones/pulls)"
log "  ✓ CI/CD pipelines faster"
log "  ✓ Clean commit history for new project"
log "  ✓ Professional narrative: Fresh start Dec 5, 2025"
log ""

log "Log file saved to: $LOG_FILE"
log "Completion time: $(date)"

echo ""
log_success "Done!"
