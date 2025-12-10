#!/bin/bash

###############################################################################
# OpenTalent Model Setup Script
# 
# This script downloads and configures custom trained models for OpenTalent
# Usage: ./setup-models.sh [--model 2b|1b|all]
###############################################################################

set -e

echo "🚀 OpenTalent Model Setup"
echo "=========================="
echo ""

# Parse arguments
MODEL=${1:-all}

# Create models directory
MODELS_DIR="$HOME/OpenTalent/models"
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

echo "📁 Models directory: $MODELS_DIR"
echo ""

# Function to download model from HuggingFace
download_model() {
  local model_name=$1
  local hf_url=$2
  local filename=$3
  
  echo "📥 Downloading $model_name (~${4})..."
  
  if [ -f "$filename" ]; then
    echo "   ✅ Already downloaded, skipping"
    return
  fi
  
  # Try wget first
  if command -v wget &> /dev/null; then
    wget "$hf_url" -O "$filename" --progress=bar:force 2>&1
  # Fall back to curl
  elif command -v curl &> /dev/null; then
    curl -L "$hf_url" -o "$filename" -# 
  else
    echo "   ❌ Error: Neither wget nor curl found"
    echo "   Please install wget or curl and try again"
    exit 1
  fi
  
  echo "   ✅ Downloaded successfully"
  echo ""
}

# Function to create Ollama model
create_ollama_model() {
  local model_id=$1
  local modelfile_path=$2
  
  echo "🔧 Creating Ollama model: $model_id..."
  
  # Check if model already exists
  if ollama list | grep -q "^$model_id"; then
    echo "   ✅ Model already exists in Ollama"
    return
  fi
  
  # Create model
  if ollama create "$model_id" -f "$modelfile_path"; then
    echo "   ✅ Model created successfully"
  else
    echo "   ❌ Error creating model"
    exit 1
  fi
  
  echo ""
}

# Setup Granite 2B GGUF
setup_granite_2b_gguf() {
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Granite 2B GGUF (Recommended - Highest Quality)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Download model
  download_model \
    "Granite 2B GGUF" \
    "https://huggingface.co/asifdotpy/vetta-granite-2b-gguf-v4/resolve/main/model.gguf" \
    "vetta-granite-2b-gguf-v4.gguf" \
    "1.2GB"
  
  # Create Modelfile
  echo "📝 Creating Modelfile..."
  cat > "Modelfile-2b" << 'EOF'
FROM ./vetta-granite-2b-gguf-v4.gguf
TEMPLATE "[INST] {{ .Prompt }} [/INST]"
PARAMETERS stop [INST] stop [/INST] stop </s>
SYSTEM You are an expert technical interviewer conducting structured interviews for software engineering, product management, and data analyst roles. Ask insightful questions that assess technical knowledge, problem-solving ability, and soft skills. Keep responses professional and constructive.
EOF
  echo "   ✅ Modelfile created"
  echo ""
  
  # Create Ollama model
  create_ollama_model "vetta-granite-2b-gguf-v4" "Modelfile-2b"
}

# Setup Llama 3.2 1B
setup_llama_1b() {
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Llama 3.2 1B (Fallback - Included with Ollama)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check if already available
  if ollama list | grep -q "llama3.2:1b"; then
    echo "✅ llama3.2:1b already available in Ollama"
    echo "   (Standard Ollama model, no download needed)"
    echo ""
    return
  fi
  
  echo "📥 Downloading Llama 3.2 1B (via Ollama)..."
  if ollama pull llama3.2:1b; then
    echo "✅ Downloaded successfully"
  else
    echo "⚠️  Could not download. Check Ollama connection."
  fi
  echo ""
}

# Verify Ollama is running
verify_ollama() {
  echo "🔍 Verifying Ollama is running..."
  
  if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found in PATH"
    echo "   Please install Ollama from https://ollama.ai"
    exit 1
  fi
  
  # Try to connect to Ollama server
  if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama server is running on localhost:11434"
  else
    echo "⚠️  Ollama server not responding at localhost:11434"
    echo "   Start Ollama with: ollama serve"
    echo "   Then run this script again"
    exit 1
  fi
  echo ""
}

# List available models
list_models() {
  echo "📋 Available models after setup:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  ollama list
  echo ""
}

# Test custom model
test_model() {
  echo "🧪 Testing custom model..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if ollama list | grep -q "vetta-granite-2b-gguf-v4"; then
    echo "Asking Granite 2B: 'What data structures would you use to implement an LRU cache?'"
    echo ""
    echo "Model response:"
    echo "─────────────────────────────────────────────────────────────────────"
    
    # Run simple test (timeout after 30s)
    timeout 30 ollama run vetta-granite-2b-gguf-v4 \
      "[INST] What data structures would you use to implement an LRU cache? [/INST]" \
      2>/dev/null || echo "⏱️  Response generation in progress (can take 1-5 minutes)..."
    
    echo "─────────────────────────────────────────────────────────────────────"
    echo "✅ Model test complete!"
  else
    echo "⚠️  Custom model not found. Run setup first."
  fi
  echo ""
}

# Main execution
main() {
  echo "Checking prerequisites..."
  verify_ollama
  
  case "$MODEL" in
    2b|2b-gguf|granite-2b)
      setup_granite_2b_gguf
      ;;
    1b|llama|llama-1b)
      setup_llama_1b
      ;;
    all|*)
      setup_granite_2b_gguf
      setup_llama_1b
      ;;
  esac
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Model setup complete!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  list_models
  
  echo "📖 Next Steps:"
  echo "1. Run interview tests: npm run test"
  echo "2. Start the desktop app: npm run dev"
  echo "3. Select Granite 2B in model selection UI"
  echo "4. Start an interview to test!"
  echo ""
  
  # Offer to run test
  read -p "Would you like to test the custom model now? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    test_model
  fi
  
  echo "✨ Ready to use OpenTalent with custom models!"
}

# Run main function
main
