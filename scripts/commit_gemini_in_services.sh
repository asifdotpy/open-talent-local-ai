#!/bin/bash
#
# Commit GEMINI.md files in all microservice submodules
# This script commits GEMINI.md in each service and updates parent references
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MICROSERVICES_DIR="$PROJECT_ROOT/open-talent-microservices"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Committing GEMINI.md in Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counter
TOTAL=0
SUCCESS=0
SKIPPED=0
FAILED=0

# Function to commit GEMINI.md in a service
commit_gemini() {
    local service_path=$1
    local service_name=$(basename "$service_path")

    TOTAL=$((TOTAL + 1))

    # Check if it's a git repository
    if [ ! -d "$service_path/.git" ]; then
        echo -e "${YELLOW}⏭️  SKIP: $service_name (not a git repository)${NC}"
        SKIPPED=$((SKIPPED + 1))
        return
    fi

    # Check if GEMINI.md exists
    if [ ! -f "$service_path/GEMINI.md" ]; then
        echo -e "${YELLOW}⏭️  SKIP: $service_name (no GEMINI.md found)${NC}"
        SKIPPED=$((SKIPPED + 1))
        return
    fi

    # Check if GEMINI.md is already committed
    cd "$service_path"
    if ! git status --porcelain | grep -q "GEMINI.md"; then
        echo -e "${YELLOW}⏭️  SKIP: $service_name (GEMINI.md already committed)${NC}"
        SKIPPED=$((SKIPPED + 1))
        cd - > /dev/null
        return
    fi

    # Commit GEMINI.md
    echo -e "${BLUE}📝 Committing: $service_name${NC}"

    if git add GEMINI.md && git commit -m "docs: Add GEMINI.md for AI context awareness"; then
        echo -e "${GREEN}✅ SUCCESS: $service_name${NC}"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}❌ FAILED: $service_name (commit failed)${NC}"
        FAILED=$((FAILED + 1))
    fi

    cd - > /dev/null
    echo ""
}

# Check if microservices directory exists
if [ ! -d "$MICROSERVICES_DIR" ]; then
    echo -e "${RED}❌ Error: open-talent-microservices directory not found${NC}"
    exit 1
fi

# Process all services in microservices directory
echo -e "${BLUE}=== Processing Microservices ===${NC}"
cd "$MICROSERVICES_DIR"

for service_dir in open-talent-*/; do
    if [ -d "$service_dir" ]; then
        commit_gemini "$MICROSERVICES_DIR/$service_dir"
    fi
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total services: ${TOTAL}"
echo -e "${GREEN}✅ Success: ${SUCCESS}${NC}"
echo -e "${YELLOW}⏭️  Skipped: ${SKIPPED}${NC}"
echo -e "${RED}❌ Failed: ${FAILED}${NC}"
echo ""

if [ $SUCCESS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Note: Submodule references need to be updated in parent repos${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. cd $MICROSERVICES_DIR"
    echo -e "  2. git add <updated-services>"
    echo -e "  3. git commit -m 'chore: Update service submodules with GEMINI.md'"
    echo -e "  4. cd $PROJECT_ROOT"
    echo -e "  5. git add open-talent-microservices"
    echo -e "  6. git commit -m 'chore: Update microservices submodule references'"
    echo ""
fi

exit 0
