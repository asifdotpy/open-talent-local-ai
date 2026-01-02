"""
Basic tests for Granite Interview Service components.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest


# Test configuration loading
def test_settings_loading():
    """Test that settings load correctly."""
    from app.config import settings

    assert settings.default_model == "granite4:350m-h"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8005

    # Test model configurations
    granite_config = settings.get_model_config("granite4:350m-h")
    assert granite_config is not None
    assert granite_config.architecture == "granite"
    assert granite_config.size == "350m"
    assert granite_config.fine_tuning_supported == True


def test_model_config_validation():
    """Test model configuration validation."""
    from app.config import settings

    # Test valid model
    validation = settings.validate_model_compatibility("granite4:350m-h")
    assert "compatible" in validation

    # Test invalid model
    validation = settings.validate_model_compatibility("nonexistent-model")
    assert validation["compatible"] == False


def test_training_prerequisites():
    """Test training prerequisite validation."""
    from app.services import training_service

    # Test with valid model and dataset
    validation = training_service.validate_training_prerequisites("granite4:350m-h", "interview_v1")

    assert validation["valid"] == True
    assert "model_config" in validation
    assert "dataset_path" in validation


def test_inference_engine_initialization():
    """Test inference engine initialization."""
    from app.services import inference_engine

    assert inference_engine.default_model == "granite4:350m-h"
    assert hasattr(inference_engine, "generate_interview_questions")
    assert hasattr(inference_engine, "analyze_candidate_response")


@patch("app.models.model_registry.load_model")
def test_model_registry(mock_load):
    """Test model registry functionality."""
    from app.models import model_registry

    mock_load.return_value = True

    # Test loading a model
    result = model_registry.load_model("granite4:350m-h")
    assert result == True

    # Test getting loaded models
    loaded = model_registry.get_loaded_models()
    assert isinstance(loaded, list)


def test_dataset_format():
    """Test that the training dataset has correct format."""
    dataset_path = Path("data/interview_v1.json")

    with open(dataset_path) as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0

    # Check required fields
    sample = data[0]
    required_fields = ["instruction", "input", "output"]
    for field in required_fields:
        assert field in sample
        assert isinstance(sample[field], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
