# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL: Merge LoRA Adapters with Base Model (Colab Version)             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Install required packages (run this first if not installed)
# !pip install torch transformers unsloth huggingface_hub

import os

from google.colab import userdata
from huggingface_hub import HfApi, login
from unsloth import FastLanguageModel

# 1. CONFIGURATION
HF_USERNAME = "asifdotpy"
BASE_MODEL = "ibm-granite/granite-3.0-2b-instruct"
LORA_REPO = f"{HF_USERNAME}/vetta-granite-2b-lora-v3"
MERGED_REPO = f"{HF_USERNAME}/vetta-granite-2b-v3"
VERSION = "v3"

# Drive paths (persistent storage)
models_dir = "/content/drive/MyDrive/open-talent-vetta/models"
lora_dir = f"{models_dir}/lora"
merged_dir = f"{models_dir}/merged"

print("🔄 Starting LoRA merge process in Colab...")
print(f"📂 Models directory: {models_dir}")
print(f"📂 LoRA directory: {lora_dir}")
print(f"📂 Merged directory: {merged_dir}")

# 2. SAFETY CHECKS
if not os.path.exists(lora_dir):
    raise FileNotFoundError(f"❌ LoRA directory not found: {lora_dir}")

# Check available RAM (Colab has ~12GB, merging needs ~8GB+)
import psutil

ram_gb = psutil.virtual_memory().total / (1024**3)
print(f"💾 Available RAM: {ram_gb:.1f}GB")

if ram_gb < 10:
    print("⚠️  Warning: Low RAM detected. Merging may fail.")
    print("   Consider using a Colab Pro instance or merging locally.")

# 3. LOGIN TO HUGGING FACE
try:
    hf_token = userdata.get("HF_TOKEN")
    login(token=hf_token)
    api = HfApi(token=hf_token)
    print("✅ Logged in to Hugging Face")
except Exception as e:
    print(f"❌ HF login failed: {e}")
    raise

# 4. LOAD BASE MODEL (Full precision for merging)
print(f"📥 Loading base model: {BASE_MODEL}")
try:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=2048,
        load_in_4bit=False,  # Full precision for merging
        device_map="auto",  # Use GPU
    )
    print("✅ Base model loaded")
except Exception as e:
    print(f"❌ Failed to load base model: {e}")
    raise

# 5. APPLY LORA ADAPTERS
print(f"📥 Applying LoRA adapters from: {LORA_REPO}")
try:
    model = FastLanguageModel.get_peft_model(
        model,
        lora_path=LORA_REPO,  # Load from HF
        r=16,
        lora_alpha=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )
    print("✅ LoRA adapters applied")
except Exception as e:
    print(f"❌ Failed to apply LoRA: {e}")
    raise

# 6. MERGE WEIGHTS
print("🔀 Merging LoRA weights into base model...")
try:
    model = model.merge_and_unload()
    print("✅ Weights merged successfully")
except Exception as e:
    print(f"❌ Merge failed: {e}")
    raise

# 7. SAVE MERGED MODEL TO DRIVE
print(f"💾 Saving merged model to Drive: {merged_dir}")
os.makedirs(merged_dir, exist_ok=True)

try:
    model.save_pretrained(
        merged_dir, safe_serialization=True
    )  # Use safe serialization to reduce size
    tokenizer.save_pretrained(merged_dir)
    print("✅ Merged model saved to Drive")

    # Check file sizes
    total_size = sum(
        os.path.getsize(os.path.join(merged_dir, f))
        for f in os.listdir(merged_dir)
        if os.path.isfile(os.path.join(merged_dir, f))
    )
    print(f"📏 Model size: {total_size / (1024**3):.2f} GB")

except Exception as e:
    print(f"❌ Failed to save merged model: {e}")
    print("💡 Alternative: Save to Colab local storage and download manually")
    print("   Run: model.save_pretrained('./merged_model', safe_serialization=True)")
    print("   Then download the folder from Colab files panel")
    raise

# 8. UPLOAD TO HUGGING FACE
print(f"📤 Uploading merged model to: {MERGED_REPO}")
try:
    api.create_repo(MERGED_REPO, exist_ok=True, private=False)

    api.upload_folder(
        folder_path=merged_dir,
        repo_id=MERGED_REPO,
        repo_type="model",
        commit_message=f"Upload merged Vetta Granite fine-tuned model {VERSION} (16-bit)",
    )
    print("✅ Merged model uploaded to Hugging Face")
    print(f"👉 https://huggingface.co/{MERGED_REPO}")

except Exception as e:
    print(f"❌ Upload failed: {e}")
    raise

# 9. CREATE MODEL CARD
print("📝 Creating model card...")
model_card = f"""---
language: en
tags:
- granite
- fine-tuned
- interview
- ai-interviewer
- vetta
- merged
license: apache-2.0
---

# Vetta Granite Merged Model {VERSION}

This repository contains the full merged Vetta AI interviewer model, fine-tuned on Granite 3.0 2B Instruct with LoRA weights integrated.

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    "asifdotpy/vetta-granite-2b-{VERSION}",
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("asifdotpy/vetta-granite-2b-{VERSION}")

# Generate
inputs = tokenizer("Begin a technical interview...", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=256, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Training Details
- Base Model: ibm-granite/granite-3.0-2b-instruct
- Training Method: LoRA fine-tuning with merged weights
- Dataset: Custom interview conversation dataset
- Training Steps: 2250
- Final Loss: 0.1124
- Precision: 16-bit

## Intended Use
This model is designed to conduct professional AI-powered interviews, providing empathetic and technically accurate responses.
"""

try:
    api.upload_file(
        path_or_fileobj=model_card.encode(),
        path_in_repo="README.md",
        repo_id=MERGED_REPO,
        repo_type="model",
        commit_message="Add model card and usage instructions",
    )
    print("✅ Model card uploaded")
except Exception as e:
    print(f"❌ Model card upload failed: {e}")

print("\n" + "=" * 60)
print("🎉 MERGE COMPLETE!")
print("=" * 60)
print(f"Merged Model: https://huggingface.co/{MERGED_REPO}")
print(f"Local Drive: {merged_dir}")
print("\nNext: Run the GGUF conversion cell to create quantized model for Ollama.")
