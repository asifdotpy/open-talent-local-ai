#!/bin/bash
# Enhanced verification script for markdown file migration
# - Checks if each source file has been moved to its intended destination
# - Reports missing or duplicate files
# - Provides color output, summary, and CSV report

MAPPING_FILE="md_mapping_full.txt"
CSV_REPORT="md_verification_report.csv"
ALL_OK=1
total=0
ok=0
missing=0
unmoved=0

# Color codes
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo "source_file,destination_file,status" > "$CSV_REPORT"

while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    # Parse mapping: source → destination
    src=$(echo "$line" | cut -d '→' -f1 | xargs)
    dest=$(echo "$line" | cut -d '→' -f2 | xargs)
    if [[ -z "$src" || -z "$dest" ]]; then
        continue
    fi
    ((total++))
    status="OK"
    if [[ -f "$dest" ]]; then
        echo -e "${GREEN}✅ $dest exists.${NC}"
        ((ok++))
    else
        echo -e "${RED}❌ $dest is missing!${NC}"
        status="MISSING"
        ((missing++))
        ALL_OK=0
    fi
    if [[ -f "$src" ]]; then
        echo -e "${YELLOW}⚠️  $src still exists (should be moved).${NC}"
        status="UNMOVED"
        ((unmoved++))
        ALL_OK=0
    fi
    echo "$src,$dest,$status" >> "$CSV_REPORT"
done < "$MAPPING_FILE"

echo -e "\nSummary:"
echo -e "  Total files checked: $total"
echo -e "  ${GREEN}OK: $ok${NC}"
echo -e "  ${RED}Missing: $missing${NC}"
echo -e "  ${YELLOW}Unmoved: $unmoved${NC}"
echo -e "\nCSV report: $CSV_REPORT"

if [[ $ALL_OK -eq 1 ]]; then
    echo -e "\n${GREEN}All markdown files are correctly migrated!${NC}"
else
    echo -e "\n${RED}Some files are missing or not moved. Please review above.${NC}"
fi
