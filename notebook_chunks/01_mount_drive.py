# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 1: Mount Google Drive                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

import os

from google.colab import drive

# Mount Google Drive
print("🔗 Mounting Google Drive...")
drive.mount("/content/drive")

# Create project directory structure on Drive
project_dir = "/content/drive/MyDrive/open-talent-vetta"
checkpoints_dir = f"{project_dir}/checkpoints"
models_dir = f"{project_dir}/models"

# Create directories if they don't exist
os.makedirs(checkpoints_dir, exist_ok=True)
os.makedirs(models_dir, exist_ok=True)
os.makedirs(f"{models_dir}/lora", exist_ok=True)
os.makedirs(f"{models_dir}/merged", exist_ok=True)
os.makedirs(f"{models_dir}/gguf", exist_ok=True)

print("✅ Google Drive mounted successfully!")
print(f"📁 Project directory: {project_dir}")
print(f"📁 Checkpoints: {checkpoints_dir}")
print(f"📁 Models: {models_dir}")

# Verify Drive is accessible
try:
    test_file = f"{project_dir}/test_write.txt"
    with open(test_file, "w") as f:
        f.write("Drive is accessible!")
    os.remove(test_file)
    print("✅ Drive write test passed - persistent storage ready!")
except Exception as e:
    print(f"⚠️  Drive write test failed: {e}")
    print("   You may need to remount Drive or check permissions")
