#!/usr/bin/env python3
"""
Merge Vetta AI v4 LoRA adapters with base Granite model and export for Ollama.

This script:
1. Loads the base Granite 3.0 2B Instruct model
2. Merges the LoRA adapters from vetta-granite-2b-lora-v4
3. Exports the merged model in GGUF format for Ollama
4. Creates a Modelfile for Ollama configuration

Requirements:
- unsloth
- torch
- transformers
- llama-cpp-python (for GGUF conversion)

Usage:
    python merge_and_export_for_ollama.py [--output-dir OUTPUT_DIR] [--quantize q4_k_m]
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import torch
    from transformers import AutoTokenizer
    from unsloth import FastLanguageModel
except ImportError as e:
    print(f"Error: Missing required dependencies: {e}")
    print("\nInstall with:")
    print("  pip install 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'")
    print("  pip install torch transformers")
    sys.exit(1)


def merge_lora_adapters(
    base_model_name: str = "ibm-granite/granite-3.0-2b-instruct",
    lora_model_name: str = "asifdotpy/vetta-granite-2b-lora-v4",
    output_dir: str = "./vetta-granite-merged",
    max_seq_length: int = 2048,
):
    """
    Merge LoRA adapters with base model.

    Args:
        base_model_name: HuggingFace model ID for base model
        lora_model_name: HuggingFace model ID for LoRA adapters
        output_dir: Directory to save merged model
        max_seq_length: Maximum sequence length

    Returns:
        Path to merged model directory
    """
    print(f"🔄 Loading base model: {base_model_name}")
    print(f"🔄 Loading LoRA adapters: {lora_model_name}")

    # Load model with LoRA adapters
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=lora_model_name,
        max_seq_length=max_seq_length,
        dtype=None,  # Auto-detect
        load_in_4bit=False,  # We want full precision for merging
    )

    print("✅ Model and adapters loaded successfully")
    print(f"📊 Model dtype: {model.dtype}")
    print(f"📊 Model device: {model.device}")

    # Merge LoRA weights into base model
    print("\n🔀 Merging LoRA adapters into base model...")
    model = model.merge_and_unload()

    print("✅ LoRA adapters merged successfully")

    # Save merged model
    print(f"\n💾 Saving merged model to: {output_dir}")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    print("✅ Merged model saved successfully")
    print(f"📁 Model location: {output_path.absolute()}")

    return str(output_path.absolute())


def export_to_gguf(
    model_dir: str,
    output_file: str = "vetta-granite-2b-merged.gguf",
    quantization: str = "q4_k_m",
):
    """
    Export merged model to GGUF format for Ollama.

    Args:
        model_dir: Directory containing merged model
        output_file: Output GGUF filename
        quantization: Quantization method (q4_k_m, q5_k_m, q8_0, f16, f32)

    Returns:
        Path to GGUF file
    """
    try:
        from llama_cpp import Llama
    except ImportError:
        print("\n⚠️  llama-cpp-python not installed")
        print("📝 Manual conversion steps:")
        print(f"\n1. Install llama.cpp:")
        print("   git clone https://github.com/ggerganov/llama.cpp")
        print("   cd llama.cpp && make")
        print(f"\n2. Convert to GGUF:")
        print(f"   python llama.cpp/convert.py {model_dir} --outfile {output_file}")
        print(f"\n3. Quantize (optional):")
        print(f"   ./llama.cpp/quantize {output_file} vetta-granite-2b-{quantization}.gguf {quantization.upper()}")
        return None

    print(f"\n🔄 Converting to GGUF format (quantization: {quantization})...")

    # Note: This is a placeholder - actual GGUF conversion requires llama.cpp
    # The proper way is to use llama.cpp's convert.py script
    print("⚠️  GGUF conversion requires manual steps with llama.cpp")
    print("📝 See instructions above")

    return None


def create_modelfile(
    model_path: str,
    output_dir: str = ".",
    model_name: str = "vetta-granite-2b",
):
    """
    Create Ollama Modelfile for the merged model.

    Args:
        model_path: Path to GGUF model file
        output_dir: Directory to save Modelfile
        model_name: Name for the Ollama model
    """
    modelfile_content = f"""# Vetta AI v4 - Granite 3.0 2B Merged Model
# Fine-tuned for recruiting across 8 domains

FROM {model_path}

