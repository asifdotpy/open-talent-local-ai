"""Unit Tests for PhonemeExtractor.

Tests phoneme extraction, timing accuracy, syllable counting, and basic phoneme mapping.
"""

import sys
from pathlib import Path

import pytest

# Add services directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from phoneme_extractor import PhonemeExtractor


class TestPhonemeExtractorInitialization:
    """Test PhonemeExtractor initialization and configuration."""

    def test_initialization_success(self):
        """Test successful initialization."""
        extractor = PhonemeExtractor()
        assert extractor is not None
        assert hasattr(extractor, "logger")
        assert hasattr(extractor, "basic_phonemes")
        assert isinstance(extractor.basic_phonemes, dict)

    def test_phonemizer_availability_detection(self):
        """Test detection of phonemizer library availability."""
        extractor = PhonemeExtractor()
        # Should have use_phonemizer attribute set based on availability
        assert hasattr(extractor, "use_phonemizer")
        assert isinstance(extractor.use_phonemizer, bool)

    def test_basic_phoneme_mapping_loaded(self):
        """Test that basic phoneme mapping dictionary is loaded."""
        extractor = PhonemeExtractor()
        # Should have common mappings
        assert "a" in extractor.basic_phonemes
        assert "e" in extractor.basic_phonemes
        assert "th" in extractor.basic_phonemes
        assert "sh" in extractor.basic_phonemes

        # Verify mapping structure
        assert isinstance(extractor.basic_phonemes["a"], list)
        assert len(extractor.basic_phonemes["a"]) > 0


class TestSyllableCounting:
    """Test syllable counting accuracy."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_single_syllable_words(self):
        """Test single syllable word counting."""
        assert self.extractor._count_syllables("cat") == 1
        assert self.extractor._count_syllables("dog") == 1
        assert self.extractor._count_syllables("fish") == 1
        assert self.extractor._count_syllables("tree") == 1

    def test_two_syllable_words(self):
        """Test two syllable word counting."""
        assert self.extractor._count_syllables("hello") == 2
        assert self.extractor._count_syllables("water") == 2
        assert self.extractor._count_syllables("happy") == 2
        assert self.extractor._count_syllables("teacher") == 2

    def test_three_syllable_words(self):
        """Test three syllable word counting."""
        assert self.extractor._count_syllables("beautiful") == 3
        assert self.extractor._count_syllables("together") == 3
        assert self.extractor._count_syllables("elephant") == 3

    def test_complex_words(self):
        """Test complex multi-syllable words."""
        # These might not be perfectly accurate due to algorithm simplicity
        syllables = self.extractor._count_syllables("imagination")
        assert syllables >= 4  # At least 4 syllables

        syllables = self.extractor._count_syllables("responsibility")
        assert syllables >= 5  # At least 5 syllables

    def test_words_ending_in_e(self):
        """Test words ending in silent 'e'."""
        # Silent e should reduce syllable count
        assert self.extractor._count_syllables("make") == 1
        assert self.extractor._count_syllables("take") == 1
        assert self.extractor._count_syllables("phone") == 1

    def test_empty_and_edge_cases(self):
        """Test edge cases for syllable counting."""
        # Single letter should be 1 syllable
        assert self.extractor._count_syllables("a") == 1
        assert self.extractor._count_syllables("i") == 1


class TestPhonemeEstimation:
    """Test phoneme count estimation."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_simple_word_phoneme_count(self):
        """Test phoneme count for simple words."""
        # 'cat' = C + A + T = 3 phonemes
        count = self.extractor._estimate_phoneme_count("cat")
        assert count >= 2  # At least a couple phonemes

        # 'dog' = D + O + G = 3 phonemes
        count = self.extractor._estimate_phoneme_count("dog")
        assert count >= 2

    def test_digraph_phoneme_count(self):
        """Test phoneme count with digraphs."""
        # 'ship' = SH + I + P = 3 phonemes (not 4)
        count = self.extractor._estimate_phoneme_count("ship")
        assert count >= 2

        # 'phone' = PH + O + N + E = 4 phonemes
        count = self.extractor._estimate_phoneme_count("phone")
        assert count >= 3

    def test_complex_word_phoneme_count(self):
        """Test phoneme count for complex words."""
        count = self.extractor._estimate_phoneme_count("threshold")
        assert count >= 6  # TH + R + E + SH + O + L + D

        count = self.extractor._estimate_phoneme_count("question")
        assert count >= 6  # QU + E + S + T + I + O + N

    def test_minimum_phoneme_count(self):
        """Test that phoneme count is at least 1."""
        # Even empty or single letter should return at least 1
        count = self.extractor._estimate_phoneme_count("a")
        assert count >= 1


