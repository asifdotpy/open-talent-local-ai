"""
Unit Tests for Phoneme Extractor Service

Tests the PhonemeExtractor class that converts text to phoneme sequences.
Part of Phase 1: Voice Service Phoneme Extraction

Created: November 11, 2025
"""

import pytest
import sys
from pathlib import Path

# Add voice-service to path
voice_service_path = Path(__file__).parent.parent.parent / "microservices" / "voice-service"
sys.path.insert(0, str(voice_service_path))

from services.phoneme_extractor import PhonemeExtractor


@pytest.fixture
def extractor():
    """Create PhonemeExtractor instance."""
    return PhonemeExtractor()


class TestPhonemeExtractorInitialization:
    """Test PhonemeExtractor initialization."""

    def test_extractor_creation(self):
        """Test that extractor can be created."""
        extractor = PhonemeExtractor()
        assert extractor is not None

    def test_backend_initialization(self, extractor):
        """Test that espeak backend is initialized."""
        # Should not raise exception
        assert hasattr(extractor, 'backend')


class TestBasicPhonemeExtraction:
    """Test basic phoneme extraction functionality."""

    def test_extract_simple_word(self, extractor):
        """Test phoneme extraction for simple word."""
        result = extractor.extract_phonemes("hello")
        assert "phonemes" in result
        assert "words" in result
        assert len(result["phonemes"]) > 0

    def test_extract_sentence(self, extractor):
        """Test phoneme extraction for sentence."""
        result = extractor.extract_phonemes("Hello world")
        phonemes = result["phonemes"]

        assert len(phonemes) > 0
        assert all("phoneme" in p for p in phonemes)
        assert all("start" in p for p in phonemes)
        assert all("end" in p for p in phonemes)

    def test_phoneme_timing_sequential(self, extractor):
        """Test that phoneme timings are sequential."""
        result = extractor.extract_phonemes("test")
        phonemes = result["phonemes"]

        for i in range(len(phonemes) - 1):
            current = phonemes[i]
            next_phoneme = phonemes[i + 1]
            assert current["end"] <= next_phoneme["start"]

    def test_phoneme_valid_duration(self, extractor):
        """Test that each phoneme has positive duration."""
        result = extractor.extract_phonemes("hello")
        phonemes = result["phonemes"]

        for p in phonemes:
            assert p["end"] > p["start"]
            assert p["end"] - p["start"] > 0


class TestPhonemeDataStructure:
    """Test phoneme data structure and format."""

    def test_phoneme_fields(self, extractor):
        """Test that phonemes have required fields."""
        result = extractor.extract_phonemes("word")
        phonemes = result["phonemes"]

        for p in phonemes:
            assert "phoneme" in p
            assert "start" in p
            assert "end" in p
            assert isinstance(p["phoneme"], str)
            assert isinstance(p["start"], (int, float))
            assert isinstance(p["end"], (int, float))

    def test_word_grouping(self, extractor):
        """Test that words are properly grouped."""
        result = extractor.extract_phonemes("hello world")
        words = result["words"]

        assert len(words) >= 1
        for word in words:
            assert "word" in word
            assert "phonemes" in word
            assert isinstance(word["phonemes"], list)

    def test_return_format(self, extractor):
        """Test that return format matches expected structure."""
        result = extractor.extract_phonemes("test")

        assert isinstance(result, dict)
        assert "phonemes" in result
        assert "words" in result
        assert isinstance(result["phonemes"], list)
        assert isinstance(result["words"], list)


