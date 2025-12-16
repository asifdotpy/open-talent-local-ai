#!/bin/bash

# Simple, robust copy script for remaining services
# Handles both root main.py and app/main.py

SRC="/home/asif1/open-talent/microservices"
DST="/home/asif1/open-talent/services"

# Services still needing copy (root main.py only)
SERVICES=(
  "conversation-service"
  "desktop-integration-service"
  "explainability-service"
  "interview-service"
  "scout-service"
  "voice-service"
)

# Services with app/main.py (full structure)
APP_SERVICES=(
  "granite-interview-service"
  "project-service"
)

echo "=== Copying Root main.py Services ==="
for svc in "${SERVICES[@]}"; do
  echo ""
  echo ">>> $svc"
  
  # Ensure destination exists
  mkdir -p "$DST/$svc"
  
  # Copy main.py
  [ -f "$SRC/$svc/main.py" ] && cp "$SRC/$svc/main.py" "$DST/$svc/" && echo "  + main.py"
  
  # Copy requirements, config, env
  [ -f "$SRC/$svc/requirements.txt" ] && cp "$SRC/$svc/requirements.txt" "$DST/$svc/" && echo "  + requirements.txt"
  [ -f "$SRC/$svc/pyproject.toml" ] && cp "$SRC/$svc/pyproject.toml" "$DST/$svc/" && echo "  + pyproject.toml"
  [ -f "$SRC/$svc/.env.example" ] && cp "$SRC/$svc/.env.example" "$DST/$svc/" && echo "  + .env.example"
  [ -f "$SRC/$svc/Dockerfile" ] && cp "$SRC/$svc/Dockerfile" "$DST/$svc/" && echo "  + Dockerfile"
  [ -f "$SRC/$svc/docker-compose.yml" ] && cp "$SRC/$svc/docker-compose.yml" "$DST/$svc/" && echo "  + docker-compose.yml"
  [ -f "$SRC/$svc/pytest.ini" ] && cp "$SRC/$svc/pytest.ini" "$DST/$svc/" && echo "  + pytest.ini"
  
  # Copy app/ if exists
  [ -d "$SRC/$svc/app" ] && cp -r "$SRC/$svc/app" "$DST/$svc/" && echo "  + app/"
  
  # Copy migrations/ if exists
  [ -d "$SRC/$svc/migrations" ] && cp -r "$SRC/$svc/migrations" "$DST/$svc/" && echo "  + migrations/"
  
  # Copy models/ if exists
  [ -d "$SRC/$svc/models" ] && cp -r "$SRC/$svc/models" "$DST/$svc/" && echo "  + models/"
  
  # Copy providers/ if exists
  [ -d "$SRC/$svc/providers" ] && cp -r "$SRC/$svc/providers" "$DST/$svc/" && echo "  + providers/"
  
  # Preserve tests/ from destination or copy from source
  if [ ! -d "$DST/$svc/tests" ]; then
    [ -d "$SRC/$svc/tests" ] && cp -r "$SRC/$svc/tests" "$DST/$svc/" && echo "  + tests/"
  fi
  
  # Copy special scripts
  [ -f "$SRC/$svc/start.sh" ] && cp "$SRC/$svc/start.sh" "$DST/$svc/" && chmod +x "$DST/$svc/start.sh" && echo "  + start.sh"
  [ -f "$SRC/$svc/run-tests.sh" ] && cp "$SRC/$svc/run-tests.sh" "$DST/$svc/" && chmod +x "$DST/$svc/run-tests.sh" && echo "  + run-tests.sh"
  [ -f "$SRC/$svc/test-*.sh" ] && cp "$SRC/$svc/test-"* "$DST/$svc/" 2>/dev/null && echo "  + test scripts"
  
done

echo ""
echo "=== Copying App-Based Services (app/main.py) ==="
for svc in "${APP_SERVICES[@]}"; do
  echo ""
  echo ">>> $svc"
  
  # Ensure destination exists
  mkdir -p "$DST/$svc"
  
  # Copy entire app/ directory
  [ -d "$SRC/$svc/app" ] && cp -r "$SRC/$svc/app" "$DST/$svc/" && echo "  + app/ (with main.py)"
  
  # Copy config
  [ -f "$SRC/$svc/requirements.txt" ] && cp "$SRC/$svc/requirements.txt" "$DST/$svc/" && echo "  + requirements.txt"
  [ -f "$SRC/$svc/pyproject.toml" ] && cp "$SRC/$svc/pyproject.toml" "$DST/$svc/" && echo "  + pyproject.toml"
  [ -f "$SRC/$svc/Dockerfile" ] && cp "$SRC/$svc/Dockerfile" "$DST/$svc/" && echo "  + Dockerfile"
  [ -f "$SRC/$svc/docker-compose.yml" ] && cp "$SRC/$svc/docker-compose.yml" "$DST/$svc/" && echo "  + docker-compose.yml"
  [ -f "$SRC/$svc/start.sh" ] && cp "$SRC/$svc/start.sh" "$DST/$svc/" && chmod +x "$DST/$svc/start.sh" && echo "  + start.sh"
  [ -f "$SRC/$svc/.env.example" ] && cp "$SRC/$svc/.env.example" "$DST/$svc/" && echo "  + .env.example"
  
  # Copy data/ if exists
  [ -d "$SRC/$svc/data" ] && cp -r "$SRC/$svc/data" "$DST/$svc/" && echo "  + data/"
  
  # Preserve tests/
  if [ ! -d "$DST/$svc/tests" ]; then
    [ -d "$SRC/$svc/tests" ] && cp -r "$SRC/$svc/tests" "$DST/$svc/" && echo "  + tests/"
  fi
done

echo ""
echo "=== Verification ==="
echo "Services with main.py:"
for dir in "$DST"/*; do
  svc=$(basename "$dir")
  [ "$svc" = "__pycache__" ] && continue
  if [ -f "$dir/main.py" ] || [ -f "$dir/app/main.py" ]; then
    echo "✓ $svc"
  else
    echo "✗ $svc"
  fi
done

echo ""
echo "=== COMPLETE ==="
