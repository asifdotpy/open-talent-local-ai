#!/bin/bash
# Quick Test Commands - Avatar Integration Test Suite
# Copy and paste these commands to run tests

echo "🧪 Avatar Integration Test Suite - Quick Commands"
echo "=================================================="
echo ""

# Check if services are running
echo "📋 Check Services:"
echo "curl -s http://localhost:8002/health | jq"
echo "curl -s http://localhost:8001/health | jq"  
echo "curl -s http://localhost:3001/health | jq"
echo ""

# Run all tests
echo "🎯 Run All Tests:"
echo "cd /home/asif1/talent-ai-platform && python tests/run_avatar_tests.py"
echo ""

# Run specific test types
echo "🔬 Unit Tests Only:"
echo "python tests/run_avatar_tests.py --unit"
echo ""

echo "🔗 Integration Tests Only:"
echo "python tests/run_avatar_tests.py --integration"
echo ""

echo "⚡ Quick Tests (Skip Slow):"
echo "python tests/run_avatar_tests.py --quick"
echo ""

# Run specific test files
echo "📁 Run Specific Test Files:"
echo "pytest tests/integration/test_avatar_integration.py -v"
echo "pytest tests/unit/test_phoneme_extractor.py -v"
echo "pytest tests/unit/test_avatar_renderer.py -v"
echo ""

# Run specific test classes
echo "📦 Run Specific Test Classes:"
echo "pytest tests/integration/test_avatar_integration.py::TestPhase1VoiceServicePhonemeExtraction -v"
echo "pytest tests/integration/test_avatar_integration.py::TestPhase2AvatarServiceRealRendering -v"
echo "pytest tests/integration/test_avatar_integration.py::TestEndToEndIntegration -v"
echo ""

# Run specific tests
echo "🎪 Run Individual Tests:"
echo "pytest tests/integration/test_avatar_integration.py::TestPhase1VoiceServicePhonemeExtraction::test_phoneme_extraction_endpoint -v"
echo "pytest tests/integration/test_avatar_integration.py::TestPhase2AvatarServiceRealRendering::test_avatar_video_generation -v"
echo "pytest tests/integration/test_avatar_integration.py::TestEndToEndIntegration::test_complete_text_to_video_pipeline -v"
echo ""

# Coverage
echo "📊 Run With Coverage:"
echo "pytest tests/ --cov=microservices/voice-service --cov=microservices/avatar-service --cov-report=html"
echo "firefox htmlcov/index.html  # View coverage report"
echo ""

# Start services
echo "🚀 Start Services (if needed):"
echo "# Terminal 1: Voice Service"
echo "cd microservices/voice-service && source .venv/bin/activate && python main.py"
echo ""
echo "# Terminal 2: Avatar Service"
echo "cd microservices/avatar-service && source venv/bin/activate && python main.py"
echo ""
echo "# Terminal 3: Avatar Renderer"
echo "cd ai-orchestra-simulation && node avatar-renderer-v2.js"
echo ""

# Watch mode
echo "👀 Watch Mode (Auto-rerun on changes):"
echo "pip install pytest-watch"
echo "ptw tests/ -- -v"
echo ""

# Verbose output
echo "🔊 Verbose Output:"
echo "python tests/run_avatar_tests.py --verbose"
echo ""

echo "✅ Done! Copy commands above as needed."
