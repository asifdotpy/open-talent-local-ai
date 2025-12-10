#!/bin/bash
#
# Quick Start: Test Data Enrichment Agent
# Run this script to test the vendor API integration
#

set -e

echo "=================================================="
echo "Data Enrichment Agent - Quick Start Test"
echo "=================================================="
echo ""

# Check if running from correct directory
if [ ! -d "agents/data-enrichment-agent" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "   Current: $(pwd)"
    echo "   Expected: /home/asif1/open-talent"
    exit 1
fi

cd agents/data-enrichment-agent

echo "Step 1: Install Python dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "Step 2: Check environment variables..."
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "📝 IMPORTANT: Edit .env and add your API keys:"
    echo "   - PROXYCURL_API_KEY (from https://nubela.co/proxycurl/)"
    echo "   - NUBELA_API_KEY (from https://nubela.co/nubela/)"
    echo "   - GOOGLE_CSE_API_KEY (from https://console.cloud.google.com/)"
    echo "   - GOOGLE_SEARCH_ENGINE_ID (from https://cse.google.com/)"
    echo ""
    echo "   Press ENTER after editing .env to continue..."
    read
fi

# Source .env
export $(cat .env | grep -v '^#' | xargs)

echo "✓ Environment variables loaded"
echo ""

echo "Step 3: Start Data Enrichment Agent..."
echo "   Port: 8097"
echo "   Press Ctrl+C to stop"
echo ""

# Start agent in background
python main.py &
AGENT_PID=$!

# Wait for agent to start
sleep 3

echo ""
echo "Step 4: Run health check..."
HEALTH=$(curl -s http://localhost:8097/health)
if [ $? -eq 0 ]; then
    echo "✓ Agent is healthy"
    echo "$HEALTH" | python -m json.tool
else
    echo "❌ Health check failed"
    kill $AGENT_PID
    exit 1
fi

echo ""
echo "Step 5: Add test credits..."
curl -s -X POST "http://localhost:8097/credits/test_user/add?amount=10.00" | python -m json.tool
echo "✓ Added $10 credits to test_user"

echo ""
echo "Step 6: Check available vendors..."
curl -s http://localhost:8097/vendors | python -m json.tool

echo ""
echo "=================================================="
echo "🎉 Success! Data Enrichment Agent is running"
echo "=================================================="
echo ""
echo "Try these commands:"
echo ""
echo "1. Enrich a LinkedIn profile (costs $0.02):"
echo '   curl -X POST http://localhost:8097/enrich -H "Content-Type: application/json" -d '"'"'{"pipeline_id": "test", "profile_urls": ["https://linkedin.com/in/williamhgates"], "vendor": "nubela", "user_id": "test_user"}'"'"
echo ""
echo "2. Check your credits:"
echo "   curl http://localhost:8097/credits/test_user"
echo ""
echo "3. View audit logs:"
echo "   curl http://localhost:8097/audit-logs?user_id=test_user"
echo ""
echo "4. Check cache stats:"
echo "   curl http://localhost:8097/cache/stats"
echo ""
echo "Press Ctrl+C to stop the agent"

# Keep script running
wait $AGENT_PID
