
import os
import subprocess
from pathlib import Path
from loguru import logger
from typing import Optional

class PiperTTSService:
    """
    Piper TTS Service - Local, Fast, High-Quality Text-to-Speech
    """

    def __init__(self, piper_path: str, model_path: str):
        """
        Initialize Piper TTS

        Args:
            piper_path: Path to piper executable
            model_path: Path to .onnx voice model file
        """
        self.piper_path = piper_path
        self.model_path = model_path

        logger.info(f"Initializing Piper TTS")
        logger.info(f"  Piper path: {self.piper_path}")
        logger.info(f"  Model path: {self.model_path}")

    def check_installation(self) -> bool:
        """Check if Piper is installed and model is available"""
        try:
            # Check if piper executable exists
            result = subprocess.run(
                [self.piper_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.error(f"✗ Piper failed: {result.stderr}")
                return False

            logger.info(f"✓ Piper version: {result.stdout.strip()}")

            # Check if model exists
            if not os.path.exists(self.model_path):
                logger.error(f"✗ Model not found: {self.model_path}")
                return False

            # Check for .json config
            json_path = f"{self.model_path}.json"
            if not os.path.exists(json_path):
                logger.error(f"✗ Model config not found: {json_path}")
                return False

            logger.info(f"✓ Model found: {self.model_path}")
            return True

        except FileNotFoundError:
            logger.error(f"✗ Piper executable not found at: {self.piper_path}")
            return False
        except Exception as e:
            logger.error(f"✗ Error checking Piper: {e}")
            return False

    def synthesize(self, text: str, output_file: str = "tts_output.wav") -> Optional[str]:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize
            output_file: Output WAV file path

        Returns:
            Path to generated audio file or None if failed
        """
        try:
            logger.info(f"Synthesizing speech: '{text[:50]}...'")

            # Run Piper TTS
            process = subprocess.Popen(
                [
                    self.piper_path,
                    "--model", self.model_path,
                    "--output_file", output_file
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send text to Piper
            stdout, stderr = process.communicate(input=text, timeout=30)

            if process.returncode != 0:
                logger.error(f"✗ Piper failed: {stderr}")
                return None

            if not os.path.exists(output_file):
                logger.error(f"✗ Output file not created: {output_file}")
                return None

            logger.info(f"✓ Speech synthesized: {output_file}")
            return output_file

        except subprocess.TimeoutExpired:
            logger.error("✗ Piper timeout")
            process.kill()
            return None
        except Exception as e:
            logger.error(f"✗ TTS synthesis failed: {e}")
            return None