# Template for Alpaca format
TEMPLATE \"\"\"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{{{{ .Prompt }}}}

### Input:
{{{{ .Context }}}}

### Response:
\"\"\"

# System prompt
SYSTEM \"\"\"You are Vetta AI, an expert recruiting assistant trained across 8 domains:
1. Interview - Avatar interview orchestration and question generation
2. Sourcing - Candidate discovery and talent pool building
3. Search - Boolean query generation and optimization
4. Engagement - Personalized outreach and communication
5. Discovery - Platform scanning and profile extraction
6. Quality - Candidate scoring and assessment
7. Market - Salary intelligence and competitive analysis
8. Integration - ATS/CRM synchronization workflows

You provide professional, actionable insights for hiring managers, recruiters, and interview coordinators.\"\"\"

# Parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 2048

# Stop sequences
PARAMETER stop "### Instruction:"
PARAMETER stop "### Input:"
PARAMETER stop "### Response:"
"""

    modelfile_path = Path(output_dir) / "Modelfile"
    modelfile_path.write_text(modelfile_content)

    print(f"\n✅ Modelfile created: {modelfile_path.absolute()}")
    print(f"\n📝 To use with Ollama:")
    print(f"   ollama create {model_name} -f {modelfile_path}")
    print(f"   ollama run {model_name}")

    return str(modelfile_path.absolute())


def create_ollama_usage_guide(output_dir: str):
    """Create usage guide for Ollama integration."""
    guide_content = """# Using Vetta AI v4 with Ollama

## Quick Start

### 1. Convert Model to GGUF (Manual Steps)

Since the model is currently in HuggingFace format, you need to convert it:

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Convert merged model to GGUF
python convert.py /path/to/vetta-granite-merged --outfile vetta-granite-2b.gguf

# Quantize for efficiency (optional but recommended)
./quantize vetta-granite-2b.gguf vetta-granite-2b-q4_k_m.gguf q4_k_m
```

### 2. Create Ollama Model

```bash
# Use the generated Modelfile
ollama create vetta-granite-2b -f Modelfile

# Or create manually
cat > Modelfile << 'EOF'
FROM ./vetta-granite-2b-q4_k_m.gguf

TEMPLATE """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{{ .Prompt }}

### Input:
{{ .Context }}

### Response:
"""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF

ollama create vetta-granite-2b -f Modelfile
```

### 3. Use the Model

**Command Line:**
```bash
ollama run vetta-granite-2b "Assess this candidate: 5 years Python, Django expert"
```

**Python API:**
```python
import ollama

response = ollama.chat(model='vetta-granite-2b', messages=[
    {
        'role': 'user',
        'content': 'Assess this candidate: 5 years Python, Django expert, for Senior Python Developer role'
    }
])
print(response['message']['content'])
```

**REST API:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "vetta-granite-2b",
  "prompt": "Generate an interview question for a Senior Python Developer with 5 years experience.",
  "stream": false
}'
```

## Integration with Interview Service

Update `microservices/interview-service/services/vetta_ai.py`:

```python
import ollama

class VettaAI:
    def __init__(self, model_name="vetta-granite-2b"):
        self.model_name = model_name
        self.ollama_available = self._check_ollama()

    def _check_ollama(self):
        try:
            ollama.list()
            return True
        except:
            return False

    def generate(self, instruction, context="", max_tokens=256, temperature=0.7):
        if not self.ollama_available:
            return self._fallback_generate(instruction, context)

        prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context.

### Instruction:
{instruction}

### Input:
{context}

### Response:
"""

        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                'temperature': temperature,
                'num_predict': max_tokens,
            }
        )

        return response['response']
```

## 8 Domain Use Cases

### 1. Interview - Question Generation
```bash
ollama run vetta-granite-2b "Generate an interview question for a candidate with 5 years Python experience applying for Senior Developer role"
```

### 2. Sourcing - Candidate Discovery
```bash
ollama run vetta-granite-2b "Suggest platforms to find senior Python developers with AWS experience"
```

### 3. Search - Boolean Queries
```bash
ollama run vetta-granite-2b "Create a boolean search query for LinkedIn to find Python developers with 5+ years experience"
```

### 4. Engagement - Outreach
```bash
ollama run vetta-granite-2b "Write a personalized outreach message for Sarah Chen, a Python/AWS expert, for Senior Backend Engineer role at OpenTalent"
```

