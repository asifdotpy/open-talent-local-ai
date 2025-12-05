#!/bin/bash

# TalentAI Platform - Quick Setup Script
# One-command setup for local development

set -e  # Exit on error

echo "🚀 TalentAI Platform Setup"
echo "=========================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Docker Compose found: $(docker compose version)"
echo ""

# Navigate to docker-compose directory
cd "$(dirname "$0")/.."

# Create .env from template if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit with your configuration."
    echo ""
    
    # Generate random passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    MINIO_PASSWORD=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    
    # Update .env with generated passwords
    sed -i "s/POSTGRES_PASSWORD=changeme_secure_password_here/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    sed -i "s/REDIS_PASSWORD=changeme_redis_password/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
    sed -i "s/MINIO_ROOT_PASSWORD=changeme_minio_password/MINIO_ROOT_PASSWORD=$MINIO_PASSWORD/" .env
    sed -i "s/JWT_SECRET_KEY=changeme_jwt_secret_key_32_chars_min/JWT_SECRET_KEY=$JWT_SECRET/" .env
    
    echo "🔐 Generated secure passwords in .env"
else
    echo "ℹ️  Using existing .env file"
fi

echo ""

# Pull latest images
echo "📦 Pulling Docker images..."
docker compose pull

# Build services
echo "🔨 Building services..."
docker compose build

# Create required directories
echo "📁 Creating required directories..."
mkdir -p ./init-scripts/postgres
mkdir -p ./backups/{postgres,redis,minio}
mkdir -p ./logs/nginx
mkdir -p ./nginx/ssl

# Start core infrastructure
echo "🚢 Starting core infrastructure (Postgres, Redis, MinIO)..."
docker compose up -d postgres redis minio

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Download Ollama model
echo "🤖 Pulling Ollama model (llama3.1:8b)..."
docker compose up -d ollama
sleep 5
docker exec talentai-ollama ollama pull llama3.1:8b || echo "⚠️  Ollama model download failed. Will retry later."

# Start all services
echo "🎯 Starting all services..."
docker compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Health check
echo "🏥 Running health checks..."
SERVICES=("avatar-service:8001" "voice-service:8002" "conversation-service:8003" "interview-service:8004" "scout-service:8005" "ai-auditing-service:8006" "analytics-service:8007" "explainability-service:8008" "project-service:8009" "candidate-service:8010" "notification-service:8011" "security-service:8012" "user-service:8013")

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -sf "http://localhost:$port/health" > /dev/null; then
        echo "  ✅ $name (port $port) - healthy"
    else
        echo "  ❌ $name (port $port) - unhealthy"
    fi
done

echo ""
echo "✨ Setup complete!"
echo ""
echo "📊 Access Points:"
echo "  - Nginx API Gateway: http://localhost:8080"
echo "  - Avatar Service: http://localhost:8001/docs"
echo "  - Voice Service: http://localhost:8002/docs"
echo "  - Conversation Service: http://localhost:8003/docs"
echo "  - Interview Service: http://localhost:8004/docs"
echo "  - Scout Service: http://localhost:8005/docs"
echo "  - AI Auditing Service: http://localhost:8006/docs"
echo "  - Analytics Service: http://localhost:8007/docs"
echo "  - Explainability Service: http://localhost:8008/docs"
echo "  - Project Service: http://localhost:8009/docs"
echo "  - Candidate Service: http://localhost:8010/docs"
echo "  - Notification Service: http://localhost:8011/docs"
echo "  - Security Service: http://localhost:8012/docs"
echo "  - User Service: http://localhost:8013/docs"
echo "  - MinIO Console: http://localhost:9001 (admin/password from .env)"
echo "  - PostgreSQL: localhost:5432 (credentials in .env)"
echo "  - Redis: localhost:6379 (password in .env)"
echo ""
echo "🛠️  Useful Commands:"
echo "  - View logs: docker compose logs -f [service-name]"
echo "  - Stop all: docker compose down"
echo "  - Restart service: docker compose restart [service-name]"
echo "  - View status: docker compose ps"
echo ""
echo "📖 Documentation: infrastructure/README.md"
