# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  Check Drive Status Script                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

"""
WHEN TO RUN: After mounting Google Drive (CELL 1) and before training/saving.

PURPOSE: Check if models are already saved on Google Drive to avoid re-saving.
This prevents wasting time retraining or re-saving models that already exist.

USAGE IN NOTEBOOK:
1. Mount Drive: Run CELL 1
2. Check status: !python check_drive_status.py
3. If models exist: Skip to upload (CELL 8)
4. If no models: Continue with training (CELL 5) then saving (CELL 7)
"""

import os


def check_drive_status():
    project_dir = '/content/drive/MyDrive/open-talent-vetta'
    checkpoints_dir = f'{project_dir}/checkpoints'
    models_dir = f'{project_dir}/models'

    print("🔍 Checking Google Drive status...")
    print(f"📁 Project: {project_dir}")
    print("   This shows what's already saved to avoid retraining!\n")

    # Check checkpoints
    if os.path.exists(checkpoints_dir):
        checkpoints = [d for d in os.listdir(checkpoints_dir) if d.startswith('checkpoint-')]
        if checkpoints:
            latest = max(checkpoints, key=lambda x: int(x.split('-')[1]))
            print(f"✅ Checkpoints: {len(checkpoints)} found, latest: {latest}")
            print("   💡 You can RESUME training from here if needed!")
        else:
            print("📂 Checkpoints directory exists but no checkpoints found")
    else:
        print("❌ No checkpoints directory found")

    # Check saved models
    models_found = []
    for model_type in ['lora', 'merged', 'gguf']:
        model_path = f'{models_dir}/{model_type}'
        if os.path.exists(model_path) and os.listdir(model_path):
            # Calculate size
            size = sum(os.path.getsize(os.path.join(model_path, f))
                      for f in os.listdir(model_path)
                      if os.path.isfile(os.path.join(model_path, f)))
            size_gb = size / (1024**3)
            print(f"✅ {model_type.upper()}: {size_gb:.2f} GB saved")
            models_found.append(model_type)
        else:
            print(f"❌ {model_type.upper()}: Not found")

    print("\n" + "="*60)
    if models_found:
        print("🎉 MODELS ALREADY SAVED! You can skip training/saving!")
        print(f"Saved models: {', '.join(models_found).upper()}")
        print("\n🚀 NEXT: Run upload cell (CELL 8) to publish to Hugging Face")
        print("   No need to train or save again!")
    else:
        print("📝 No saved models found.")
        print("\n🚀 NEXT: Run training (CELL 5) then save models (CELL 7)")
        print("   Models will be saved to Drive automatically")

    if os.path.exists(checkpoints_dir) and checkpoints:
        print("💾 Training checkpoints available - can resume training if interrupted.")

    print("\n" + "="*60)
    print("💡 DRIVE PERSISTENCE: Even if Colab crashes, your progress is safe!")
    print("   Run this script anytime to check status.")

if __name__ == "__main__":
    check_drive_status()</content>
<parameter name="filePath">/home/asif1/open-talent-platform/notebook_chunks/check_drive_status.py
