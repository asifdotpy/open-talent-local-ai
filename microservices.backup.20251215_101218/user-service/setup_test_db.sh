#!/bin/bash

# Test Database Setup Script
# This script helps set up a temporary PostgreSQL database for testing

echo "Setting up test database for talent-ai-user-service..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found. Setting up test PostgreSQL container..."
    
    # Stop and remove existing test container if it exists
    docker stop postgres-test-user-service 2>/dev/null || true
    docker rm postgres-test-user-service 2>/dev/null || true
    
    # Start new PostgreSQL container for testing
    docker run --name postgres-test-user-service \
        -e POSTGRES_USER=testuser \
        -e POSTGRES_PASSWORD=testpass \
        -e POSTGRES_DB=test_user_service \
        -p 5433:5432 \
        -d postgres:15
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Set environment variable
    export TEST_DATABASE_URL="postgresql://testuser:testpass@localhost:5433/test_user_service"
    echo "✅ Test database URL: $TEST_DATABASE_URL"
    
    echo ""
    echo "🚀 Ready to run tests! Use:"
    echo "   export TEST_DATABASE_URL=\"postgresql://testuser:testpass@localhost:5433/test_user_service\""
    echo "   pytest tests/ -v"
    echo ""
    echo "🧹 To clean up after testing:"
    echo "   docker stop postgres-test-user-service"
    echo "   docker rm postgres-test-user-service"
    
else
    echo "❌ Docker not found. Please install Docker or set up PostgreSQL manually."
    echo ""
    echo "Manual setup:"
    echo "1. Create a test database:"
    echo "   CREATE DATABASE test_user_service;"
    echo "   CREATE USER testuser WITH PASSWORD 'testpass';"
    echo "   GRANT ALL PRIVILEGES ON DATABASE test_user_service TO testuser;"
    echo ""
    echo "2. Set environment variable:"
    echo "   export TEST_DATABASE_URL=\"postgresql://testuser:testpass@localhost:5432/test_user_service\""
    echo ""
    echo "3. Run tests:"
    echo "   pytest tests/ -v"
fi