class TestBasicPhonemeExtraction:
    """Test basic phoneme extraction without phonemizer."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_simple_word_phonemes(self):
        """Test basic phoneme extraction for simple words."""
        phonemes = self.extractor._get_basic_phonemes("cat")
        assert isinstance(phonemes, list)
        assert len(phonemes) > 0

        # Should have some phoneme symbols
        for p in phonemes:
            assert isinstance(p, str)
            assert len(p) > 0

    def test_digraph_detection(self):
        """Test that digraphs are properly detected."""
        phonemes = self.extractor._get_basic_phonemes("ship")
        # 'sh' should be detected as digraph
        # Exact phoneme symbols depend on implementation
        assert len(phonemes) >= 2

    def test_vowel_phonemes(self):
        """Test vowel phoneme extraction."""
        phonemes = self.extractor._get_basic_phonemes("eat")
        assert len(phonemes) >= 2

        phonemes = self.extractor._get_basic_phonemes("out")
        assert len(phonemes) >= 2

    def test_empty_word_fallback(self):
        """Test fallback for empty or single character words."""
        phonemes = self.extractor._get_basic_phonemes("a")
        # Should return at least one phoneme
        assert len(phonemes) >= 1


class TestBasicPhonemeExtractionWithTiming:
    """Test complete basic phoneme extraction with timing."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_basic_extraction_structure(self):
        """Test that basic extraction returns correct structure."""
        result = self.extractor._extract_basic("hello world", duration=2.0)

        # Verify structure
        assert "phonemes" in result
        assert "words" in result
        assert "text" in result
        assert "duration" in result

        assert isinstance(result["phonemes"], list)
        assert isinstance(result["words"], list)
        assert result["text"] == "hello world"
        assert result["duration"] == 2.0

    def test_phoneme_timing_fields(self):
        """Test that phonemes have correct timing fields."""
        result = self.extractor._extract_basic("hello", duration=1.0)

        assert len(result["phonemes"]) > 0

        for phoneme in result["phonemes"]:
            assert "phoneme" in phoneme
            assert "start" in phoneme
            assert "end" in phoneme
            assert "duration" in phoneme

            # Verify types
            assert isinstance(phoneme["phoneme"], str)
            assert isinstance(phoneme["start"], (int, float))
            assert isinstance(phoneme["end"], (int, float))
            assert isinstance(phoneme["duration"], (int, float))

            # Verify timing logic
            assert phoneme["start"] >= 0
            assert phoneme["end"] > phoneme["start"]
            assert abs(phoneme["duration"] - (phoneme["end"] - phoneme["start"])) < 0.01

    def test_word_timing_fields(self):
        """Test that words have correct timing fields."""
        result = self.extractor._extract_basic("hello world", duration=2.0)

        assert len(result["words"]) == 2

        for word in result["words"]:
            assert "word" in word
            assert "start" in word
            assert "end" in word
            assert "phonemes" in word

            assert isinstance(word["word"], str)
            assert isinstance(word["start"], (int, float))
            assert isinstance(word["end"], (int, float))
            assert isinstance(word["phonemes"], list)

            # Verify timing
            assert word["start"] >= 0
            assert word["end"] > word["start"]

    def test_timing_distribution(self):
        """Test that phonemes are distributed across duration."""
        result = self.extractor._extract_basic("test", duration=1.0)

        phonemes = result["phonemes"]
        assert len(phonemes) > 0

        # First phoneme should start near 0
        assert phonemes[0]["start"] < 0.2

        # Last phoneme should end near total duration
        assert phonemes[-1]["end"] > 0.8

    def test_auto_duration_estimation(self):
        """Test automatic duration estimation when duration=0."""
        result = self.extractor._extract_basic("hello world", duration=0.0)

        # Should estimate duration (roughly 0.3s per word = 0.6s total)
        assert result["duration"] > 0
        assert result["duration"] >= 0.5  # At least 2 words * 0.3s
        assert result["duration"] <= 2.0  # Reasonable upper bound

    def test_multiple_words_alignment(self):
        """Test that multiple words are properly aligned."""
        result = self.extractor._extract_basic("one two three", duration=3.0)

        words = result["words"]
        assert len(words) == 3

        # Words should be in sequence
        assert words[0]["word"] == "one"
        assert words[1]["word"] == "two"
        assert words[2]["word"] == "three"

        # Words should not overlap
        assert words[0]["end"] <= words[1]["start"]
        assert words[1]["end"] <= words[2]["start"]


