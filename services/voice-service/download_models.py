#!/usr/bin/env python3
"""Model Download Script for Voice Service
Downloads Vosk, Piper, and Silero models with progress tracking.
"""

import hashlib
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

# Progress bar support
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Install tqdm for progress bars: pip install tqdm")


class ModelDownloader:
    """Download and verify speech processing models."""

    # Model URLs and checksums
    MODELS = {
        "vosk": {
            "name": "vosk-model-small-en-us-0.15",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "size": "40 MB",
            "checksum": None,  # Optional: add MD5 checksum if available
            "type": "zip"
        },
        "piper_lessac": {
            "name": "en_US-lessac-medium",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
            "size": "45 MB",
            "checksum": None,
            "type": "file"
        },
        "piper_amy": {
            "name": "en_US-amy-medium",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json",
            "size": "43 MB",
            "checksum": None,
            "type": "file"
        },
        "silero_vad": {
            "name": "silero_vad",
            "url": "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx",
            "size": "2 MB",
            "checksum": None,
            "type": "file"
        }
    }

    def __init__(self, models_dir: str = "models"):
        """Initialize downloader with target directory."""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def download_file(self, url: str, output_path: Path, desc: str = "Downloading") -> bool:
        """Download file with progress bar.

        Args:
            url: Download URL
            output_path: Local file path
            desc: Progress bar description

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n{desc}: {url}")
            print(f"Saving to: {output_path}")

            # Get file size
            with urllib.request.urlopen(url) as response:
                file_size = int(response.headers.get('Content-Length', 0))

            # Download with progress bar
            if TQDM_AVAILABLE and file_size > 0:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=desc) as pbar:
                    def reporthook(blocknum, blocksize, totalsize):
                        pbar.update(blocksize)

                    urllib.request.urlretrieve(url, output_path, reporthook=reporthook)
            else:
                urllib.request.urlretrieve(url, output_path)

            print(f"✓ Downloaded: {output_path.name}")
            return True

        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False

    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file SHA-256 checksum."""
        if not expected_checksum:
            return True  # Skip if no checksum provided

        print(f"Verifying checksum for: {file_path.name}")

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        actual_checksum = sha256_hash.hexdigest()

        if actual_checksum == expected_checksum:
            print("✓ Checksum verified")
            return True
        else:
            print("✗ Checksum mismatch!")
            print(f"  Expected: {expected_checksum}")
            print(f"  Actual:   {actual_checksum}")
            return False

    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract ZIP or TAR archive with security checks."""
        try:
            print(f"Extracting: {archive_path.name}")

            def is_within_directory(directory: Path, target: Path) -> bool:
                abs_directory = directory.resolve()
                abs_target = target.resolve()
                return abs_target.is_relative_to(abs_directory)

            if archive_path.suffix == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    # Security check: Validate and extract all members individually
                    for member in zip_ref.namelist():
                        member_path = extract_to / member
                        if not is_within_directory(extract_to, member_path):
                            raise Exception(f"Unsafe ZIP member detected: {member}")
                        zip_ref.extract(member, extract_to)
            elif archive_path.suffix in [".tar", ".gz", ".tgz"]:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    # Security check: Validate and extract all members individually
                    for member in tar_ref.getmembers():
                        member_path = extract_to / member.name
                        if not is_within_directory(extract_to, member_path):
                            raise Exception(f"Unsafe TAR member detected: {member.name}")
                        tar_ref.extract(member, extract_to)
            else:
                print(f"✗ Unknown archive format: {archive_path.suffix}")
                return False

            print(f"✓ Extracted to: {extract_to}")
            return True

        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            return False

    def download_vosk_model(self) -> bool:
        """Download Vosk speech-to-text model."""
        model_info = self.MODELS["vosk"]
        model_name = model_info["name"]

        print(f"\n{'='*60}")
        print(f"Downloading Vosk STT Model: {model_name}")
        print(f"Size: {model_info['size']}")
        print(f"{'='*60}")

        # Check if already exists
        model_dir = self.models_dir / model_name
        if model_dir.exists():
            print(f"✓ Model already exists: {model_dir}")
            return True

        # Download archive
        archive_path = self.models_dir / f"{model_name}.zip"
        if not self.download_file(model_info["url"], archive_path, f"Vosk Model ({model_info['size']})"):
            return False

        # Verify checksum if available
        if model_info["checksum"] and not self.verify_checksum(archive_path, model_info["checksum"]):
            archive_path.unlink()
            return False

        # Extract archive
        if not self.extract_archive(archive_path, self.models_dir):
            return False

        # Cleanup archive
        archive_path.unlink()
        print(f"✓ Vosk model ready: {model_dir}")

        return True

    def download_piper_voice(self, voice_key: str = "piper_lessac") -> bool:
        """Download Piper TTS voice model."""
        model_info = self.MODELS[voice_key]
        model_name = model_info["name"]

        print(f"\n{'='*60}")
        print(f"Downloading Piper TTS Voice: {model_name}")
        print(f"Size: {model_info['size']}")
        print(f"{'='*60}")

        # Download ONNX model
        model_path = self.models_dir / f"{model_name}.onnx"
        if model_path.exists():
            print(f"✓ Model already exists: {model_path}")
        elif not self.download_file(model_info["url"], model_path, f"Piper Voice ({model_info['size']})"):
            return False

        # Download config JSON
        config_path = self.models_dir / f"{model_name}.onnx.json"
        if config_path.exists():
            print(f"✓ Config already exists: {config_path}")
        elif not self.download_file(model_info["config_url"], config_path, "Piper Config"):
            return False

        print(f"✓ Piper voice ready: {model_name}")
        return True

    def download_silero_vad(self) -> bool:
        """Download Silero VAD model."""
        model_info = self.MODELS["silero_vad"]

        print(f"\n{'='*60}")
        print("Downloading Silero VAD Model")
        print(f"Size: {model_info['size']}")
        print(f"{'='*60}")

        # Download ONNX model
        model_path = self.models_dir / "silero_vad.onnx"
        if model_path.exists():
            print(f"✓ Model already exists: {model_path}")
            return True

        if not self.download_file(model_info["url"], model_path, f"Silero VAD ({model_info['size']})"):
            return False

        print(f"✓ Silero VAD ready: {model_path}")
        return True

    def download_all(self) -> bool:
        """Download all required models."""
        print("\n" + "="*60)
        print("Voice Service Model Downloader")
        print("="*60)
        print(f"Models directory: {self.models_dir.absolute()}")
        print("\nThis will download:")
        print("  1. Vosk STT model (40 MB - small model)")
        print("  2. Piper TTS voices (45 MB each)")
        print("  3. Silero VAD model (2 MB)")
        print("\nTotal download: ~135 MB")
        print("="*60)

        # Confirm download
        response = input("\nProceed with download? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("Download cancelled.")
            return False

        success = True

        # Download Vosk
        if not self.download_vosk_model():
            success = False

        # Download Piper voices
        for voice_key in ["piper_lessac", "piper_amy"]:
            if not self.download_piper_voice(voice_key):
                success = False

        # Download Silero VAD
        if not self.download_silero_vad():
            success = False

        print("\n" + "="*60)
        if success:
            print("✓ All models downloaded successfully!")
            print(f"\nModels location: {self.models_dir.absolute()}")
            print("\nYou can now start the voice service:")
            print("  python main.py")
        else:
            print("✗ Some downloads failed. Please check errors above.")
        print("="*60)

        return success


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download speech processing models for Voice Service"
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="Directory to store models (default: models)"
    )
    parser.add_argument(
        "--vosk-only",
        action="store_true",
        help="Download only Vosk STT model (40MB small model)"
    )
    parser.add_argument(
        "--piper-only",
        action="store_true",
        help="Download only Piper TTS voices"
    )
    parser.add_argument(
        "--vad-only",
        action="store_true",
        help="Download only Silero VAD model"
    )

    args = parser.parse_args()

    downloader = ModelDownloader(models_dir=args.models_dir)

    if args.vosk_only:
        success = downloader.download_vosk_model()
    elif args.piper_only:
        success = (
            downloader.download_piper_voice("piper_lessac") and
            downloader.download_piper_voice("piper_amy")
        )
    elif args.vad_only:
        success = downloader.download_silero_vad()
    else:
        success = downloader.download_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
