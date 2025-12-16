#!/bin/bash

# Comprehensive Copy Script: microservices/ → services/
# Handles: root main.py, app/main.py, full directories, test preservation
# Date: December 15, 2025

set -e  # Exit on error

MICROSERVICES_DIR="/home/asif1/open-talent/microservices"
SERVICES_DIR="/home/asif1/open-talent/services"

echo "================================================================================"
echo "COMPREHENSIVE MICROSERVICES → SERVICES COPY"
echo "================================================================================"

# Step 1: Backup
echo ""
echo "=== Step 1: Backup existing services/ ==="
if [ -d "$SERVICES_DIR" ]; then
  BACKUP_DIR="${SERVICES_DIR}_backup_dec15_$(date +%s)"
  cp -r "$SERVICES_DIR" "$BACKUP_DIR"
  echo "✓ Backed up to: $BACKUP_DIR"
else
  echo "! services/ does not exist (creating)"
  mkdir -p "$SERVICES_DIR"
fi

# Step 2: Define all services with copy strategy
echo ""
echo "=== Step 2: Copy all services ==="

# Services with main.py in root
ROOT_MAIN_SERVICES=(
  "ai-auditing-service"
  "analytics-service"
  "avatar-service"
  "candidate-service"
  "conversation-service"
  "desktop-integration-service"
  "explainability-service"
  "interview-service"
  "notification-service"
  "scout-service"
  "security-service"
  "user-service"
)

# Services with main.py in app/ subdirectory (full structure)
APP_MAIN_SERVICES=(
  "granite-interview-service"
  "project-service"
)

# Voice-service: full directory (largest, special handling)
FULL_DIR_SERVICES=(
  "voice-service"
)

