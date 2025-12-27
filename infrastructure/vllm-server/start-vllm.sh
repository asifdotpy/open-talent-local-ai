#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  OpenTalent vLLM Production Server Startup                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

echo "🚀 Starting OpenTalent vLLM Production Server"
echo "==========================================="

# Configuration
CONFIG_FILE="/app/vllm-config.yaml"
MODEL_DIR="/models"
LOG_FILE="/app/vllm-server.log"

# Create model directory if it doesn't exist
mkdir -p $MODEL_DIR

# Set environment variables for optimal performance
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export VLLM_LOGGING_LEVEL=INFO

echo "📋 Configuration:"
echo "   Config: $CONFIG_FILE"
echo "   Model Dir: $MODEL_DIR"
echo "   Log File: $LOG_FILE"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "🔄 Starting vLLM server..."
echo "   This may take several minutes to download and load the model..."

# Start vLLM server with configuration
python3 -m vllm.entrypoints.openai.api_server \
    --config $CONFIG_FILE \
    --download-dir $MODEL_DIR \
    2>&1 | tee $LOG_FILE

echo "✅ vLLM server started successfully"
