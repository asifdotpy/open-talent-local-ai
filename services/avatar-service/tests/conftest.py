"""Pytest configuration and shared fixtures for avatar service tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_paths():
    """Ensure correct import paths."""
    avatar_service_root = Path(__file__).resolve().parents[1]
    if str(avatar_service_root) not in sys.path:
        sys.path.insert(0, str(avatar_service_root))


@pytest.fixture(scope="session")
def app():
    """Load and return the FastAPI app from main.py."""
    main_path = Path(__file__).resolve().parents[1] / "main.py"
    if not main_path.exists():
        raise FileNotFoundError(f"main.py not found at {main_path}")

    spec = importlib.util.spec_from_file_location("avatar_main", main_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load spec from {main_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["avatar_main"] = module
    spec.loader.exec_module(module)

    return module.app
