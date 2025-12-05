#!/bin/bash
set -e

echo "Setting up TalentAI Platform dev environment..."

# Start infrastructure services
echo "Starting PostgreSQL and Redis..."
cd config
docker-compose up -d
cd ..

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
docker-compose -f config/docker-compose.yml ps

echo "Dev environment is ready!"
echo "PostgreSQL: localhost:5433"
echo "Redis: localhost:6379"
echo ""
echo "To start working:"
echo "1. Navigate to a microservice: cd talent-ai-microservices/<service-name>"
echo "2. Create virtual environment: python3 -m venv venv"
echo "3. Activate it: source venv/bin/activate"
echo "4. Install dependencies: pip install -r requirements.txt"