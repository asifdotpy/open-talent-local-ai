#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TalentAI - Ollama Multi-Persona Interviewer Setup                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

echo "🤖 Setting up Ollama Multi-Persona Interviewers for TalentAI"
echo "============================================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Check if granite3.0:2b is available
echo "🔍 Checking for base Granite model..."
if ! ollama list | grep -q "granite3.0:2b"; then
    echo "📥 Pulling Granite 3.0 2B model (this may take a few minutes)..."
    ollama pull granite3.0:2b
fi

# Create base interviewer model
echo "🏗️  Creating base interviewer model..."
ollama create granite-interviewer-base -f Modelfile.base

# Create persona-specific models
echo "🎭 Creating technical interviewer persona..."
ollama create granite-technical -f Modelfile.technical

echo "🎭 Creating behavioral interviewer persona..."
ollama create granite-behavioral -f Modelfile.behavioral

echo "🎭 Creating HR interviewer persona..."
ollama create granite-hr -f Modelfile.hr

echo ""
echo "✅ All interviewer personas created successfully!"
echo ""
echo "📋 Available Interviewer Personas:"
echo "   • granite-technical   - Technical/SWE focus"
echo "   • granite-behavioral  - Behavioral/soft skills focus"
echo "   • granite-hr          - HR/cultural fit focus"
echo ""
echo "🚀 Usage Examples:"
echo "   ollama run granite-technical"
echo "   ollama run granite-behavioral"
echo "   ollama run granite-hr"
echo ""
echo "⚙️  Next: Update your conversation service configuration"
echo "   to use these models instead of the PEFT approach."