import os
import shutil
import time  # Import time for delay

source_data_path = "/content/drive/MyDrive/Open Talent/data"
destination_colab_path = "."  # Copy to the current working directory

# First check for existence
if not os.path.exists(source_data_path):
    print(f"❌ Source directory '{source_data_path}' not found on first check.")
    print(
        "It's possible Google Drive momentarily disconnected. Retrying check after a short delay..."
    )
    time.sleep(5)  # Wait for 5 seconds

if os.path.exists(source_data_path):
    print(f"Copying contents from '{source_data_path}' to '{destination_colab_path}'...")

    # Iterate through items and copy them
    for item_name in os.listdir(source_data_path):
        source_item = os.path.join(source_data_path, item_name)
        destination_item = os.path.join(destination_colab_path, item_name)

        if os.path.isfile(source_item):
            shutil.copy2(source_item, destination_item)
        elif os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item, dirs_exist_ok=True)

    print("✅ Contents copied successfully!")
    # Verify contents in the current directory
    print("Contents of current directory (after copy):")
    for item in os.listdir(destination_colab_path):
        if (
            item.startswith("vetta_") or item == "enhanced_vetta_data.py" or item == "README.md"
        ):  # Only show relevant copied files
            print(f"- {item}")
else:
    print(f"❌ Source directory '{source_data_path}' still not found after retry.")
    print(
        "This indicates a persistent issue. Please ensure your Google Drive is correctly mounted and consider restarting the Colab runtime."
    )
