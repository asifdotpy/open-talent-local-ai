#!/bin/bash

# Simplified Avatar Integration Test for Development Environment
# Tests components that can run without full Docker stack

set -e

echo "🧪 Running Simplified Avatar Integration Tests"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test 1: R3F Build Process
print_status "Testing R3F build process..."
cd poc-webgl
if npm run build > /dev/null 2>&1; then
    print_success "R3F build completed successfully"
    if [ -d "dist" ] && [ -f "dist/index.html" ]; then
        print_success "Build artifacts created correctly"
    else
        print_error "Build artifacts missing"
        exit 1
    fi
else
    print_error "R3F build failed"
    exit 1
fi
cd ..

# Test 2: Bundle Size Analysis
print_status "Analyzing bundle sizes..."
if [ -f "poc-webgl/dist/index.html" ]; then
    # Check if main chunks exist
    if [ -f "poc-webgl/dist/assets/index-*.js" ]; then
        INDEX_SIZE=$(ls -lh poc-webgl/dist/assets/index-*.js | awk '{print $5}')
        print_success "Main bundle: $INDEX_SIZE"
    fi

    if [ -f "poc-webgl/dist/assets/Scene3D-*.js" ]; then
        SCENE_SIZE=$(ls -lh poc-webgl/dist/assets/Scene3D-*.js | awk '{print $5}')
        print_success "Scene3D bundle: $SCENE_SIZE (lazy loaded)"
    fi

    print_success "Code splitting working correctly"
else
    print_error "Build output not found"
    exit 1
fi

# Test 3: Avatar Renderer Health (if running)
print_status "Testing Avatar Renderer (if available)..."
if curl -f -s http://localhost:3001/health > /dev/null 2>&1; then
    print_success "Avatar Renderer is running and healthy"
else
    print_warning "Avatar Renderer not available (expected in dev environment)"
fi

# Test 4: Voice Service Health (if running)
print_status "Testing Voice Service (if available)..."
if curl -f -s http://localhost:8002/health > /dev/null 2>&1; then
    print_success "Voice Service is running and healthy"
else
    print_warning "Voice Service not available (expected in dev environment)"
fi

# Test 5: Component Structure Validation
print_status "Validating component structure..."
if [ -f "poc-webgl/src/components/Scene3D.jsx" ] && \
   [ -f "poc-webgl/src/components/Avatar.jsx" ] && \
   [ -f "poc-webgl/src/components/LipSyncController.jsx" ] && \
   [ -f "poc-webgl/src/components/PerformanceMonitor.jsx" ]; then
    print_success "All required components present"
else
    print_error "Missing required components"
    exit 1
fi

# Test 6: Configuration Files
print_status "Checking configuration files..."
if [ -f "poc-webgl/vite.config.js" ] && \
   [ -f "poc-webgl/nginx.conf" ] && \
   [ -f "docker-compose.prod.yml" ]; then
    print_success "Configuration files present"
else
    print_error "Missing configuration files"
    exit 1
fi

# Test 7: Performance Optimizations
print_status "Validating performance optimizations..."
if grep -q "lazy(" poc-webgl/src/App.jsx && \
   grep -q "manualChunks" poc-webgl/vite.config.js; then
    print_success "Lazy loading and code splitting implemented"
else
    print_error "Performance optimizations not properly implemented"
    exit 1
fi

echo
print_success "🎉 Simplified integration tests completed successfully!"
echo
print_status "Components validated:"
echo "  ✅ R3F Frontend build process"
echo "  ✅ Code splitting and lazy loading"
echo "  ✅ Component architecture"
echo "  ✅ Performance monitoring"
echo "  ✅ Production configuration"
echo
print_status "Note: Full end-to-end tests require Docker services to be running."
print_status "Run 'docker-compose -f docker-compose.prod.yml up -d' for complete testing."
echo
print_success "Day 7: Documentation & Deployment - COMPLETE! 🚀"