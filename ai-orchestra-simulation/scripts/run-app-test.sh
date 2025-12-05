#!/bin/bash

echo "🚀 Starting AI Orchestra Simulation with FaceCap Model..."
echo "📍 Server: http://localhost:8000"
echo "🎯 Target: Mouth animation with morph targets"
echo ""
echo "Open your browser and navigate to: http://localhost:8000"
echo "Then click the 'Start' button to initialize the application."
echo ""
echo "✅ Watch the console for:"
echo "   - Morph target detection"
echo "   - Mouth vertex initialization"
echo "   - Lip-sync animation (toggle via GUI)"
echo ""
echo "📊 Monitor performance in the GUI dashboard"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Show server logs
tail -f /tmp/server.log 2>/dev/null &
TAIL_PID=$!

# Wait for Ctrl+C
trap "kill $TAIL_PID 2>/dev/null; exit 0" INT

wait
