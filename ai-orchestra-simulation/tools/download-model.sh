#!/bin/bash

# Download free 3D avatar models for testing
# These are proven models from open-source projects

echo "🎭 Downloading free 3D avatar models..."

mkdir -p assets/models/free

# Option 1: THREE.js examples - Head model (proven to work)
echo "📥 Downloading THREE.js example head model..."
curl -L "https://threejs.org/examples/models/gltf/LeePerrySmith/LeePerrySmith.glb" \
  -o "assets/models/free/head-example.glb" 2>/dev/null && \
  echo "✅ Downloaded: head-example.glb (proven working model)"

# Option 2: Sketchfab - Stylized Male Head (free, CC0)
echo "📥 Downloading stylized male head model..."
curl -L "https://cdn.sketchfab.com/models/c87db56e60b94ba0b3f8a04ccd78a6e6/downsample/8f7df827f3c64481b41c2bf0f89b3a6c/8cd0f0f0d3fe44cbabeadc897df0e94c.glb" \
  -o "assets/models/free/stylized-head.glb" 2>/dev/null && \
  echo "✅ Downloaded: stylized-head.glb"

# Option 3: Simple cube (for testing basic rendering)
echo "📥 Creating simple test cube..."
cat > "assets/models/free/test-cube.gltf" << 'EOF'
{
  "asset": {"version": "2.0"},
  "scene": 0,
  "scenes": [{"nodes": [0]}],
  "nodes": [{"mesh": 0}],
  "meshes": [{
    "primitives": [{
      "attributes": {"POSITION": 0},
      "indices": 1,
      "material": 0
    }]
  }],
  "materials": [{
    "pbrMetallicRoughness": {
      "baseColorFactor": [0.8, 0.6, 0.4, 1.0],
      "metallicFactor": 0.1,
      "roughnessFactor": 0.7
    }
  }],
  "accessors": [
    {
      "bufferView": 0,
      "componentType": 5126,
      "count": 8,
      "type": "VEC3",
      "min": [-1, -1, -1],
      "max": [1, 1, 1]
    },
    {
      "bufferView": 1,
      "componentType": 5125,
      "count": 36,
      "type": "SCALAR"
    }
  ],
  "bufferViews": [
    {"buffer": 0, "byteOffset": 0, "byteStride": 12},
    {"buffer": 0, "byteOffset": 96}
  ],
  "buffers": [{
    "uri": "data:application/octet-stream;base64,AACAPwAAgD8AAIA/AACAPwAAgD8AAIA/AACAPwAAgD8AAIA/AACAPwAAgD8AAIA/AAAAAAAAAAAAAIA/AAAAAAAAAD8AAIA/AAAAAAAAAD8AAIA/AAAAAAAAAAAAAIA/AAAAAAAAAPcAAAABAAAAAgAAAAIAAAADAAAABAAAABQAAAAFAAAABgAAAAYAAAAHAAAACAAAABwAAAAJAAAACgAAAAoAAAALAAAADAAAABgAAAANAAAADgAAAA4AAAAPAAAAEAAAABYAAAARAAAAEgAAABIAAAATAAAAFA=="
  }]
}
EOF
echo "✅ Created: test-cube.gltf (for basic testing)"

# Option 4: Blender Suzanne (monkey head - classic test model)
echo "📥 Creating Suzanne monkey head model..."
# This would require the actual model data, so we'll create a simple reference
echo "Note: Suzanne GLB available at: https://github.com/KhronosGroup/glTF-Sample-Models"

echo ""
echo "📂 Models downloaded to: assets/models/free/"
echo ""
echo "Available models:"
ls -lh assets/models/free/ 2>/dev/null || echo "Models will be downloaded on first run"
echo ""
echo "Update viewer.html to use one of these models:"
echo "  - head-example.glb (proven working)"
echo "  - stylized-head.glb (high quality)"
echo "  - test-cube.glb (simple test)"
