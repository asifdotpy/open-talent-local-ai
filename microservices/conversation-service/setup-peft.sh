#!/bin/bash
# Lightweight setup script for PEFT/LoRA model integration in conversation service

set -e

echo "🔄 Setting up PEFT/LoRA model integration for TalentAI Conversation Service..."
echo "📝 Note: Heavy computation (model packaging) should be done on Colab first!"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "app" ]; then
    echo "❌ Please run this script from the conversation-service directory"
    exit 1
fi

# Install lightweight dependencies (no heavy model downloads)
echo "📦 Installing lightweight PEFT dependencies..."
pip install torch transformers peft accelerate

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
else
    echo "ℹ️  .env file already exists"
fi

# Test basic PEFT imports (no model loading)
echo "🧪 Testing PEFT imports..."
python -c "
import sys
sys.path.append('.')

try:
    # Test imports
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel, PeftConfig
    from app.services.modular_llm_service import LLMProvider, LLMConfig
    
    print('✅ All PEFT dependencies imported successfully')
    print('✅ Modular LLM service imports working')
    
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 Lightweight PEFT setup complete!"
echo ""
echo "📋 IMPORTANT: Before running the service, you need to:"
echo ""
echo "1. 🚀 Run the Colab notebook to package the model:"
echo "   https://colab.research.google.com/notebook#fileId=package_peft_model_colab.ipynb"
echo ""
echo "2. 📝 Update .env file:"
echo "   LLM_PROVIDER=peft"
echo "   LLM_MODEL=asifdotpy/vetta-granite-2b-packaged-v3"
echo ""
echo "3. ▶️  Start the service:"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8003"
echo ""
echo "4. 🧪 Test the endpoint:"
echo "   curl -X POST http://localhost:8003/api/v1/interviews/generate-questions \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"job_description\": \"Python developer\", \"num_questions\": 3}'"
echo ""
echo "💡 For multiple personas: Create different packaged models and switch LLM_MODEL"