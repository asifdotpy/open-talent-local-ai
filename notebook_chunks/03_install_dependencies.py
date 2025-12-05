# ╗═════════════════════════════════════════════════════════╗
# ║  CELL 1: Install Dependencies                                             ║
# ╚══════════════════════════════════════════════════════════╝

%%capture
print("🚀 Starting dependency installation...")

# Conditional package installation - only install if not already correct
import subprocess
import sys
from packaging import version

def check_package_version(package, version_spec):
    """Check if installed package version satisfies the version spec."""
    try:
        result = subprocess.run([sys.executable, '-c', f'import {package}; print({package}.__version__)'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            installed_version = result.stdout.strip()
            # Parse version spec (e.g., '<0.9.0')
            if version_spec.startswith('<'):
                max_version = version_spec[1:]
                return version.parse(installed_version) < version.parse(max_version)
            elif version_spec.startswith('>='):
                min_version = version_spec[2:]
                return version.parse(installed_version) >= version.parse(min_version)
            else:
                return installed_version == version_spec
    except Exception as e:
        print(f"Version check failed: {e}")
        pass
    return False

# Check if key packages are already installed correctly
packages_ok = (
    check_package_version('trl', '<0.9.0') and
    check_package_version('unsloth', '>=2025.11.4')  # Check for recent unsloth version
)

if not packages_ok:
    print("📦 Installing required packages...")
    # Install trl first to avoid version conflicts
    !pip install --no-deps "trl<0.9.0"
    # Then install the rest
    !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    !pip install --no-deps "xformers<0.0.27" peft accelerate bitsandbytes
    print("✅ Dependencies installed - please restart runtime if prompted")
else:
    print("✅ Dependencies already installed correctly - skipping installation")

print("✅ Dependencies ready")