# Step 2a: Copy root main.py services
echo ""
echo "--- Copying services with root main.py ---"
for service in "${ROOT_MAIN_SERVICES[@]}"; do
  src="$MICROSERVICES_DIR/$service"
  dst="$SERVICES_DIR/$service"
  
  if [ ! -d "$src" ]; then
    echo "⚠ SKIP: $service (source not found)"
    continue
  fi
  
  # Ensure destination exists
  mkdir -p "$dst"
  
  # Copy main.py if it exists in root
  if [ -f "$src/main.py" ]; then
    cp "$src/main.py" "$dst/main.py"
    echo "✓ $service: main.py"
  fi
  
  # Copy requirements.txt if exists
  if [ -f "$src/requirements.txt" ]; then
    cp "$src/requirements.txt" "$dst/requirements.txt"
    echo "  + requirements.txt"
  fi
  
  # Copy Dockerfile if exists
  if [ -f "$src/Dockerfile" ]; then
    cp "$src/Dockerfile" "$dst/Dockerfile"
    echo "  + Dockerfile"
  fi
  
  # Copy .env.example if exists
  if [ -f "$src/.env.example" ]; then
    cp "$src/.env.example" "$dst/.env.example"
    echo "  + .env.example"
  fi
  
  # Copy pyproject.toml if exists
  if [ -f "$src/pyproject.toml" ]; then
    cp "$src/pyproject.toml" "$dst/pyproject.toml"
    echo "  + pyproject.toml"
  fi
  
  # Copy providers/ if exists (for notification-service)
  if [ -d "$src/providers" ]; then
    cp -r "$src/providers" "$dst/providers"
    echo "  + providers/"
  fi
  
  # Copy app/ if exists (user-service, etc)
  if [ -d "$src/app" ]; then
    cp -r "$src/app" "$dst/app"
    echo "  + app/"
  fi
  
  # Copy migrations/ if exists (user-service)
  if [ -d "$src/migrations" ]; then
    cp -r "$src/migrations" "$dst/migrations"
    echo "  + migrations/"
  fi
  
  # Preserve existing tests/ and merge if needed
  if [ -d "$src/tests" ] && [ ! -d "$dst/tests" ]; then
    cp -r "$src/tests" "$dst/tests"
    echo "  + tests/ (new)"
  elif [ -d "$src/tests" ] && [ -d "$dst/tests" ]; then
    # Merge: copy any test files from source that don't exist in destination
    for test_file in "$src/tests"/*; do
      test_name=$(basename "$test_file")
      if [ ! -f "$dst/tests/$test_name" ]; then
        cp "$test_file" "$dst/tests/$test_name"
        echo "  + tests/$test_name (merged)"
      fi
    done
  fi
done

# Step 2b: Copy app/ main.py services (full structure)
echo ""
echo "--- Copying services with app/main.py (full structure) ---"
for service in "${APP_MAIN_SERVICES[@]}"; do
  src="$MICROSERVICES_DIR/$service"
  dst="$SERVICES_DIR/$service"
  
  if [ ! -d "$src" ]; then
    echo "⚠ SKIP: $service (source not found)"
    continue
  fi
  
  # Ensure destination exists
  mkdir -p "$dst"
  
  # Copy entire app/ directory (contains main.py + structure)
  if [ -d "$src/app" ]; then
    cp -r "$src/app" "$dst/app"
    echo "✓ $service: app/ (with main.py)"
  fi
  
  # Copy requirements.txt
  if [ -f "$src/requirements.txt" ]; then
    cp "$src/requirements.txt" "$dst/requirements.txt"
    echo "  + requirements.txt"
  fi
  
  # Copy Dockerfile
  if [ -f "$src/Dockerfile" ]; then
    cp "$src/Dockerfile" "$dst/Dockerfile"
    echo "  + Dockerfile"
  fi
  
  # Copy docker-compose.yml if exists
  if [ -f "$src/docker-compose.yml" ]; then
    cp "$src/docker-compose.yml" "$dst/docker-compose.yml"
    echo "  + docker-compose.yml"
  fi
  
  # Copy pyproject.toml
  if [ -f "$src/pyproject.toml" ]; then
    cp "$src/pyproject.toml" "$dst/pyproject.toml"
    echo "  + pyproject.toml"
  fi
  
  # Copy data/ if exists (granite-interview-service)
  if [ -d "$src/data" ]; then
    cp -r "$src/data" "$dst/data"
    echo "  + data/"
  fi
  
  # Copy start.sh if exists
  if [ -f "$src/start.sh" ]; then
    cp "$src/start.sh" "$dst/start.sh"
    chmod +x "$dst/start.sh"
    echo "  + start.sh"
  fi
  
  # Copy config/ if exists in app/
  if [ -d "$src/app/config" ]; then
    echo "  + app/config/"
  fi
  
  # Preserve existing tests/
  if [ -d "$src/tests" ] && [ ! -d "$dst/tests" ]; then
    cp -r "$src/tests" "$dst/tests"
    echo "  + tests/ (new)"
  elif [ -d "$src/tests" ] && [ -d "$dst/tests" ]; then
    for test_file in "$src/tests"/*; do
      test_name=$(basename "$test_file")
      if [ ! -f "$dst/tests/$test_name" ]; then
        cp "$test_file" "$dst/tests/$test_name"
        echo "  + tests/$test_name (merged)"
      fi
    done
  fi
done

# Step 2c: Copy full directory services
echo ""
echo "--- Copying full-structure services ---"
for service in "${FULL_DIR_SERVICES[@]}"; do
  src="$MICROSERVICES_DIR/$service"
  dst="$SERVICES_DIR/$service"
  
  if [ ! -d "$src" ]; then
    echo "⚠ SKIP: $service (source not found)"
    continue
  fi
  
  # Remove destination if it exists (except tests/)
  if [ -d "$dst" ]; then
    # Backup tests/ from destination
    if [ -d "$dst/tests" ]; then
      cp -r "$dst/tests" "$dst/tests_backup_local"
    fi
    
    # Remove old destination
    rm -rf "$dst"
  fi
  
  # Copy entire source
  cp -r "$src" "$dst"
  echo "✓ $service: entire directory"
  
  # Restore local tests/ if had backup
  if [ -d "$dst/tests_backup_local" ]; then
    # Merge: keep source tests, add any local-only tests
    for test_file in "$dst/tests_backup_local"/*; do
      test_name=$(basename "$test_file")
      if [ ! -f "$dst/tests/$test_name" ]; then
        cp "$test_file" "$dst/tests/$test_name"
        echo "  + tests/$test_name (local, preserved)"
      fi
    done
    rm -rf "$dst/tests_backup_local"
  fi
  
  # Copy app/ contents if top-level main.py doesn't exist
  if [ ! -f "$dst/main.py" ] && [ -f "$dst/app/main.py" ]; then
    echo "  + app/main.py (app/ structure)"
  fi
done

# Step 3: Verify all services have main.py
echo ""
echo "=== Step 3: Verify main.py files ==="
MISSING=0
for service_dir in "$SERVICES_DIR"/*; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    
    # Check for root main.py or app/main.py
    if [ -f "$service_dir/main.py" ]; then
      echo "✓ $service_name/main.py"
    elif [ -f "$service_dir/app/main.py" ]; then
      echo "✓ $service_name/app/main.py"
    else
      echo "✗ $service_name - NO main.py FOUND"
      MISSING=$((MISSING + 1))
    fi
  fi
done

echo ""
echo "=== Step 4: Port conflict check ==="
echo "Scanning for port conflicts..."

# Extract port numbers from main.py files
declare -A port_map
for service_dir in "$SERVICES_DIR"/*; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    
    # Check root main.py
    if [ -f "$service_dir/main.py" ]; then
      port=$(grep -oP '(?<=port=)\d+' "$service_dir/main.py" | head -1 || echo "unknown")
      if [ "$port" != "unknown" ]; then
        if [ -n "${port_map[$port]}" ]; then
          echo "⚠ PORT CONFLICT: $port used by both ${port_map[$port]} and $service_name"
        else
          port_map[$port]="$service_name"
          echo "  $service_name: port $port"
        fi
      fi
    fi
    
    # Check app/main.py
    if [ -f "$service_dir/app/main.py" ]; then
      port=$(grep -oP '(?<=port=)\d+' "$service_dir/app/main.py" | head -1 || echo "unknown")
      if [ "$port" != "unknown" ]; then
        if [ -n "${port_map[$port]}" ]; then
          echo "⚠ PORT CONFLICT: $port used by both ${port_map[$port]} and $service_name"
        else
          port_map[$port]="$service_name"
          echo "  $service_name: port $port"
        fi
      fi
    fi
  fi
done

echo ""
echo "================================================================================"
echo "COPY SUMMARY"
echo "================================================================================"

# Count services
total_services=$(find "$SERVICES_DIR" -maxdepth 1 -type d | grep -v "^$SERVICES_DIR$" | wc -l)
echo "Total services in services/: $total_services"

if [ $MISSING -gt 0 ]; then
  echo "⚠ WARNING: $MISSING services missing main.py"
else
  echo "✓ All services have main.py"
fi

echo ""
echo "Backup location: $BACKUP_DIR"
echo "Services directory: $SERVICES_DIR"
echo ""
echo "Next steps:"
echo "  1. Verify imports: python -m py_compile services/*/main.py"
echo "  2. Check tests: find services/ -name 'test_*.py' | wc -l"
echo "  3. Update documentation to reference services/"
echo ""
echo "================================================================================"
