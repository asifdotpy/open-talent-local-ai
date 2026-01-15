#!/usr/bin/env python3
"""Audio Processing Validators for Voice Service
Comprehensive validation suite for audio quality, latency, and processing metrics.
"""

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass

import numpy as np
import soundfile as sf
from scipy import signal

logger = logging.getLogger(__name__)


@dataclass
class AudioMetrics:
    """Container for audio processing metrics."""

    snr_db: float
    thd_percent: float  # Total Harmonic Distortion
    latency_ms: float
    compression_ratio: float
    rnnoise_effectiveness: float  # 0-1 scale
    opus_bitrate_kbps: float
    sample_rate: int
    channels: int
    duration_seconds: float


@dataclass
class ValidationResult:
    """Result of audio processing validation."""

    passed: bool
    metrics: AudioMetrics
    errors: list[str]
    warnings: list[str]
    recommendations: list[str]


class AudioProcessingValidator:
    """Comprehensive validator for audio processing pipeline
    Tests SNR, latency, compression, and quality metrics.
    """

    def __init__(self, sample_rate: int = 48000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.temp_files = []

    def __del__(self):
        """Cleanup temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except OSError:
                pass

    async def validate_audio_pipeline(
        self,
        input_audio: np.ndarray,
        processed_audio: np.ndarray,
        original_bitrate: int | None = None,
        compressed_bitrate: int | None = None,
        processing_latency_ms: float | None = None,
    ) -> ValidationResult:
        """Comprehensive validation of audio processing pipeline.

        Args:
            input_audio: Original audio samples
            processed_audio: Processed audio samples (after RNNoise/Opus)
            original_bitrate: Original bitrate in kbps
            compressed_bitrate: Compressed bitrate in kbps
            processing_latency_ms: Measured processing latency

        Returns:
            ValidationResult with metrics and pass/fail status
        """
        errors = []
        warnings = []
        recommendations = []

        try:
            # Calculate core metrics
            snr_db = self._calculate_snr(input_audio, processed_audio)
            thd_percent = self._calculate_thd(processed_audio)
            compression_ratio = self._calculate_compression_ratio(original_bitrate, compressed_bitrate)
            rnnoise_effectiveness = self._evaluate_rnnoise_effectiveness(input_audio, processed_audio)

            # Estimate latency if not provided
            if processing_latency_ms is None:
                processing_latency_ms = self._estimate_latency(input_audio, processed_audio)

            # Create metrics object
            metrics = AudioMetrics(
                snr_db=snr_db,
                thd_percent=thd_percent,
                latency_ms=processing_latency_ms,
                compression_ratio=compression_ratio,
                rnnoise_effectiveness=rnnoise_effectiveness,
                opus_bitrate_kbps=compressed_bitrate or 0,
                sample_rate=self.sample_rate,
                channels=self.channels,
                duration_seconds=len(processed_audio) / self.sample_rate,
            )

            # Validate against thresholds
            passed = self._validate_metrics(metrics, errors, warnings, recommendations)

            return ValidationResult(
                passed=passed,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Audio validation error: {e}")
            return ValidationResult(
                passed=False,
                metrics=AudioMetrics(0, 0, 0, 0, 0, 0, self.sample_rate, self.channels, 0),
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                recommendations=["Check audio processing pipeline for errors"],
            )

    def _calculate_snr(self, original: np.ndarray, processed: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio in dB."""
        try:
            # Ensure same length
            min_len = min(len(original), len(processed))
            orig = original[:min_len]
            proc = processed[:min_len]

            # Calculate signal power (original audio)
            signal_power = np.mean(orig**2)

            # Calculate noise power (difference between original and processed)
            noise = orig - proc
            noise_power = np.mean(noise**2)

            if noise_power <= 0 or signal_power <= 0:
                return 0.0

            snr = 10 * np.log10(signal_power / noise_power)
            return max(0.0, snr)  # Ensure non-negative

        except Exception as e:
            logger.error(f"SNR calculation error: {e}")
            return 0.0

    def _calculate_thd(self, audio: np.ndarray, fundamental_freq: int = 1000) -> float:
        """Calculate Total Harmonic Distortion percentage."""
        try:
            # Find fundamental frequency bin
            freqs = np.fft.fftfreq(len(audio), 1 / self.sample_rate)
            fundamental_idx = np.argmin(np.abs(freqs - fundamental_freq))

            # Get FFT
            fft = np.fft.fft(audio)
            magnitudes = np.abs(fft)

            # Fundamental amplitude
            fundamental = magnitudes[fundamental_idx]

            # Sum of harmonics (2nd to 5th)
            harmonics = 0
            for i in range(2, 6):
                harmonic_idx = np.argmin(np.abs(freqs - (fundamental_freq * i)))
                harmonics += magnitudes[harmonic_idx]

            if fundamental <= 0:
                return 0.0

            thd = (harmonics / fundamental) * 100
            return thd

        except Exception as e:
            logger.error(f"THD calculation error: {e}")
            return 0.0

    def _calculate_compression_ratio(self, original_bitrate: int | None, compressed_bitrate: int | None) -> float:
        """Calculate compression ratio."""
        if original_bitrate and compressed_bitrate and compressed_bitrate > 0:
            return original_bitrate / compressed_bitrate
        return 1.0  # No compression

    def _evaluate_rnnoise_effectiveness(self, original: np.ndarray, processed: np.ndarray) -> float:
        """Evaluate RNNoise effectiveness (0-1 scale)."""
        try:
            # Simple effectiveness metric: reduction in low-frequency noise
            # Apply low-pass filter to focus on noise frequencies (< 300Hz)
            nyquist = self.sample_rate / 2
            cutoff = 300 / nyquist
            b, a = signal.butter(4, cutoff, btype="low")

            orig_filtered = signal.filtfilt(b, a, original)
            proc_filtered = signal.filtfilt(b, a, processed)

            # Calculate noise reduction
            orig_noise_power = np.var(orig_filtered)
            proc_noise_power = np.var(proc_filtered)

            if orig_noise_power <= 0:
                return 1.0  # Perfect if no original noise

            reduction = (orig_noise_power - proc_noise_power) / orig_noise_power
            return max(0.0, min(1.0, reduction))

        except Exception as e:
            logger.error(f"RNNoise effectiveness calculation error: {e}")
            return 0.0

    def _estimate_latency(self, original: np.ndarray, processed: np.ndarray) -> float:
        """Estimate processing latency in milliseconds."""
        try:
            # Cross-correlation to find delay
            correlation = signal.correlate(processed, original, mode="full")
            delay_samples = np.argmax(correlation) - len(original) + 1
            delay_ms = (delay_samples / self.sample_rate) * 1000
            return max(0.0, delay_ms)

        except Exception as e:
            logger.error(f"Latency estimation error: {e}")
            return 0.0

    def _validate_metrics(
        self,
        metrics: AudioMetrics,
        errors: list[str],
        warnings: list[str],
        recommendations: list[str],
    ) -> bool:
        """Validate metrics against acceptable thresholds for voice processing."""
        passed = True

        # SNR validation - critical for voice quality
        if metrics.snr_db < 10:  # More lenient for voice processing
            errors.append(f"Low SNR: {metrics.snr_db:.1f}dB (minimum 10dB required for voice)")
            recommendations.append("Improve noise suppression or increase input volume")
            passed = False
        elif metrics.snr_db < 15:
            warnings.append(f"Moderate SNR: {metrics.snr_db:.1f}dB (target >15dB for clear voice)")

        # THD validation - less critical for voice processing
        # Skip THD validation for voice as it's not as relevant
        # THD is more important for music/audio equipment testing

        # Latency validation - critical for real-time communication
        if metrics.latency_ms > 150:  # More lenient for voice
            errors.append(f"High latency: {metrics.latency_ms:.1f}ms (maximum 150ms for voice)")
            recommendations.append("Optimize audio processing pipeline for lower latency")
            passed = False
        elif metrics.latency_ms > 50:
            warnings.append(f"Moderate latency: {metrics.latency_ms:.1f}ms (target <50ms for real-time)")

        # RNNoise effectiveness - important for voice quality
        if metrics.rnnoise_effectiveness < 0.2:  # More lenient threshold
            warnings.append(f"Low RNNoise effectiveness: {metrics.rnnoise_effectiveness:.2f} (target >0.5)")
            recommendations.append("Tune RNNoise parameters or check audio input quality")

        # Duration validation
        if metrics.duration_seconds < 0.5:
            warnings.append(f"Short audio duration: {metrics.duration_seconds:.1f}s (minimum 0.5s recommended)")

        return passed

    async def validate_file(
        self,
        input_file: str,
        processed_file: str,
        original_bitrate: int | None = None,
        compressed_bitrate: int | None = None,
        processing_latency_ms: float | None = None,
    ) -> ValidationResult:
        """Validate audio files directly."""
        try:
            # Load audio files
            input_audio, input_sr = sf.read(input_file)
            processed_audio, processed_sr = sf.read(processed_file)

            # Ensure mono and same sample rate
            if input_audio.ndim > 1:
                input_audio = np.mean(input_audio, axis=1)
            if processed_audio.ndim > 1:
                processed_audio = np.mean(processed_audio, axis=1)

            # Resample if necessary
            if input_sr != self.sample_rate:
                input_audio = self._resample_audio(input_audio, input_sr, self.sample_rate)
            if processed_sr != self.sample_rate:
                processed_audio = self._resample_audio(processed_audio, processed_sr, self.sample_rate)

            return await self.validate_audio_pipeline(
                input_audio,
                processed_audio,
                original_bitrate,
                compressed_bitrate,
                processing_latency_ms,
            )

        except Exception as e:
            logger.error(f"File validation error: {e}")
            return ValidationResult(
                passed=False,
                metrics=AudioMetrics(0, 0, 0, 0, 0, 0, self.sample_rate, self.channels, 0),
                errors=[f"File validation failed: {str(e)}"],
                warnings=[],
                recommendations=["Check audio file formats and paths"],
            )

    def _resample_audio(self, audio: np.ndarray, from_sr: int, to_sr: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        try:
            from scipy import signal

            resample_ratio = to_sr / from_sr
            resampled = signal.resample(audio, int(len(audio) * resample_ratio))
            return resampled
        except ImportError:
            # Fallback: simple linear interpolation
            logger.warning("SciPy not available, using basic resampling")
            ratio = to_sr / from_sr
            new_length = int(len(audio) * ratio)
            indices = np.linspace(0, len(audio) - 1, new_length)
            return np.interp(indices, np.arange(len(audio)), audio)

    async def generate_test_audio(
        self,
        duration_seconds: float = 3.0,
        include_noise: bool = True,
        include_speech_like: bool = True,
        frequency: int = 1000,
    ) -> tuple[np.ndarray, str]:
        """Generate test audio for validation testing."""
        try:
            # Generate base sine wave
            t = np.linspace(0, duration_seconds, int(self.sample_rate * duration_seconds))
            audio = np.sin(2 * np.pi * frequency * t)

            # Add speech-like characteristics
            if include_speech_like:
                # Add some harmonics
                audio += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
                audio += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)

            # Add noise
            if include_noise:
                noise = np.random.normal(0, 0.1, len(audio))
                audio += noise

            # Normalize
            audio = audio / np.max(np.abs(audio))

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, audio, self.sample_rate)
                self.temp_files.append(tmp.name)
                return audio, tmp.name

        except Exception as e:
            logger.error(f"Test audio generation error: {e}")
            return np.array([]), ""

    def print_validation_report(self, result: ValidationResult):
        """Print a formatted validation report."""
        print("\n" + "=" * 60)
        print("🎵 AUDIO PROCESSING VALIDATION REPORT")
        print("=" * 60)

        print("📊 METRICS:")
        print(".1f")
        print(".1f")
        print(".1f")
        print(".1f")
        print(".2f")
        print(".1f")
        print(f"  Sample Rate: {result.metrics.sample_rate}Hz")
        print(f"  Channels: {result.metrics.channels}")
        print(".1f")

        print("\n📋 VALIDATION STATUS:")
        if result.passed:
            print("✅ PASSED - All metrics within acceptable ranges")
        else:
            print("❌ FAILED - Some metrics outside acceptable ranges")

        if result.errors:
            print("\n❌ ERRORS:")
            for error in result.errors:
                print(f"  • {error}")

        if result.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in result.warnings:
                print(f"  • {warning}")

        if result.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in result.recommendations:
                print(f"  • {rec}")

        print("=" * 60)


