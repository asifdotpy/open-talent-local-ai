#!/usr/bin/env python3
"""
Convert Hugging Face LoRA adapters to Ollama-compatible format.

This script converts your fine-tuned LoRA adapters to GGUF format
that Ollama can use with the base Granite model.

Usage:
    python3 convert_lora_to_ollama.py --lora asifdotpy/vetta-granite-2b-lora-v3 --output ./lora_adapters
"""

import argparse
import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if required tools are available."""
    try:
        import torch

        print("✅ torch available")
    except ImportError:
        print("❌ torch not installed - needed for conversion")
        print("   Install: pip install torch --index-url https://download.pytorch.org/whl/cpu")
        return False

    try:
        from transformers import AutoModelForCausalLM

        print("✅ transformers available")
    except ImportError:
        print("❌ transformers not installed")
        print("   Install: pip install transformers")
        return False

    try:
        from peft import PeftModel

        print("✅ peft available")
    except ImportError:
        print("❌ peft not installed")
        print("   Install: pip install peft")
        return False

    return True


def convert_lora_to_gguf(lora_repo: str, base_model: str, output_dir: str):
    """
    Convert LoRA adapters to GGUF format.

    Note: This is a simplified version. For production, you'd use:
    - llama.cpp's convert.py script
    - Ollama's model creation tools
    """
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"📥 Loading base model: {base_model}")
    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="cpu",  # CPU only for low-spec hardware
        trust_remote_code=True,
    )

    print(f"📥 Loading LoRA adapters: {lora_repo}")
    model = PeftModel.from_pretrained(base, lora_repo)

    print("🔄 Merging LoRA into base model...")
    merged_model = model.merge_and_unload()

    print(f"💾 Saving to: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    merged_model.save_pretrained(output_dir)

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.save_pretrained(output_dir)

    print("✅ Conversion complete!")
    print("\n📋 Next steps:")
    print("1. Use llama.cpp to convert to GGUF:")
    print(f"   python3 convert.py {output_dir} --outtype q4_0")
    print("2. Create Ollama Modelfile")
    print("3. Import to Ollama: ollama create my-model -f Modelfile")


def create_ollama_modelfile(base_model: str, adapter_path: str, persona: str, output_path: str):
    """Create an Ollama Modelfile for a specific persona."""

    modelfile_content = f"""# Modelfile for {persona} interviewer persona
FROM {base_model}

# Load LoRA adapter
ADAPTER {adapter_path}

# System prompt for {persona}
SYSTEM You are a {persona} interviewer for OpenTalent platform. You conduct professional interviews with expertise in {persona} topics. Be concise, clear, and focused on assessing candidate skills.

# Parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_predict 2048
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"

# Template
TEMPLATE \"\"\"{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
\"\"\"
"""

    with open(output_path, "w") as f:
        f.write(modelfile_content)

    print(f"✅ Created Modelfile: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert LoRA adapters to Ollama format")
    parser.add_argument(
        "--lora", default="asifdotpy/vetta-granite-2b-lora-v3", help="LoRA repository"
    )
    parser.add_argument("--base", default="ibm-granite/granite-3.0-2b-instruct", help="Base model")
    parser.add_argument("--output", default="./lora_adapters", help="Output directory")
    parser.add_argument(
        "--skip-convert", action="store_true", help="Skip conversion, just create Modelfiles"
    )

    args = parser.parse_args()

    print("🚀 Ollama LoRA Adapter Setup")
    print("=" * 50)

    if not args.skip_convert:
        if not check_dependencies():
            print("\n⚠️  Missing dependencies. Install them first.")
            sys.exit(1)

        convert_lora_to_gguf(args.lora, args.base, args.output)

    # Create example Modelfiles for different personas
    personas = {
        "technical": "Python, system design, algorithms",
        "behavioral": "team dynamics, leadership, communication",
        "creative": "problem-solving, innovation, design thinking",
    }

    print("\n📝 Creating Modelfiles for different personas...")
    modelfiles_dir = Path("./ollama_modelfiles")
    modelfiles_dir.mkdir(exist_ok=True)

    for persona, topics in personas.items():
        modelfile_path = modelfiles_dir / f"{persona}_interviewer.Modelfile"
        create_ollama_modelfile(
            base_model="granite3.0:2b",
            adapter_path="./lora_adapters/adapter.gguf",  # Placeholder
            persona=f"{persona} ({topics})",
            output_path=str(modelfile_path),
        )

    print("\n🎉 Setup complete!")
    print("\n📋 Usage:")
    print("1. Create models in Ollama:")
    print(
        "   ollama create technical_interviewer -f ollama_modelfiles/technical_interviewer.Modelfile"
    )
    print(
        "   ollama create behavioral_interviewer -f ollama_modelfiles/behavioral_interviewer.Modelfile"
    )
    print("2. Use in your service:")
    print("   LLM_MODEL=technical_interviewer")
    print("3. Switch personas by changing LLM_MODEL")


if __name__ == "__main__":
    main()
