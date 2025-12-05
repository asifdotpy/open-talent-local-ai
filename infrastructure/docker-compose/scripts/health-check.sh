#!/bin/bash

# TalentAI Platform - Health Check Script
# Validates all services are running and healthy

set -e

echo "🏥 TalentAI Platform Health Check"
echo "=================================="
echo ""

FAILED=0

# Check Docker containers
echo "📦 Container Status:"
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || {
    echo "❌ Docker Compose not running"
    exit 1
}

echo ""

# Check service health endpoints
echo "🔍 Service Health Checks:"

check_service() {
    local name=$1
    local port=$2
    local endpoint=${3:-/health}
    
    if curl -sf "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo "  ✅ $name (port $port)"
    else
        echo "  ❌ $name (port $port) - FAILED"
        FAILED=$((FAILED + 1))
    fi
}

check_service "Nginx Gateway" 8080 /health
check_service "Avatar Service" 8001 /health
check_service "Voice Service" 8002 /health
check_service "Conversation Service" 8003 /health
check_service "Interview Service" 8004 /health
check_service "Scout Service" 8005 /health
check_service "Analytics Service" 8007 /health

echo ""

# Check databases
echo "🗄️  Database Checks:"

# PostgreSQL
if docker exec talentai-postgres pg_isready -U talentai > /dev/null 2>&1; then
    echo "  ✅ PostgreSQL"
else
    echo "  ❌ PostgreSQL - FAILED"
    FAILED=$((FAILED + 1))
fi

# Redis
if docker exec talentai-redis redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Redis"
else
    echo "  ❌ Redis - FAILED"
    FAILED=$((FAILED + 1))
fi

# MinIO
if curl -sf "http://localhost:9000/minio/health/live" > /dev/null 2>&1; then
    echo "  ✅ MinIO"
else
    echo "  ❌ MinIO - FAILED"
    FAILED=$((FAILED + 1))
fi

# Ollama
if curl -sf "http://localhost:11434/api/tags" > /dev/null 2>&1; then
    echo "  ✅ Ollama"
else
    echo "  ⚠️  Ollama - Not responding (may still be starting)"
fi

echo ""

# Resource usage
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10

echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All critical services healthy!"
    exit 0
else
    echo "❌ $FAILED service(s) failed health check"
    exit 1
fi
