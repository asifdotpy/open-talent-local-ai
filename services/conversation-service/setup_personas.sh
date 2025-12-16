#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TalentAI - Lightweight Persona Setup with Ollama LoRA               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

echo "🎭 Setting up TalentAI Interviewer Personas with Ollama + LoRA"
echo "================================================================="

# Check if Ollama is running
if ! ollama list > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Check if base model exists
if ! ollama list | grep -q "granite4:350m-h"; then
    echo "📥 Pulling base model: granite4:350m-h"
    ollama pull granite4:350m-h
    echo "✅ Base model downloaded"
else
    echo "✅ Base model granite4:350m-h already available"
fi

# Create Technical Interviewer
echo ""
echo "🔧 Creating Technical Interviewer persona..."
if ollama list | grep -q "technical-interviewer"; then
    echo "⚠️  Technical Interviewer model already exists. Removing..."
    ollama rm technical-interviewer
fi

ollama create technical-interviewer -f technical_interviewer.Modelfile
echo "✅ Technical Interviewer created"

# Create Behavioral Interviewer
echo ""
echo "🤝 Creating Behavioral Interviewer persona..."
if ollama list | grep -q "behavioral-interviewer"; then
    echo "⚠️  Behavioral Interviewer model already exists. Removing..."
    ollama rm behavioral-interviewer
fi

ollama create behavioral-interviewer -f behavioral_interviewer.Modelfile
echo "✅ Behavioral Interviewer created"

# Create HR Interviewer
echo ""
echo "🏢 Creating HR Interviewer persona..."
if ollama list | grep -q "hr-interviewer"; then
    echo "⚠️  HR Interviewer model already exists. Removing..."
    ollama rm hr-interviewer
fi

ollama create hr-interviewer -f hr_interviewer.Modelfile
echo "✅ HR Interviewer created"

echo ""
echo "🎉 All interviewer personas created successfully!"
echo ""
echo "📋 Available models:"
ollama list | grep interviewer

echo ""
echo "🧪 Test commands:"
echo "  ollama run technical-interviewer 'Generate 3 interview questions about Python'"
echo "  ollama run behavioral-interviewer 'Ask about a challenging team situation'"
echo "  ollama run hr-interviewer 'Discuss company culture fit'"

echo ""
echo "🚀 Next: Update conversation service to use these personas!"
echo "   Set LLM_MODEL to: technical-interviewer, behavioral-interviewer, or hr-interviewer"