class TestTimingWithDuration:
    """Test phoneme timing with specified duration."""

    def test_timing_scales_with_duration(self, extractor):
        """Test that timing scales with specified duration."""
        text = "hello"
        duration = 2.0

        result = extractor.extract_phonemes(text, duration)
        phonemes = result["phonemes"]

        # Last phoneme should end at or near specified duration
        last_phoneme = phonemes[-1]
        assert last_phoneme["end"] <= duration * 1.1  # Allow 10% tolerance

    def test_zero_duration_handling(self, extractor):
        """Test handling of zero duration."""
        result = extractor.extract_phonemes("test", duration=0.0)
        phonemes = result["phonemes"]

        # Should still extract phonemes with default timing
        assert len(phonemes) > 0
        assert phonemes[-1]["end"] > 0

    def test_short_duration(self, extractor):
        """Test with very short duration."""
        result = extractor.extract_phonemes("hi", duration=0.5)
        phonemes = result["phonemes"]

        assert len(phonemes) > 0
        assert phonemes[-1]["end"] <= 0.6  # Should fit within duration


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_string(self, extractor):
        """Test extraction with empty string."""
        result = extractor.extract_phonemes("")
        assert isinstance(result, dict)
        assert "phonemes" in result
        assert "words" in result

    def test_single_character(self, extractor):
        """Test extraction with single character."""
        result = extractor.extract_phonemes("a")
        phonemes = result["phonemes"]
        assert len(phonemes) > 0

    def test_numbers(self, extractor):
        """Test extraction with numbers."""
        result = extractor.extract_phonemes("one two three")
        phonemes = result["phonemes"]
        assert len(phonemes) > 0

    def test_punctuation(self, extractor):
        """Test extraction with punctuation."""
        result = extractor.extract_phonemes("Hello, world!")
        phonemes = result["phonemes"]
        assert len(phonemes) > 0

    def test_multiple_spaces(self, extractor):
        """Test extraction with multiple spaces."""
        result = extractor.extract_phonemes("hello    world")
        phonemes = result["phonemes"]
        assert len(phonemes) > 0

    def test_long_text(self, extractor):
        """Test extraction with long text."""
        text = " ".join(["word"] * 50)
        result = extractor.extract_phonemes(text)
        phonemes = result["phonemes"]
        assert len(phonemes) > 100  # Should have many phonemes


class TestPhonemeAccuracy:
    """Test phoneme extraction accuracy."""

    def test_common_words_phonemes(self, extractor):
        """Test phoneme extraction for common words."""
        test_words = {
            "hello": ["HH", "EH", "L", "OW"],
            "world": ["W", "ER", "L", "D"],
            "test": ["T", "EH", "S", "T"]
        }

        for word, expected in test_words.items():
            result = extractor.extract_phonemes(word)
            extracted = [p["phoneme"] for p in result["phonemes"]]

            # Check that most expected phonemes are present
            matches = sum(1 for e in expected if e in extracted)
            assert matches >= len(expected) * 0.5  # At least 50% match

    def test_vowel_detection(self, extractor):
        """Test that vowels are detected."""
        vowel_phonemes = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"]

        result = extractor.extract_phonemes("hello world")
        extracted = [p["phoneme"] for p in result["phonemes"]]

        # Should have at least some vowels
        vowels_found = [p for p in extracted if p in vowel_phonemes]
        assert len(vowels_found) > 0

    def test_consonant_detection(self, extractor):
        """Test that consonants are detected."""
        result = extractor.extract_phonemes("test string")
        extracted = [p["phoneme"] for p in result["phonemes"]]

        # Common consonants
        consonants = ["T", "S", "R", "N", "G"]
        consonants_found = [p for p in extracted if p in consonants]
        assert len(consonants_found) > 0


class TestWordBoundaries:
    """Test word boundary detection."""

    def test_two_word_separation(self, extractor):
        """Test that two words are properly separated."""
        result = extractor.extract_phonemes("hello world")
        words = result["words"]

        assert len(words) >= 2

    def test_word_phoneme_assignment(self, extractor):
        """Test that phonemes are assigned to correct words."""
        result = extractor.extract_phonemes("hi there")
        words = result["words"]

        # Each word should have phonemes
        for word in words:
            assert len(word["phonemes"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