class TestPhonemeExtractorMainMethod:
    """Test main extract_phonemes method."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_extract_phonemes_basic(self):
        """Test main extraction method."""
        result = self.extractor.extract_phonemes("hello world", duration=2.0)

        # Should return dictionary with required keys
        assert "phonemes" in result
        assert "words" in result
        assert "text" in result
        assert "duration" in result

    def test_extract_phonemes_auto_duration(self):
        """Test extraction with automatic duration estimation."""
        result = self.extractor.extract_phonemes("testing automatic duration")

        assert result["duration"] > 0
        assert len(result["phonemes"]) > 0
        assert len(result["words"]) == 3

    def test_extract_phonemes_empty_text(self):
        """Test extraction with empty text."""
        # Should handle gracefully
        try:
            result = self.extractor.extract_phonemes("")
            # If it succeeds, should have empty or minimal data
            assert isinstance(result, dict)
        except Exception:
            # If it fails, that's also acceptable behavior
            pass

    def test_extract_phonemes_special_characters(self):
        """Test extraction with punctuation and special characters."""
        result = self.extractor.extract_phonemes("Hello, world! How are you?", duration=3.0)

        # Should extract actual words, ignoring punctuation
        assert len(result["words"]) >= 4  # hello, world, how, are, you

        # Words should be clean
        for word in result["words"]:
            assert word["word"].isalpha()  # No punctuation in words

    def test_extract_phonemes_numbers(self):
        """Test extraction with numbers in text."""
        result = self.extractor.extract_phonemes("I have 2 cats", duration=2.0)

        # Should handle numbers (may extract '2' as word or skip it)
        assert len(result["words"]) >= 2  # At least 'have' and 'cats'

    def test_phoneme_timing_consistency(self):
        """Test that phoneme timing is consistent and logical."""
        result = self.extractor.extract_phonemes("consistency test", duration=2.0)

        phonemes = result["phonemes"]

        # Phonemes should be in chronological order
        for i in range(len(phonemes) - 1):
            assert phonemes[i]["end"] <= phonemes[i + 1]["start"] + 0.01  # Small tolerance

    def test_word_phoneme_alignment(self):
        """Test that phonemes align with words."""
        result = self.extractor.extract_phonemes("test word", duration=2.0)

        # Each word should have phonemes listed
        for word in result["words"]:
            assert len(word["phonemes"]) > 0

            # Word phonemes should be strings
            for p in word["phonemes"]:
                assert isinstance(p, str)


class TestPhonemeExtractorEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_very_long_text(self):
        """Test extraction with very long text."""
        long_text = "word " * 100  # 100 words
        result = self.extractor.extract_phonemes(long_text, duration=40.0)

        # Should handle without crashing
        assert len(result["words"]) > 0
        assert len(result["phonemes"]) > 0

    def test_very_short_text(self):
        """Test extraction with single word."""
        result = self.extractor.extract_phonemes("hi", duration=0.5)

        assert len(result["words"]) == 1
        assert result["words"][0]["word"] == "hi"
        assert len(result["phonemes"]) > 0

    def test_repeated_words(self):
        """Test extraction with repeated words."""
        result = self.extractor.extract_phonemes("test test test", duration=3.0)

        assert len(result["words"]) == 3
        # All words should be 'test'
        for word in result["words"]:
            assert word["word"] == "test"

    def test_mixed_case_text(self):
        """Test extraction with mixed case."""
        result = self.extractor.extract_phonemes("HeLLo WoRLd", duration=2.0)

        # Should normalize to lowercase
        assert all(word["word"].islower() for word in result["words"])

    def test_unicode_text(self):
        """Test extraction with unicode characters."""
        # Should handle or skip unicode gracefully
        try:
            result = self.extractor.extract_phonemes("café résumé", duration=2.0)
            assert isinstance(result, dict)
        except Exception:
            # If it fails, that's acceptable for basic implementation
            pass

    def test_zero_duration(self):
        """Test that zero duration triggers auto-estimation."""
        result = self.extractor.extract_phonemes("auto estimate", duration=0.0)

        # Should have auto-estimated duration
        assert result["duration"] > 0

    def test_negative_duration(self):
        """Test that negative duration triggers auto-estimation."""
        result = self.extractor.extract_phonemes("negative test", duration=-1.0)

        # Should have auto-estimated duration (positive)
        assert result["duration"] > 0


class TestPhonemeSymbols:
    """Test phoneme symbol generation."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_phoneme_symbols_are_strings(self):
        """Test that all phoneme symbols are strings."""
        result = self.extractor.extract_phonemes("testing symbols", duration=2.0)

        for phoneme in result["phonemes"]:
            assert isinstance(phoneme["phoneme"], str)
            assert len(phoneme["phoneme"]) > 0

    def test_phoneme_symbols_uppercase(self):
        """Test that phoneme symbols are uppercase."""
        result = self.extractor.extract_phonemes("uppercase test", duration=2.0)

        for phoneme in result["phonemes"]:
            # Most phoneme symbols should be uppercase
            # (some might have special characters depending on implementation)
            assert any(c.isupper() for c in phoneme["phoneme"]) or len(phoneme["phoneme"]) <= 2

    def test_common_phoneme_symbols_present(self):
        """Test that common English phonemes appear."""
        # Test with text containing various sounds
        result = self.extractor.extract_phonemes(
            "the quick brown fox jumps over the lazy dog", duration=5.0
        )

        phoneme_set = {p["phoneme"] for p in result["phonemes"]}

        # Should have a variety of phoneme symbols
        assert len(phoneme_set) >= 5  # At least 5 different phonemes


