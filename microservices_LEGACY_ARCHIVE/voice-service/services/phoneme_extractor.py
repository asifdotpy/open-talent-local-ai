"""
Phoneme Extractor Service for Voice Service

Provides phoneme timing extraction for lip-sync animation.
Uses phonemizer for phoneme identification and estimated timing.
"""

import logging
import re
from typing import Dict, List, Optional
from pathlib import Path
import json

try:
    from phonemizer import phonemize

    PHONEMIZER_AVAILABLE = True
except ImportError:
    PHONEMIZER_AVAILABLE = False


class PhonemeExtractor:
    """
    Extracts phonemes and timing information for lip-sync animation.

    Uses phonemizer for accurate phoneme identification and provides
    estimated timing based on phoneme count and syllable structure.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

        if not PHONEMIZER_AVAILABLE:
            self.logger.warning("Phonemizer not available. Using basic phoneme estimation.")
            self.use_phonemizer = False
        else:
            self.use_phonemizer = True

        # Basic phoneme mapping for fallback
        self.basic_phonemes = {
            "a": ["AH"],
            "e": ["EH"],
            "i": ["IH"],
            "o": ["OW"],
            "u": ["UH"],
            "th": ["TH"],
            "sh": ["SH"],
            "ch": ["CH"],
            "ph": ["F"],
            "wh": ["W"],
            "qu": ["K", "W"],
            "ck": ["K"],
            "ng": ["NG"],
            "er": ["ER"],
            "tion": ["SH", "AH", "N"],
            "ture": ["CH", "ER"],
            "sure": ["ZH", "ER"],
            "cious": ["SH", "AH", "S"],
            "tious": ["SH", "AH", "S"],
            "sious": ["ZH", "AH", "S"],
        }

    def extract_phonemes(self, text: str, duration: float = 0.0) -> Dict:
        """
        Extract phonemes and timing from text.

        Args:
            text: Input text
            duration: Audio duration in seconds (0 = estimate)

        Returns:
            Dictionary with phonemes and words timing
        """
        try:
            if self.use_phonemizer:
                return self._extract_with_phonemizer(text, duration)
            else:
                return self._extract_basic(text, duration)

        except Exception as e:
            self.logger.error(f"Phoneme extraction failed: {e}")
            return self._extract_basic(text, duration)

    def _extract_with_phonemizer(self, text: str, duration: float = 0.0) -> Dict:
        """Extract phonemes using phonemizer library."""
        # Get phoneme string from phonemizer
        phoneme_text = phonemize(text, language="en-us", backend="espeak", strip=True)

        # Split text into words for alignment
        word_list = re.findall(r"\b\w+\b", text.lower())

        # Estimate duration if not provided
        if duration <= 0:
            duration = max(1.0, len(word_list) * 0.4)  # ~400ms per word

        # Create approximate phoneme segmentation
        # This is a simplified approach - in production you'd want better alignment
        phoneme_parts = self._segment_phonemes(phoneme_text, len(word_list))

        phonemes = []
        words = []

        current_time = 0.0
        phoneme_idx = 0

        for word_idx, word in enumerate(word_list):
            # Estimate phonemes per word based on syllable count
            syllable_count = self._count_syllables(word)
            phonemes_in_word = max(1, syllable_count * 2)  # ~2 phonemes per syllable

            word_start = current_time
            word_duration = duration * (len(word) / max(1, len(text.replace(" ", ""))))
            word_end = word_start + word_duration

            word_phonemes = []

            # Distribute phonemes across the word duration
            for i in range(phonemes_in_word):
                if phoneme_idx < len(phoneme_parts):
                    phoneme_duration = word_duration / phonemes_in_word
                    phoneme_start = word_start + (i * phoneme_duration)
                    phoneme_end = phoneme_start + phoneme_duration

                    phoneme_symbol = (
                        phoneme_parts[phoneme_idx] if phoneme_idx < len(phoneme_parts) else "AH"
                    )

                    phonemes.append(
                        {
                            "phoneme": phoneme_symbol.upper(),
                            "start": round(phoneme_start, 3),
                            "end": round(phoneme_end, 3),
                            "duration": round(phoneme_duration, 3),
                        }
                    )
                    word_phonemes.append(phoneme_symbol.upper())
                    phoneme_idx += 1

            words.append(
                {
                    "word": word,
                    "start": round(word_start, 3),
                    "end": round(word_end, 3),
                    "phonemes": word_phonemes,
                }
            )

            current_time = word_end

        return {"phonemes": phonemes, "words": words, "text": text, "duration": duration}

    def _segment_phonemes(self, phoneme_text: str, num_words: int) -> List[str]:
        """Segment phoneme text into individual phoneme symbols."""
        # Split on spaces and common phoneme boundaries
        parts = re.split(r"[ː\s]+", phoneme_text)

        # Further split compound phonemes
        phonemes = []
        for part in parts:
            if len(part) <= 2:
                phonemes.append(part)
            else:
                # Split longer sequences into individual phonemes
                for char in part:
                    if char not in ["ː", "ˈ", "ˌ"]:  # Skip stress markers
                        phonemes.append(char)

        # Filter out empty strings
        phonemes = [p for p in phonemes if p.strip()]

        # If we have too few phonemes, pad with common ones
        while len(phonemes) < num_words * 2:
            phonemes.append("AH")

        return phonemes[: num_words * 3]  # Limit to reasonable number

    def _extract_basic(self, text: str, duration: float = 0.0) -> Dict:
        """Basic phoneme extraction without phonemizer."""
        # Estimate duration if not provided
        if duration <= 0:
            duration = max(1.0, len(text.split()) * 0.3)

        phonemes = []
        words = []

        # Split text into words
        word_list = re.findall(r"\b\w+\b", text.lower())

        current_time = 0.0
        total_phonemes = 0

        # Count total phonemes for timing distribution
        for word in word_list:
            total_phonemes += self._estimate_phoneme_count(word)

        if total_phonemes == 0:
            total_phonemes = len(word_list) * 2  # fallback

        time_per_phoneme = duration / total_phonemes

        for word in word_list:
            word_phonemes = self._get_basic_phonemes(word)
            word_duration = len(word_phonemes) * time_per_phoneme
            word_start = current_time
            word_end = current_time + word_duration

            # Add phonemes for this word
            for phoneme in word_phonemes:
                phoneme_start = current_time
                phoneme_end = current_time + time_per_phoneme

                phonemes.append(
                    {
                        "phoneme": phoneme,
                        "start": round(phoneme_start, 3),
                        "end": round(phoneme_end, 3),
                        "duration": round(time_per_phoneme, 3),
                    }
                )

                current_time = phoneme_end

            words.append(
                {
                    "word": word,
                    "start": round(word_start, 3),
                    "end": round(word_end, 3),
                    "phonemes": word_phonemes,
                }
            )

        return {"phonemes": phonemes, "words": words, "text": text, "duration": duration}

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"

        if word[0] in vowels:
            count += 1

        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1

        if word.endswith("e"):
            count -= 1

        if count == 0:
            count += 1

        return count

    def _estimate_phoneme_count(self, word: str) -> int:
        """Estimate number of phonemes in a word."""
        word = word.lower()
        count = 0

        i = 0
        while i < len(word):
            # Check for digraphs first
            if i < len(word) - 1:
                digraph = word[i : i + 2]
                if digraph in self.basic_phonemes:
                    count += len(self.basic_phonemes[digraph])
                    i += 2
                    continue

            # Single letter
            if word[i] in self.basic_phonemes:
                count += len(self.basic_phonemes[word[i]])
            else:
                count += 1  # Default to 1 phoneme

            i += 1

        return max(1, count)

    def _get_basic_phonemes(self, word: str) -> List[str]:
        """Get basic phoneme list for a word."""
        word = word.lower()
        phonemes = []

        i = 0
        while i < len(word):
            # Check for digraphs first
            if i < len(word) - 1:
                digraph = word[i : i + 2]
                if digraph in self.basic_phonemes:
                    phonemes.extend(self.basic_phonemes[digraph])
                    i += 2
                    continue

            # Single letter
            if word[i] in self.basic_phonemes:
                phonemes.extend(self.basic_phonemes[word[i]])
            else:
                phonemes.append(word[i].upper())  # Default

            i += 1

        return phonemes if phonemes else [word[0].upper()]


# Test function
if __name__ == "__main__":
    extractor = PhonemeExtractor()

    test_text = "Hello world, how are you today?"
    result = extractor.extract_phonemes(test_text, duration=3.0)

    print(f"Text: {test_text}")
    print(f"Duration: {result['duration']}s")
    print(f"Phonemes: {len(result['phonemes'])}")
    print(f"Words: {len(result['words'])}")

    print("\nPhoneme timing:")
    for p in result["phonemes"][:10]:  # Show first 10
        print(f"  {p['phoneme']}: {p['start']:.3f}-{p['end']:.3f}s")

    print("\nWord timing:")
    for w in result["words"]:
        print(f"  {w['word']}: {w['start']:.3f}-{w['end']:.3f}s")
