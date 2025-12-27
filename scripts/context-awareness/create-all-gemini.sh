#!/bin/bash
#
# Create GEMINI.md files for all repositories in open-talent-platform
# This script generates context-aware documentation for AI models
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GENERATOR="$SCRIPT_DIR/generate-gemini-md.py"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Creating GEMINI.md Files${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counter
TOTAL=0
SUCCESS=0
SKIPPED=0
FAILED=0

# Function to generate GEMINI.md for a service
generate_gemini() {
    local service_path=$1
    local service_name=$(basename "$service_path")

    TOTAL=$((TOTAL + 1))

    # Check if GEMINI.md already exists
    if [ -f "$service_path/GEMINI.md" ]; then
        echo -e "${YELLOW}⏭️  SKIP: $service_name (GEMINI.md already exists)${NC}"
        SKIPPED=$((SKIPPED + 1))
        return
    fi

    # Generate GEMINI.md
    echo -e "${BLUE}📝 Generating: $service_name${NC}"

    if python3 "$GENERATOR" "$service_path"; then
        echo -e "${GREEN}✅ SUCCESS: $service_name${NC}"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}❌ FAILED: $service_name${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# 1. Root directory (if not exists)
echo -e "${BLUE}=== Processing Root Directory ===${NC}"
if [ ! -f "$PROJECT_ROOT/GEMINI.md" ]; then
    echo -e "${BLUE}📝 Generating: open-talent-platform (root)${NC}"
    TOTAL=$((TOTAL + 1))
    if python3 "$GENERATOR" "$PROJECT_ROOT"; then
        echo -e "${GREEN}✅ SUCCESS: open-talent-platform (root)${NC}"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}❌ FAILED: open-talent-platform (root)${NC}"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${YELLOW}⏭️  SKIP: open-talent-platform (root) - GEMINI.md already exists${NC}"
    TOTAL=$((TOTAL + 1))
    SKIPPED=$((SKIPPED + 1))
fi
echo ""

# 2. Level 1 Submodules
echo -e "${BLUE}=== Processing Level 1 Submodules ===${NC}"

# Note: open-talent-infrastructure needs custom template
if [ -d "$PROJECT_ROOT/open-talent-infrastructure" ]; then
    echo -e "${YELLOW}⚠️  TODO: open-talent-infrastructure (needs custom infrastructure template)${NC}"
    TOTAL=$((TOTAL + 1))
    SKIPPED=$((SKIPPED + 1))
fi

# Note: open-talent-landing-page needs custom template
if [ -d "$PROJECT_ROOT/open-talent-landing-page" ]; then
    echo -e "${YELLOW}⚠️  TODO: open-talent-landing-page (needs custom frontend template)${NC}"
    TOTAL=$((TOTAL + 1))
    SKIPPED=$((SKIPPED + 1))
fi

# quarkdown-specs already has GEMINI.md
if [ -d "$PROJECT_ROOT/quarkdown-specs" ]; then
    if [ -f "$PROJECT_ROOT/quarkdown-specs/GEMINI.md" ]; then
        echo -e "${YELLOW}⏭️  SKIP: quarkdown-specs (already has GEMINI.md)${NC}"
        TOTAL=$((TOTAL + 1))
        SKIPPED=$((SKIPPED + 1))
    fi
fi

echo ""

# 3. open-talent-microservices parent
echo -e "${BLUE}=== Processing Microservices Parent ===${NC}"
if [ -d "$PROJECT_ROOT/open-talent-microservices" ]; then
    echo -e "${YELLOW}⚠️  TODO: open-talent-microservices parent (needs orchestration template)${NC}"
    TOTAL=$((TOTAL + 1))
    SKIPPED=$((SKIPPED + 1))
fi
echo ""

# 4. Individual Microservices (Level 2)
echo -e "${BLUE}=== Processing Individual Microservices ===${NC}"

MICROSERVICES_DIR="$PROJECT_ROOT/open-talent-microservices"

if [ -d "$MICROSERVICES_DIR" ]; then
    for service_dir in "$MICROSERVICES_DIR"/open-talent-*/; do
        if [ -d "$service_dir" ]; then
            generate_gemini "$service_dir"
        fi
    done
else
    echo -e "${RED}❌ ERROR: open-talent-microservices directory not found${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total repositories: ${TOTAL}"
echo -e "${GREEN}✅ Successfully generated: ${SUCCESS}${NC}"
echo -e "${YELLOW}⏭️  Skipped (already exists): ${SKIPPED}${NC}"
echo -e "${RED}❌ Failed: ${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All GEMINI.md files created successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Review generated GEMINI.md files"
    echo "2. Customize service-specific details"
    echo "3. Run validation: ./validate-context.sh"
    echo "4. Commit changes to respective repositories"
else
    echo -e "${RED}⚠️  Some files failed to generate. Please check errors above.${NC}"
    exit 1
fi
