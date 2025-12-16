"""
Modular Sentiment Analysis Service for TalentAI Platform

This service provides sentiment analysis capabilities using various models:
- BERT (via transformers library)
- Pre-trained sentiment models
- Custom fine-tuned models
- API-based sentiment services (future)

The service uses a strategy pattern for easy model switching and includes
caching, batch processing, and confidence scoring.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentModel(Enum):
    """Available sentiment analysis models."""
    BERT_BASE = "bert_base"
    BERT_LARGE = "bert_large"
    DISTILBERT = "distilbert"
    ROBERTA = "roberta"
    MOCK = "mock"

@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    sentiment: str  # "positive", "negative", "neutral"
    confidence: float  # 0.0 to 1.0
    scores: Dict[str, float]  # Raw scores for each class
    model_used: str
    processing_time: float
    text_hash: str
    timestamp: datetime

@dataclass
class SentimentConfig:
    """Configuration for sentiment analysis."""
    model: SentimentModel
    model_name: str
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    batch_size: int = 16
    max_length: int = 512
    device: str = "auto"  # "cpu", "cuda", "auto"

class BaseSentimentAnalyzer(ABC):
    """Abstract base class for sentiment analyzers."""

    def __init__(self, config: SentimentConfig):
        self.config = config
        self.cache: Dict[str, SentimentResult] = {}
        self.model = None
        self.tokenizer = None

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text."""
        pass

    @abstractmethod
    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment of multiple texts in batch."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the analyzer is healthy."""
        pass

    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text caching."""
        return hashlib.md5(text.encode()).hexdigest()

    def _get_cached_result(self, text_hash: str) -> Optional[SentimentResult]:
        """Get cached result if available and not expired."""
        if not self.config.cache_enabled:
            return None

        result = self.cache.get(text_hash)
        if result:
            # Check if cache is expired
            if datetime.now() - result.timestamp > timedelta(hours=self.config.cache_ttl_hours):
                del self.cache[text_hash]
                return None
        return result

    def _cache_result(self, text_hash: str, result: SentimentResult):
        """Cache sentiment result."""
        if self.config.cache_enabled:
            self.cache[text_hash] = result

class BERTSentimentAnalyzer(BaseSentimentAnalyzer):
    """BERT-based sentiment analyzer using transformers."""

    def __init__(self, config: SentimentConfig):
        super().__init__(config)
        self._load_model()

    def _load_model(self):
        """Load the BERT model and tokenizer."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            # Determine device
            if self.config.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = self.config.device

            logger.info(f"Loading {self.config.model_name} sentiment model on {self.device}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.config.model_name)
            self.model.to(self.device)
            self.model.eval()

            # Get label mapping
            self.id2label = self.model.config.id2label
            self.label2id = {v: k for k, v in self.id2label.items()}

            logger.info(f"Successfully loaded {self.config.model_name} with labels: {list(self.id2label.values())}")

        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
            raise

    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text using BERT."""
        start_time = datetime.now()
        text_hash = self._get_text_hash(text)

        # Check cache first
        cached_result = self._get_cached_result(text_hash)
        if cached_result:
            logger.debug(f"Using cached sentiment result for text hash {text_hash}")
            return cached_result

        try:
            import torch

            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=self.config.max_length
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)

            # Get prediction
            predicted_class_idx = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class_idx].item()

            # Get all scores
            scores = {}
            for idx, prob in enumerate(probabilities[0]):
                label = self.id2label[idx]
                scores[label.lower()] = prob.item()

            # Map to standard sentiment labels
            predicted_label = self.id2label[predicted_class_idx].lower()
            sentiment = self._map_to_sentiment(predicted_label)

            processing_time = (datetime.now() - start_time).total_seconds()

            result = SentimentResult(
                sentiment=sentiment,
                confidence=confidence,
                scores=scores,
                model_used=self.config.model_name,
                processing_time=processing_time,
                text_hash=text_hash,
                timestamp=datetime.now()
            )

            # Cache result
            self._cache_result(text_hash, result)

            return result

        except Exception as e:
            logger.error(f"BERT sentiment analysis failed: {e}")
            raise

    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment of multiple texts in batch."""
        results = []
        for i in range(0, len(texts), self.config.batch_size):
            batch_texts = texts[i:i + self.config.batch_size]
            batch_results = await asyncio.gather(*[
                self.analyze_sentiment(text) for text in batch_texts
            ])
            results.extend(batch_results)
        return results

    def _map_to_sentiment(self, label: str) -> str:
        """Map model-specific labels to standard sentiment labels."""
        label_lower = label.lower()

        # Common mappings for different BERT models
        if "positive" in label_lower or "pos" in label_lower or "4" in label_lower or "5" in label_lower:
            return "positive"
        elif "negative" in label_lower or "neg" in label_lower or "1" in label_lower or "2" in label_lower:
            return "negative"
        elif "neutral" in label_lower or "neu" in label_lower or "3" in label_lower:
            return "neutral"
        else:
            # Default fallback
            return "neutral"

    async def health_check(self) -> bool:
        """Check if BERT model is loaded and working."""
        try:
            if not self.model or not self.tokenizer:
                return False

            # Quick test with a simple sentence
            test_result = await self.analyze_sentiment("This is a test sentence.")
            return test_result.confidence > 0
        except Exception as e:
            logger.error(f"BERT health check failed: {e}")
            return False

class MockSentimentAnalyzer(BaseSentimentAnalyzer):
    """Mock sentiment analyzer for testing."""

    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Return mock sentiment analysis."""
        await asyncio.sleep(0.01)  # Simulate processing time

        text_hash = self._get_text_hash(text)

        # Check cache
        cached_result = self._get_cached_result(text_hash)
        if cached_result:
            return cached_result

        # Simple mock logic based on keywords
        text_lower = text.lower()
        if any(word in text_lower for word in ["good", "great", "excellent", "amazing", "love"]):
            sentiment = "positive"
            confidence = 0.8
        elif any(word in text_lower for word in ["bad", "terrible", "awful", "hate", "worst"]):
            sentiment = "negative"
            confidence = 0.8
        else:
            sentiment = "neutral"
            confidence = 0.6

        scores = {
            "positive": confidence if sentiment == "positive" else 0.1,
            "negative": confidence if sentiment == "negative" else 0.1,
            "neutral": confidence if sentiment == "neutral" else 0.1
        }

        result = SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            scores=scores,
            model_used="mock_analyzer",
            processing_time=0.01,
            text_hash=text_hash,
            timestamp=datetime.now()
        )

        self._cache_result(text_hash, result)
        return result

    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze batch with mock results."""
        return await asyncio.gather(*[self.analyze_sentiment(text) for text in texts])

    async def health_check(self) -> bool:
        """Mock health check always passes."""
        return True

class ModularSentimentService:
    """Main service that manages multiple sentiment analyzers."""

    def __init__(self):
        self.analyzers: Dict[SentimentModel, BaseSentimentAnalyzer] = {}
        self.primary_analyzer: Optional[SentimentModel] = None
        self.fallback_analyzer: Optional[SentimentModel] = None

    def configure_analyzer(self, config: SentimentConfig):
        """Configure a specific sentiment analyzer."""
        if config.model == SentimentModel.MOCK:
            analyzer = MockSentimentAnalyzer(config)
        else:
            # All BERT variants use the same analyzer class
            analyzer = BERTSentimentAnalyzer(config)

        self.analyzers[config.model] = analyzer

        # Set primary analyzer if not set
        if not self.primary_analyzer:
            self.primary_analyzer = config.model

    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment using primary analyzer with fallback."""
        return await self._execute_with_fallback("analyze_sentiment", text)

    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment for multiple texts."""
        return await self._execute_with_fallback("analyze_batch", texts)

    async def _execute_with_fallback(self, method_name: str, *args, **kwargs):
        """Execute method with fallback to secondary analyzer."""
        primary = self.analyzers.get(self.primary_analyzer)
        if not primary:
            raise ValueError(f"Primary analyzer {self.primary_analyzer} not configured")

        try:
            method = getattr(primary, method_name)
            result = await method(*args, **kwargs)
            logger.info(f"Successfully used {self.primary_analyzer.value} for {method_name}")
            return result
        except Exception as e:
            logger.warning(f"Primary analyzer {self.primary_analyzer.value} failed: {e}")

            # Try fallback analyzer
            if self.fallback_analyzer and self.fallback_analyzer in self.analyzers:
                try:
                    fallback = self.analyzers[self.fallback_analyzer]
                    method = getattr(fallback, method_name)
                    result = await method(*args, **kwargs)
                    logger.info(f"Successfully used fallback {self.fallback_analyzer.value} for {method_name}")
                    return result
                except Exception as fallback_e:
                    logger.error(f"Fallback analyzer {self.fallback_analyzer.value} also failed: {fallback_e}")

            raise e

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all configured analyzers."""
        results = {}
        for analyzer_type, analyzer in self.analyzers.items():
            results[analyzer_type.value] = await analyzer.health_check()
        return results

    def clear_cache(self):
        """Clear all analyzer caches."""
        for analyzer in self.analyzers.values():
            analyzer.cache.clear()
        logger.info("Cleared all sentiment analysis caches")

# Global instance
modular_sentiment_service = ModularSentimentService()

def configure_sentiment_service():
    """Configure the sentiment service based on environment variables."""
    # Primary analyzer configuration
    primary_model_str = os.getenv("SENTIMENT_MODEL", "mock").lower()
    primary_model_name = os.getenv("SENTIMENT_MODEL_NAME", "cardiffnlp/twitter-roberta-base-sentiment-latest")

    # Fallback analyzer configuration
    fallback_model_str = os.getenv("SENTIMENT_FALLBACK_MODEL", "mock").lower()
    fallback_model_name = os.getenv("SENTIMENT_FALLBACK_MODEL_NAME", "cardiffnlp/twitter-roberta-base-sentiment-latest")

    # Map string to enum
    try:
        primary_model = SentimentModel(primary_model_str)
    except ValueError:
        logger.warning(f"Invalid SENTIMENT_MODEL '{primary_model_str}', using 'mock'")
        primary_model = SentimentModel.MOCK

    try:
        fallback_model = SentimentModel(fallback_model_str)
    except ValueError:
        logger.warning(f"Invalid SENTIMENT_FALLBACK_MODEL '{fallback_model_str}', using 'mock'")
        fallback_model = SentimentModel.MOCK

    # Configure primary analyzer
    primary_config = SentimentConfig(
        model=primary_model,
        model_name=primary_model_name,
        cache_enabled=os.getenv("SENTIMENT_CACHE_ENABLED", "true").lower() == "true",
        cache_ttl_hours=int(os.getenv("SENTIMENT_CACHE_TTL_HOURS", "24")),
        batch_size=int(os.getenv("SENTIMENT_BATCH_SIZE", "16")),
        max_length=int(os.getenv("SENTIMENT_MAX_LENGTH", "512")),
        device=os.getenv("SENTIMENT_DEVICE", "auto")
    )

    modular_sentiment_service.configure_analyzer(primary_config)

    # Configure fallback analyzer if different from primary
    if fallback_model != primary_model:
        fallback_config = SentimentConfig(
            model=fallback_model,
            model_name=fallback_model_name,
            cache_enabled=os.getenv("SENTIMENT_FALLBACK_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl_hours=int(os.getenv("SENTIMENT_FALLBACK_CACHE_TTL_HOURS", "24")),
            batch_size=int(os.getenv("SENTIMENT_FALLBACK_BATCH_SIZE", "16")),
            max_length=int(os.getenv("SENTIMENT_FALLBACK_MAX_LENGTH", "512")),
            device=os.getenv("SENTIMENT_FALLBACK_DEVICE", "auto")
        )

        modular_sentiment_service.configure_analyzer(fallback_config)
        # Note: We don't set fallback in config since it's handled at service level

    logger.info(f"Configured sentiment service with primary: {primary_model.value}, fallback: {fallback_model.value}")

# Initialize on import
configure_sentiment_service()