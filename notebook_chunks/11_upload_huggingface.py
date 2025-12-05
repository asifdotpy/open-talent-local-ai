# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 8: Upload to Hugging Face Hub                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

import os
from huggingface_hub import login, HfApi
from google.colab import userdata
from unsloth import FastLanguageModel

# 1. Retrieve HuggingFace token securely
try:
    token = userdata.get('HF_TOKEN')
    login(token=token)
    api = HfApi(token=token)
except Exception:
    print("⚠️ Error: Could not log in. Make sure 'HF_TOKEN' is set in Colab Secrets.")
    raise

# 2. CONFIGURATION
HF_USERNAME = "asifdotpy"
BASE_MODEL_NAME = "vetta-granite-2b"
VERSION = "v3"  # Updated version for new training
REPO_ID_MERGED = f"{HF_USERNAME}/{BASE_MODEL_NAME}-{VERSION}"
REPO_ID_LORA = f"{HF_USERNAME}/{BASE_MODEL_NAME}-lora-{VERSION}"

# Directories (from Drive - persistent storage)
output_dir = "/content/drive/MyDrive/talent-ai-vetta/checkpoints"  # Checkpoints
models_dir = "/content/drive/MyDrive/talent-ai-vetta/models"      # Saved models
lora_dir = f"{models_dir}/lora"
merged_dir = f"{models_dir}/merged"
gguf_dir = f"{models_dir}/gguf"

# 3. SAFETY CHECKS
required_dirs = [lora_dir]  # LoRA is always required
optional_dirs = [merged_dir, gguf_dir]  # Merged and GGUF are optional in Colab

for dir_path in required_dirs:
    if not os.path.exists(dir_path):
        raise FileNotFoundError(
            f"❌ CRITICAL ERROR: The directory {dir_path} was not found.\n"
            "Make sure you ran the save model cell (CELL 7) successfully.\n"
            "If your runtime disconnected, you may need to retrain and save again."
        )

# Check optional directories
def has_files(dir_path):
    if not os.path.exists(dir_path):
        return False
    return len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]) > 0

merged_available = has_files(merged_dir)
gguf_available = has_files(gguf_dir)

if merged_available and gguf_available:
    print("✅ All model directories found with files. Ready for upload.")
elif merged_available:
    print("✅ LoRA and merged models found with files. GGUF will be uploaded later from local conversion.")
    print("   ℹ️  To convert GGUF locally: python convert_to_gguf.py")
elif gguf_available:
    print("⚠️  Only LoRA and GGUF found with files. Merged model skipped in Colab - merge locally.")
    print("   ℹ️  To merge locally: python merge_lora.py")
else:
    print("⚠️  Only LoRA found with files. Merged and GGUF skipped in Colab - process locally.")
    print("   ℹ️  To merge: python merge_lora.py")
    print("   ℹ️  To convert GGUF: python convert_to_gguf.py")

# 4. UPLOAD LORA ADAPTERS (Small, for fine-tuning)
print(f"\n📤 Uploading LoRA adapters to: {REPO_ID_LORA}")
try:
    api.create_repo(REPO_ID_LORA, exist_ok=True, private=False)

    # Upload LoRA files
    api.upload_folder(
        folder_path=lora_dir,
        repo_id=REPO_ID_LORA,
        repo_type="model",
        commit_message="Upload LoRA adapters for Vetta Granite fine-tuned model"
    )

    print(f"✅ LoRA adapters uploaded successfully!")
    print(f"👉 https://huggingface.co/{REPO_ID_LORA}")

except Exception as e:
    print(f"❌ Error uploading LoRA: {e}")

# 5. UPLOAD MERGED MODEL (Full model for inference) - Only if available
if merged_available:
    print(f"\n📤 Uploading merged model to: {REPO_ID_MERGED}")
    try:
        api.create_repo(REPO_ID_MERGED, exist_ok=True, private=False)

        # Upload merged model files
        api.upload_folder(
            folder_path=merged_dir,
            repo_id=REPO_ID_MERGED,
            repo_type="model",
            commit_message="Upload merged Vetta Granite fine-tuned model (16-bit)"
        )

        print(f"✅ Merged model uploaded successfully!")
        print(f"👉 https://huggingface.co/{REPO_ID_MERGED}")

    except Exception as e:
        print(f"❌ Error uploading merged model: {e}")
else:
    print("\n⏭️  Skipping merged model upload (not available in Colab)")
    print("   ℹ️  Merge LoRA locally and upload separately")

# 6. UPLOAD GGUF (For Ollama/vLLM deployment) - Only if available
if gguf_available:
    GGUF_REPO_ID = f"{HF_USERNAME}/{BASE_MODEL_NAME}-gguf-{VERSION}"
    print(f"\n📤 Uploading GGUF to: {GGUF_REPO_ID}")
    try:
        api.create_repo(GGUF_REPO_ID, exist_ok=True, private=False)

        # Upload GGUF files
        api.upload_folder(
            folder_path=gguf_dir,
            repo_id=GGUF_REPO_ID,
            repo_type="model",
            commit_message="Upload GGUF quantized model for Vetta Granite (Ollama compatible)"
        )

        print(f"✅ GGUF model uploaded successfully!")
        print(f"👉 https://huggingface.co/{GGUF_REPO_ID}")

    except Exception as e:
        print(f"❌ Error uploading GGUF: {e}")