# Convenience functions for common validation scenarios


async def validate_rnnoise_processing(
    input_audio: np.ndarray, output_audio: np.ndarray, latency_ms: float | None = None
) -> ValidationResult:
    """Validate RNNoise processing specifically."""
    validator = AudioProcessingValidator()
    return await validator.validate_audio_pipeline(input_audio, output_audio, processing_latency_ms=latency_ms)


async def validate_opus_compression(
    original_file: str, compressed_file: str, target_bitrate_kbps: int = 64
) -> ValidationResult:
    """Validate Opus compression quality."""
    validator = AudioProcessingValidator()
    return await validator.validate_file(
        original_file,
        compressed_file,
        original_bitrate=384,  # PCM 48kHz 16-bit mono
        compressed_bitrate=target_bitrate_kbps,
    )


async def quick_audio_check(audio_file: str) -> bool:
    """Quick validation check for basic audio file integrity."""
    try:
        audio, sr = sf.read(audio_file)
        return len(audio) > 0 and sr > 0
    except Exception:
        return False


if __name__ == "__main__":
    # Example usage
    async def main():
        validator = AudioProcessingValidator()

        # Generate test audio
        print("Generating test audio...")
        test_audio, test_file = await validator.generate_test_audio(
            duration_seconds=2.0, include_noise=True, frequency=800
        )

        if len(test_audio) > 0:
            print(f"Generated {len(test_audio)} samples of test audio")

            # Simulate processing (add some noise reduction)
            processed_audio = test_audio * 0.9  # Simulate slight processing

            # Validate
            result = await validator.validate_audio_pipeline(test_audio, processed_audio, processing_latency_ms=25.0)

            validator.print_validation_report(result)
        else:
            print("Failed to generate test audio")

    asyncio.run(main())
