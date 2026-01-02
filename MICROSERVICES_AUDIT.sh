#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# OpenTalent Microservices Comprehensive Audit Script
# ═══════════════════════════════════════════════════════════════════════════
# This script audits all microservices and generates a detailed report
# Usage: ./MICROSERVICES_AUDIT.sh
# ═══════════════════════════════════════════════════════════════════════════

WORKSPACE="/home/asif1/open-talent"
MICROSERVICES_DIR="$WORKSPACE/microservices"
REPORT_FILE="/tmp/microservices_audit_$(date +%Y%m%d_%H%M%S).txt"
REPORT_JSON="/tmp/microservices_audit_$(date +%Y%m%d_%H%M%S).json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Initialize report files
{
    echo "═══════════════════════════════════════════════════════════════════"
    echo "OPENTALENT MICROSERVICES COMPREHENSIVE AUDIT REPORT"
    echo "Generated: $(date)"
    echo "Workspace: $WORKSPACE"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
} > "$REPORT_FILE"

# Array to collect service info for JSON
declare -a SERVICES_INFO

# Get list of actual services (exclude non-service directories)
echo -e "${BLUE}Scanning microservices directory...${NC}"
services=($(ls -d "$MICROSERVICES_DIR"/*/ 2>/dev/null | xargs -I {} basename {} | grep -v -E "^(deployment|scripts|shared|\.)" | sort))

echo -e "${CYAN}Found ${#services[@]} services to audit${NC}"
echo ""

# Audit each service
for i in "${!services[@]}"; do
    service="${services[$i]}"
    service_path="$MICROSERVICES_DIR/$service"
    service_num=$((i + 1))

    echo -e "${BLUE}[$service_num/${#services[@]}]${NC} Auditing ${CYAN}$service${NC}..."

    {
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "SERVICE #$service_num: $service"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Path: $service_path"
        echo ""
    } >> "$REPORT_FILE"

    # 1. ENTRY POINTS
    {
        echo "1. ENTRY POINTS & APPLICATION STRUCTURE:"
        echo "  ─────────────────────────────────────"
    } >> "$REPORT_FILE"

    entry_point=""
    if [ -f "$service_path/main.py" ]; then
        echo "  ✓ main.py (at root level)" >> "$REPORT_FILE"
        entry_point="main.py"
        # Check file size
        size=$(wc -l < "$service_path/main.py")
        echo "    Lines of code: $size" >> "$REPORT_FILE"
    fi

    if [ -f "$service_path/app/main.py" ]; then
        echo "  ✓ app/main.py (in subdirectory)" >> "$REPORT_FILE"
        entry_point="app/main.py"
        size=$(wc -l < "$service_path/app/main.py")
        echo "    Lines of code: $size" >> "$REPORT_FILE"
    fi

    if [ -z "$entry_point" ]; then
        echo "  ✗ NO ENTRY POINT FOUND" >> "$REPORT_FILE"
    fi

    # 2. PYTHON DEPENDENCIES
    {
        echo ""
        echo "2. PYTHON DEPENDENCIES:"
        echo "  ─────────────────────"
    } >> "$REPORT_FILE"

    if [ -f "$service_path/requirements.txt" ]; then
        req_count=$(wc -l < "$service_path/requirements.txt")
        echo "  ✓ requirements.txt ($req_count packages)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        head -20 "$service_path/requirements.txt" | sed 's/^/    /' >> "$REPORT_FILE"
        if [ $req_count -gt 20 ]; then
            echo "    ... and $((req_count - 20)) more packages" >> "$REPORT_FILE"
        fi
    else
        echo "  ✗ No requirements.txt found" >> "$REPORT_FILE"
    fi

    # 3. VIRTUAL ENVIRONMENT STATUS
    {
        echo ""
        echo "3. VIRTUAL ENVIRONMENT STATUS:"
        echo "  ────────────────────────────"
    } >> "$REPORT_FILE"

    venv_status="✗ MISSING"
    venv_py_version="Unknown"

    if [ -d "$service_path/venv/bin" ]; then
        venv_status="✓ EXISTS (venv)"
        if [ -f "$service_path/venv/bin/python3" ]; then
            venv_py_version=$("$service_path/venv/bin/python3" --version 2>&1 | awk '{print $2}')
        fi
    elif [ -d "$service_path/.venv/bin" ]; then
        venv_status="✓ EXISTS (.venv)"
        if [ -f "$service_path/.venv/bin/python3" ]; then
            venv_py_version=$("$service_path/.venv/bin/python3" --version 2>&1 | awk '{print $2}')
        fi
    else
        # Check for incomplete venv
        if [ -d "$service_path/venv" ] || [ -d "$service_path/.venv" ]; then
            venv_status="⚠ INCOMPLETE (missing bin/)"
        fi
    fi

    echo "  Status: $venv_status" >> "$REPORT_FILE"
    echo "  Python Version: $venv_py_version" >> "$REPORT_FILE"

    # 4. CONFIGURATION FILES
    {
        echo ""
        echo "4. CONFIGURATION FILES:"
        echo "  ─────────────────────"
    } >> "$REPORT_FILE"

    config_found=0
    for config_file in config.py config.json config.toml .env .env.example docker-compose.yml Dockerfile pyproject.toml setup.py; do
        if [ -f "$service_path/$config_file" ]; then
            echo "  ✓ $config_file" >> "$REPORT_FILE"
            config_found=$((config_found + 1))
        fi
    done

    if [ $config_found -eq 0 ]; then
        echo "  (No standard config files found)" >> "$REPORT_FILE"
    fi

    # 5. FASTAPI/FRAMEWORK DETECTION
    {
        echo ""
        echo "5. FRAMEWORK & TECHNOLOGY DETECTION:"
        echo "  ──────────────────────────────────"
    } >> "$REPORT_FILE"

    framework="Unknown"
    port="Not specified"

    if [ -n "$entry_point" ]; then
        entry_file="$service_path/$entry_point"

        if grep -q "FastAPI\|from fastapi" "$entry_file" 2>/dev/null; then
            echo "  ✓ FastAPI detected" >> "$REPORT_FILE"
            framework="FastAPI"
        fi

        if grep -q "Flask" "$entry_file" 2>/dev/null; then
            echo "  ✓ Flask detected" >> "$REPORT_FILE"
            framework="Flask"
        fi

        if grep -q "uvicorn\|uvicorn.run" "$entry_file" 2>/dev/null; then
            echo "  ✓ Uvicorn server detected" >> "$REPORT_FILE"
        fi

        # Try to find port
        port_match=$(grep -oP "port['\"]?\s*[:=]\s*\K[0-9]{4,5}" "$entry_file" | head -1)
        if [ -n "$port_match" ]; then
            port=$port_match
            echo "  Port: $port" >> "$REPORT_FILE"
        fi
    fi

    # 6. API ROUTES/ENDPOINTS
    {
        echo ""
        echo "6. API ENDPOINTS:"
        echo "  ───────────────"
    } >> "$REPORT_FILE"

    if [ -n "$entry_point" ]; then
        entry_file="$service_path/$entry_point"
        routes=$(grep -E "@app\.(get|post|put|delete|patch|head|options)" "$entry_file" 2>/dev/null | head -15)

        if [ -n "$routes" ]; then
            echo "$routes" | sed 's/^/  /' >> "$REPORT_FILE"
            route_count=$(grep -c "@app\." "$entry_file" 2>/dev/null || echo 0)
            if [ $route_count -gt 15 ]; then
                echo "  ... and $((route_count - 15)) more routes" >> "$REPORT_FILE"
            fi
        else
            echo "  (No FastAPI routes detected)" >> "$REPORT_FILE"
        fi
    fi

    # 7. DIRECTORY STRUCTURE
    {
        echo ""
        echo "7. DIRECTORY STRUCTURE:"
        echo "  ─────────────────────"
    } >> "$REPORT_FILE"

    (
        cd "$service_path" && find . -maxdepth 2 -type d | sed 's|^\./||' | grep -v "^\.$" | sort | sed 's/^/  /'
    ) >> "$REPORT_FILE" 2>/dev/null

    # 8. KEY FILES
    {
        echo ""
        echo "8. KEY FILES IN SERVICE:"
        echo "  ──────────────────────"
    } >> "$REPORT_FILE"

    (
        cd "$service_path" && ls -1 *.py *.json *.yml *.yaml *.txt *.md 2>/dev/null | head -20 | sed 's/^/  /'
    ) >> "$REPORT_FILE"

    # 9. STATUS SUMMARY
    {
        echo ""
        echo "9. STATUS SUMMARY:"
        echo "  ────────────────"
        echo "  Entry Point: $entry_point"
        echo "  Framework: $framework"
        echo "  Port: $port"
        echo "  Venv: $venv_status"
        echo "  Python: $venv_py_version"
        echo ""
    } >> "$REPORT_FILE"
done

# Print summary to console
{
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "AUDIT SUMMARY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Total Services Audited: ${#services[@]}"
    echo ""
    echo "Services:"
    for service in "${services[@]}"; do
        echo "  • $service"
    done
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
} >> "$REPORT_FILE"

# Display report
echo -e "${GREEN}✓ Audit complete!${NC}"
echo ""
echo -e "${YELLOW}Report saved to:${NC}"
echo -e "  ${CYAN}$REPORT_FILE${NC}"
echo ""
echo -e "${YELLOW}To view the report:${NC}"
echo "  cat $REPORT_FILE"
echo "  less $REPORT_FILE"
echo ""
echo -e "${YELLOW}Services audited:${NC}"
for service in "${services[@]}"; do
    echo "  • $service"
done