else:
    print("\n⏭️  Skipping GGUF upload (not available in Colab)")
    print("   ℹ️  Convert GGUF locally and upload separately")

# 7. CREATE MODEL CARDS
print("\n📝 Creating model cards...")

# LoRA Model Card
lora_card = f"""---
language: en
tags:
- granite
- lora
- fine-tuned
- interview
- ai-interviewer
- vetta
license: apache-2.0
---

# Vetta Granite LoRA Adapters {VERSION}

This repository contains the LoRA adapters for the Vetta AI interviewer model, fine-tuned on Granite 3.0 2B Instruct.

## Usage

```python
from unsloth import FastLanguageModel
from transformers import AutoTokenizer

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="ibm-granite/granite-3.0-2b-instruct",
    max_seq_length=2048,
    load_in_4bit=True,
)

# Load LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    lora_path="asifdotpy/vetta-granite-2b-lora-{VERSION}",
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

# Enable inference
FastLanguageModel.for_inference(model)

# Generate
inputs = tokenizer("Begin a technical interview...", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=256)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Training Details
- Base Model: ibm-granite/granite-3.0-2b-instruct
- Training Method: LoRA fine-tuning
- Dataset: Custom interview conversation dataset
- Training Steps: 450
- Final Loss: 0.2422

## Intended Use
This model is designed to conduct professional AI-powered interviews, providing empathetic and technically accurate responses.
"""

# Merged Model Card
merged_card = f"""---
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
- Training Steps: 450
- Final Loss: 0.2422
- Precision: 16-bit

## Intended Use
This model is designed to conduct professional AI-powered interviews, providing empathetic and technically accurate responses.
"""

# GGUF Model Card
gguf_card = f"""---
language: en
tags:
- granite
- gguf
- quantized
- interview
- ai-interviewer
- vetta
- ollama
license: apache-2.0
---

# Vetta Granite GGUF Model {VERSION}

This repository contains the quantized GGUF version of the Vetta AI interviewer model for efficient inference with Ollama or vLLM.

## Usage with Ollama

1. Download the GGUF file
2. Create Modelfile:
```
FROM ./vetta-granite-2b-gguf-{VERSION}.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM "You are Vetta, a professional AI interviewer conducting technical interviews."
```

3. Create model: `ollama create vetta-granite -f Modelfile`
4. Run: `ollama run vetta-granite`

## Training Details
- Base Model: ibm-granite/granite-3.0-2b-instruct
- Training Method: LoRA fine-tuning
- Quantization: Q4_K_M
- Dataset: Custom interview conversation dataset
- Training Steps: 450
- Final Loss: 0.2422

## Intended Use
This model is designed to conduct professional AI-powered interviews, providing empathetic and technically accurate responses.
"""

# Upload model cards
try:
    api.upload_file(
        path_or_fileobj=lora_card.encode(),
        path_in_repo="README.md",
        repo_id=REPO_ID_LORA,
        repo_type="model",
        commit_message="Add model card and usage instructions"
    )
    print("✅ LoRA model card uploaded")

    if merged_available:
        api.upload_file(
            path_or_fileobj=merged_card.encode(),
            path_in_repo="README.md",
            repo_id=REPO_ID_MERGED,
            repo_type="model",
            commit_message="Add model card and usage instructions"
        )
        print("✅ Merged model card uploaded")
    else:
        print("⏭️  Skipping merged model card (merged model not available)")

    if gguf_available:
        api.upload_file(
            path_or_fileobj=gguf_card.encode(),
            path_in_repo="README.md",
            repo_id=GGUF_REPO_ID,
            repo_type="model",
            commit_message="Add model card and usage instructions"
        )
        print("✅ GGUF model card uploaded")
    else:
        print("⏭️  Skipping GGUF model card (GGUF not available)")

except Exception as e:
    print(f"❌ Error uploading model cards: {e}")

print("\n" + "="*60)
print("🎉 UPLOAD COMPLETE!")
print("="*60)
print(f"LoRA Adapters: https://huggingface.co/{REPO_ID_LORA}")
if merged_available:
    print(f"Merged Model:  https://huggingface.co/{REPO_ID_MERGED}")
else:
    print("Merged Model:  Not uploaded (merge locally)")
if gguf_available:
    print(f"GGUF Model:    https://huggingface.co/{GGUF_REPO_ID}")
else:
    print("GGUF Model:    Not uploaded (convert locally)")
print("\nAll available models are now publicly available with proper documentation!")
if not merged_available or not gguf_available:
    print("\n📋 To complete the model suite:")
    if not merged_available:
        print("1. Merge LoRA: python merge_lora.py")
        print("2. Upload merged to: asifdotpy/vetta-granite-2b-v3")
    if not gguf_available:
        print("3. Convert GGUF: python convert_to_gguf.py")
        print("4. Upload GGUF to: asifdotpy/vetta-granite-2b-gguf-v3")
print("\nYou can now integrate Vetta into your interview service using LoRA format!")</content>
<parameter name="filePath">/home/asif1/talent-ai-platform/notebook_chunks/11_upload_huggingface.py