### 5. Discovery - Profile Analysis
```bash
ollama run vetta-granite-2b "Analyze this GitHub profile: 50 Python repos, 1000+ stars, active contributor to Django"
```

### 6. Quality - Candidate Scoring
```bash
ollama run vetta-granite-2b "Score this candidate (1-10): 5 years Python, Django, AWS, led team of 3, for Senior Python Developer role"
```

### 7. Market - Salary Intelligence
```bash
ollama run vetta-granite-2b "What's the market salary range for Senior Python Developer with 5 years experience in San Francisco?"
```

### 8. Integration - ATS Sync
```bash
ollama run vetta-granite-2b "What fields should I map when syncing candidates from LinkedIn to Greenhouse ATS?"
```

## Performance Tips

1. **Quantization:** Use q4_k_m for best balance (4-bit, ~2GB model size)
2. **Context Length:** Keep prompts under 2048 tokens for best performance
3. **Batch Processing:** Process multiple candidates in batches
4. **Caching:** Ollama automatically caches models in memory

## Troubleshooting

**Model not found:**
```bash
ollama list  # Check if model exists
ollama pull vetta-granite-2b  # If using registry
```

**Slow responses:**
```bash
# Check Ollama is using GPU
ollama ps
# Use lighter quantization (q4_0 instead of q4_k_m)
```

**Out of memory:**
```bash
# Use more aggressive quantization
./quantize vetta-granite-2b.gguf vetta-granite-2b-q4_0.gguf q4_0
```
"""

    guide_path = Path(output_dir) / "OLLAMA_USAGE_GUIDE.md"
    guide_path.write_text(guide_content)

    print(f"✅ Usage guide created: {guide_path.absolute()}")

    return str(guide_path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Merge Vetta AI v4 LoRA adapters and export for Ollama"
    )
    parser.add_argument(
        "--output-dir",
        default="./vetta-granite-merged",
        help="Output directory for merged model (default: ./vetta-granite-merged)",
    )
    parser.add_argument(
        "--quantization",
        default="q4_k_m",
        choices=["q4_0", "q4_k_m", "q5_0", "q5_k_m", "q8_0", "f16", "f32"],
        help="Quantization method for GGUF (default: q4_k_m)",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Skip merging step (use if already merged)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Vetta AI v4 → Ollama Export Tool")
    print("=" * 60)

    # Step 1: Merge LoRA adapters
    if not args.skip_merge:
        model_dir = merge_lora_adapters(output_dir=args.output_dir)
    else:
        model_dir = args.output_dir
        print(f"⏭️  Skipping merge, using existing model at: {model_dir}")

    # Step 2: Create Modelfile
    gguf_path = f"{model_dir}/vetta-granite-2b-{args.quantization}.gguf"
    modelfile_path = create_modelfile(
        model_path=gguf_path,
        output_dir=args.output_dir,
    )

    # Step 3: Create usage guide
    guide_path = create_ollama_usage_guide(args.output_dir)

    # Step 4: Export to GGUF (manual steps)
    print("\n" + "=" * 60)
    print("  📋 Next Steps for GGUF Conversion")
    print("=" * 60)
    print(f"\n1️⃣  Install llama.cpp:")
    print("   git clone https://github.com/ggerganov/llama.cpp")
    print("   cd llama.cpp && make")
    print(f"\n2️⃣  Convert to GGUF:")
    print(f"   python llama.cpp/convert.py {model_dir} --outfile vetta-granite-2b.gguf")
    print(f"\n3️⃣  Quantize for efficiency:")
    print(f"   ./llama.cpp/quantize vetta-granite-2b.gguf vetta-granite-2b-{args.quantization}.gguf {args.quantization.upper()}")
    print(f"\n4️⃣  Create Ollama model:")
    print(f"   mv vetta-granite-2b-{args.quantization}.gguf {model_dir}/")
    print(f"   ollama create vetta-granite-2b -f {modelfile_path}")
    print(f"\n5️⃣  Test the model:")
    print("   ollama run vetta-granite-2b 'Assess this candidate: 5 years Python, Django expert'")

    print(f"\n📚 Full guide: {guide_path}")
    print("\n✅ Merge complete! Follow the steps above to create GGUF and use with Ollama.")


if __name__ == "__main__":
    main()
