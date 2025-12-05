#!/bin/bash
#
# Validate context awareness across all repositories
# Checks for GEMINI.md, .gemini/, and docs/ directories
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Context Awareness Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counters
TOTAL_REPOS=0
GEMINI_MD_COUNT=0
GEMINI_DIR_COUNT=0
DOCS_DIR_COUNT=0
README_COUNT=0

# Function to check a repository
check_repo() {
    local repo_path=$1
    local repo_name=$(basename "$repo_path")
    
    TOTAL_REPOS=$((TOTAL_REPOS + 1))
    
    echo -e "${CYAN}📁 Checking: $repo_name${NC}"
    
    local has_gemini_md="❌"
    local has_gemini_dir="❌"
    local has_docs="❌"
    local has_readme="❌"
    
    # Check GEMINI.md
    if [ -f "$repo_path/GEMINI.md" ]; then
        has_gemini_md="✅"
        GEMINI_MD_COUNT=$((GEMINI_MD_COUNT + 1))
    fi
    
    # Check .gemini/
    if [ -d "$repo_path/.gemini" ]; then
        has_gemini_dir="✅"
        GEMINI_DIR_COUNT=$((GEMINI_DIR_COUNT + 1))
    fi
    
    # Check docs/
    if [ -d "$repo_path/docs" ]; then
        has_docs="✅"
        DOCS_DIR_COUNT=$((DOCS_DIR_COUNT + 1))
    fi
    
    # Check README.md
    if [ -f "$repo_path/README.md" ]; then
        has_readme="✅"
        README_COUNT=$((README_COUNT + 1))
    fi
    
    echo "   GEMINI.md: $has_gemini_md  |  .gemini/: $has_gemini_dir  |  docs/: $has_docs  |  README.md: $has_readme"
    echo ""
}

# Check root
echo -e "${BLUE}=== Root Repository ===${NC}"
check_repo "$PROJECT_ROOT"

# Check Level 1 submodules
echo -e "${BLUE}=== Level 1 Submodules ===${NC}"
[ -d "$PROJECT_ROOT/talent-ai-infrastructure" ] && check_repo "$PROJECT_ROOT/talent-ai-infrastructure"
[ -d "$PROJECT_ROOT/talent-ai-landing-page" ] && check_repo "$PROJECT_ROOT/talent-ai-landing-page"
[ -d "$PROJECT_ROOT/quarkdown-specs" ] && check_repo "$PROJECT_ROOT/quarkdown-specs"
[ -d "$PROJECT_ROOT/talent-ai-microservices" ] && check_repo "$PROJECT_ROOT/talent-ai-microservices"

# Check Level 2 microservices
echo -e "${BLUE}=== Microservices (Level 2) ===${NC}"
if [ -d "$PROJECT_ROOT/talent-ai-microservices" ]; then
    for service_dir in "$PROJECT_ROOT/talent-ai-microservices"/talent-ai-*/; do
        if [ -d "$service_dir" ]; then
            check_repo "$service_dir"
        fi
    done
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Total Repositories: ${TOTAL_REPOS}"
echo ""
echo -e "Coverage:"
echo -e "  ${CYAN}GEMINI.md:${NC} ${GEMINI_MD_COUNT}/${TOTAL_REPOS} ($(( GEMINI_MD_COUNT * 100 / TOTAL_REPOS ))%)"
echo -e "  ${CYAN}.gemini/:${NC}  ${GEMINI_DIR_COUNT}/${TOTAL_REPOS} ($(( GEMINI_DIR_COUNT * 100 / TOTAL_REPOS ))%)"
echo -e "  ${CYAN}docs/:${NC}     ${DOCS_DIR_COUNT}/${TOTAL_REPOS} ($(( DOCS_DIR_COUNT * 100 / TOTAL_REPOS ))%)"
echo -e "  ${CYAN}README.md:${NC} ${README_COUNT}/${TOTAL_REPOS} ($(( README_COUNT * 100 / TOTAL_REPOS ))%)"
echo ""

# Status
if [ $GEMINI_MD_COUNT -eq $TOTAL_REPOS ]; then
    echo -e "${GREEN}✅ All repositories are GEMINI.md context-aware!${NC}"
elif [ $GEMINI_MD_COUNT -gt $(( TOTAL_REPOS / 2 )) ]; then
    echo -e "${YELLOW}⚠️  Good progress! $(( TOTAL_REPOS - GEMINI_MD_COUNT )) repositories still need GEMINI.md${NC}"
else
    echo -e "${RED}❌ More work needed. $(( TOTAL_REPOS - GEMINI_MD_COUNT )) repositories missing GEMINI.md${NC}"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
if [ $GEMINI_MD_COUNT -lt $TOTAL_REPOS ]; then
    echo "1. Run ./create-all-gemini.sh to generate missing GEMINI.md files"
fi
if [ $GEMINI_DIR_COUNT -lt $TOTAL_REPOS ]; then
    echo "2. Create .gemini/ directories for model configuration"
fi
if [ $DOCS_DIR_COUNT -lt $TOTAL_REPOS ]; then
    echo "3. Create docs/ directories for comprehensive documentation"
fi
echo ""
