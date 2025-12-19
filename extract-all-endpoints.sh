#!/bin/bash
# Automated endpoint extraction for all OpenTalent services
# Usage: ./extract-all-endpoints.sh

# Disable exit-on-error to allow partial extraction even if some services are down
set +e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service definitions: service-name:port
SERVICES=(
    "avatar-service:8001"
    "conversation-service:8003"
    "interview-service:8004"
    "security-service:8005"
    "candidate-service:8008"
    "notification-service:8011"
    "ai-auditing-service:8012"
    "analytics-service:8017"
    "explainability-service:8014"
    "voice-service:8015"
    "scout-service:8010"
)

# Create output directory with timestamp
OUTPUT_DIR="$HOME/open-talent/endpoint-extraction-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}OpenTalent Endpoint Extraction Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""

# Initialize summary file
cat > "$OUTPUT_DIR/SUMMARY.md" << EOF
# OpenTalent Endpoint Extraction Report

**Generated:** $(date)  
**Location:** $OUTPUT_DIR

---

## Summary

EOF

total_endpoints=0
running_services=0
failed_services=0

# Process each service
for service_port in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_port"
    echo -e "${YELLOW}🔍 Checking $service on port $port...${NC}"
    
    # Check if service is running (try health endpoint first, then root)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health" 2>/dev/null || echo "000")
    
    if [ "$http_code" == "000" ]; then
        # Try root endpoint
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/" 2>/dev/null || echo "000")
    fi
    
    if [ "$http_code" == "200" ] || [ "$http_code" == "307" ]; then
        echo -e "${GREEN}✅ $service is running (HTTP $http_code)${NC}"
        ((running_services++))
        
        # Extract OpenAPI schema
        schema_response=$(curl -s "http://localhost:$port/openapi.json" 2>/dev/null)
        
        if [ -n "$schema_response" ] && echo "$schema_response" | jq empty 2>/dev/null; then
            # Extract endpoints (paths only)
            echo "$schema_response" | jq -r '.paths | keys[]' > "$OUTPUT_DIR/${service}-endpoints.txt"
            
            # Extract full path details
            echo "$schema_response" | jq '.paths' > "$OUTPUT_DIR/${service}-full.json"
            
            # Extract with methods and summaries
            echo "$schema_response" | jq -r '.paths | to_entries[] | .key as $path | .value | to_entries[] | "\(.key | ascii_upcase) \($path) - \(.value.summary // \"No description\")"' > "$OUTPUT_DIR/${service}-detailed.txt"
            
            # Get service info
            echo "$schema_response" | jq '.info' > "$OUTPUT_DIR/${service}-info.json"
            
            # Count endpoints
            count=$(echo "$schema_response" | jq '.paths | keys | length')
            echo -e "${GREEN}  📊 Found $count endpoints${NC}"
            ((total_endpoints+=count))
            
            # Add to summary
            cat >> "$OUTPUT_DIR/SUMMARY.md" << EOF
### $service (Port $port)
- **Status:** ✅ Running
- **Endpoints:** $count
- **Swagger UI:** http://localhost:$port/docs
- **OpenAPI JSON:** http://localhost:$port/openapi.json
- **Files Generated:**
  - \`${service}-endpoints.txt\` (endpoint paths)
  - \`${service}-detailed.txt\` (methods + descriptions)
  - \`${service}-full.json\` (complete OpenAPI paths)
  - \`${service}-info.json\` (service metadata)

EOF
        else
            echo -e "${RED}  ❌ Failed to fetch valid OpenAPI schema${NC}"
            ((failed_services++))
            cat >> "$OUTPUT_DIR/SUMMARY.md" << EOF
### $service (Port $port)
- **Status:** ⚠️ Running but OpenAPI schema unavailable
- **Swagger UI:** http://localhost:$port/docs (may not exist)

EOF
        fi
    else
        echo -e "${RED}❌ $service not responding on port $port (HTTP $http_code)${NC}"
        ((failed_services++))
        cat >> "$OUTPUT_DIR/SUMMARY.md" << EOF
### $service (Port $port)
- **Status:** ❌ Not Running
- **Note:** Start service with: \`cd services/$service && python main.py\`

EOF
    fi
    echo ""
done

# Add final statistics to summary
cat >> "$OUTPUT_DIR/SUMMARY.md" << EOF

---

## Statistics

- **Total Services Checked:** ${#SERVICES[@]}
- **Running Services:** $running_services
- **Failed/Unavailable:** $failed_services
- **Total Endpoints Found:** $total_endpoints
- **Average Endpoints per Service:** $(( running_services > 0 ? total_endpoints / running_services : 0 ))

---

## Next Steps

1. Review individual service endpoint files
2. Compare with specification documents in project root
3. Update \`FINAL_API_VALIDATION_DOCUMENT.md\`
4. Cross-reference with service README files
5. Test critical endpoints manually

---

## Files in This Directory

- \`SUMMARY.md\` - This file
- \`*-endpoints.txt\` - Simple list of endpoint paths
- \`*-detailed.txt\` - Endpoints with HTTP methods and descriptions
- \`*-full.json\` - Complete OpenAPI path objects
- \`*-info.json\` - Service metadata (title, version, description)

EOF

# Create consolidated endpoints file
echo "# All OpenTalent Endpoints" > "$OUTPUT_DIR/ALL-ENDPOINTS.txt"
echo "# Generated: $(date)" >> "$OUTPUT_DIR/ALL-ENDPOINTS.txt"
echo "" >> "$OUTPUT_DIR/ALL-ENDPOINTS.txt"

for service_port in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_port"
    if [ -f "$OUTPUT_DIR/${service}-endpoints.txt" ]; then
        echo "## $service (Port $port)" >> "$OUTPUT_DIR/ALL-ENDPOINTS.txt"
        cat "$OUTPUT_DIR/${service}-endpoints.txt" >> "$OUTPUT_DIR/ALL-ENDPOINTS.txt"
        echo "" >> "$OUTPUT_DIR/ALL-ENDPOINTS.txt"
    fi
done

# Print final summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Extraction Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "📊 ${GREEN}Results:${NC}"
echo -e "   - Running Services: ${GREEN}$running_services${NC} / ${#SERVICES[@]}"
echo -e "   - Failed Services: ${RED}$failed_services${NC}"
echo -e "   - Total Endpoints: ${GREEN}$total_endpoints${NC}"
echo ""
echo -e "📁 ${BLUE}Output Directory:${NC} $OUTPUT_DIR"
echo -e "📄 ${BLUE}Summary File:${NC} $OUTPUT_DIR/SUMMARY.md"
echo -e "📋 ${BLUE}All Endpoints:${NC} $OUTPUT_DIR/ALL-ENDPOINTS.txt"
echo ""
echo -e "${YELLOW}💡 Tip:${NC} View summary with: cat $OUTPUT_DIR/SUMMARY.md"
echo ""
