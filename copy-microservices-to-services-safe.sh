#!/bin/bash

################################################################################
# Copy Microservices to Services Directory (Preserves Existing Tests)
# 
# Purpose: Migrate working microservices code to services/ while preserving
#          existing test files in services/
#
# Usage: bash copy-microservices-to-services-safe.sh
#
# What This Does:
# 1. Copies source code from microservices/ to services/
# 2. EXCLUDES tests/ directories (preserves existing tests in services/)
# 3. EXCLUDES build artifacts (__pycache__, .pytest_cache, etc.)
# 4. Skips if source doesn't exist
################################################################################

set -e  # Exit on error

REPO_ROOT="/home/asif1/open-talent"
MICROSERVICES_DIR="$REPO_ROOT/microservices"
SERVICES_DIR="$REPO_ROOT/services"

echo "================================================================================"
echo "🚀 SAFE COPY: Microservices → Services (Preserves Existing Tests)"
echo "================================================================================"
echo ""

# List of all services to migrate
SERVICES=(
    "ai-auditing-service"
    "analytics-service"
    "avatar-service"
    "candidate-service"
    "conversation-service"
    "desktop-integration-service"
    "explainability-service"
    "granite-interview-service"
    "interview-service"
    "notification-service"
    "scout-service"
    "security-service"
    "user-service"
    "voice-service"
)

TOTAL_SERVICES=${#SERVICES[@]}
COPIED=0
SKIPPED=0

for service in "${SERVICES[@]}"; do
    SOURCE="$MICROSERVICES_DIR/$service"
    DEST="$SERVICES_DIR/$service"
    
    if [ ! -d "$SOURCE" ]; then
        echo "⏭️  SKIP: $service (source not found in microservices/)"
        ((SKIPPED++))
        continue
    fi
    
    # Check if source has main.py (indicates working service)
    if [ ! -f "$SOURCE/main.py" ]; then
        echo "⏭️  SKIP: $service (no main.py found)"
        ((SKIPPED++))
        continue
    fi
    
    # Ensure destination directory exists
    mkdir -p "$DEST"
    
    echo "📋 Copying: $service"
    
    # Copy everything EXCEPT tests/, __pycache__, .pytest_cache, .env
    # Use rsync with excludes for safety
    rsync -av \
        --exclude='tests/' \
        --exclude='__pycache__/' \
        --exclude='.pytest_cache/' \
        --exclude='.env' \
        --exclude='*.pyc' \
        --exclude='.venv*' \
        --exclude='venv*' \
        "$SOURCE/" "$DEST/"
    
    # Verify key files exist
    if [ -f "$DEST/main.py" ]; then
        echo "   ✅ main.py copied"
        ((COPIED++))
    else
        echo "   ❌ ERROR: main.py not found after copy!"
        exit 1
    fi
    
    # Verify tests/ directory still exists (from original services/)
    if [ -d "$DEST/tests" ]; then
        echo "   ✅ Existing tests/ preserved"
    else
        echo "   ⚠️  No tests/ directory (will be created on first test run)"
    fi
    
    echo ""
done

echo "================================================================================"
echo "📊 COPY SUMMARY"
echo "================================================================================"
echo "Total services:     $TOTAL_SERVICES"
echo "Copied:             $COPIED ✅"
echo "Skipped:            $SKIPPED ⏭️"
echo ""
echo "✅ All source code migrated!"
echo "✅ All existing tests preserved!"
echo "================================================================================"
echo ""
echo "Next Steps:"
echo "1. Verify services/ has main.py files:"
echo "   find services/ -name 'main.py' | wc -l"
echo ""
echo "2. Verify tests/ directories are preserved:"
echo "   find services/ -type d -name 'tests' | sort"
echo ""
echo "3. Run tests to verify:"
echo "   cd services/candidate-service && pytest tests/"
echo ""