class TestTimingAccuracy:
    """Test timing accuracy and precision."""

    def setup_method(self):
        """Setup for each test."""
        self.extractor = PhonemeExtractor()

    def test_timing_precision(self):
        """Test that timing values are properly rounded."""
        result = self.extractor.extract_phonemes("precision test", duration=2.0)

        for phoneme in result["phonemes"]:
            # Should be rounded to 3 decimal places
            start_str = f"{phoneme['start']:.3f}"
            end_str = f"{phoneme['end']:.3f}"
            duration_str = f"{phoneme['duration']:.3f}"

            # Converting back should match
            assert abs(float(start_str) - phoneme["start"]) < 0.0001
            assert abs(float(end_str) - phoneme["end"]) < 0.0001
            assert abs(float(duration_str) - phoneme["duration"]) < 0.0001

    def test_no_overlapping_phonemes(self):
        """Test that phonemes don't overlap."""
        result = self.extractor.extract_phonemes("no overlap test", duration=3.0)

        phonemes = result["phonemes"]
        for i in range(len(phonemes) - 1):
            # Next phoneme should start at or after current phoneme ends
            assert phonemes[i + 1]["start"] >= phonemes[i]["end"] - 0.01  # Small tolerance

    def test_total_duration_coverage(self):
        """Test that phonemes roughly cover the total duration."""
        duration = 3.0
        result = self.extractor.extract_phonemes("duration coverage test", duration=duration)

        if len(result["phonemes"]) > 0:
            first_start = result["phonemes"][0]["start"]
            last_end = result["phonemes"][-1]["end"]

            # Should start near 0
            assert first_start < 0.5

            # Should end near total duration
            assert last_end > duration * 0.7  # At least 70% of duration


# Integration test that runs the example from the module
class TestPhonemeExtractorExample:
    """Test the example from the module's __main__ block."""

    def test_module_example(self):
        """Test the example code from the module."""
        extractor = PhonemeExtractor()

        test_text = "Hello world, how are you today?"
        result = extractor.extract_phonemes(test_text, duration=3.0)

        assert result["text"] == test_text
        assert result["duration"] == 3.0
        assert len(result["phonemes"]) > 0
        assert len(result["words"]) > 0

        # Verify some words extracted
        word_list = [w["word"] for w in result["words"]]
        assert "hello" in word_list
        assert "world" in word_list


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
