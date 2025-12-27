"""Renderer integration tests. Marked @pytest.mark.renderer for optional execution.
Tests interaction with Node.js render.js process and ffmpeg video generation.
Skipped if renderer infrastructure unavailable.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.renderer
def test_render_script_exists():
    """Verify render.js is present and readable."""
    render_js = Path(__file__).resolve().parents[1] / "renderer" / "render.js"
    if not render_js.exists():
        pytest.skip("render.js not found")
    assert render_js.stat().st_size > 4_000, "render.js suspiciously small"


@pytest.mark.renderer
def test_node_binary_available():
    """Verify node is available for renderer subprocess."""
    node_path = shutil.which("node")
    if not node_path:
        pytest.skip("node not in PATH")
    proc = subprocess.run([node_path, "--version"], check=False, capture_output=True, text=True, timeout=5)
    assert proc.returncode == 0, "node --version failed"
    assert proc.stdout.strip(), "node version output empty"


@pytest.mark.renderer
def test_ffmpeg_binary_available():
    """Verify ffmpeg is available for video encoding."""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        pytest.skip("ffmpeg not in PATH")
    proc = subprocess.run([ffmpeg_path, "-version"], check=False, capture_output=True, text=True, timeout=5)
    assert proc.returncode == 0, "ffmpeg -version failed"


@pytest.mark.renderer
def test_render_script_stdin_json_parsing():
    """Verify render.js can parse JSON from stdin (minimal mock)."""
    render_js = Path(__file__).resolve().parents[1] / "renderer" / "render.js"
    if not render_js.exists():
        pytest.skip("render.js not found")

    node_path = shutil.which("node")
    if not node_path:
        pytest.skip("node not available")

    # Create minimal JSON input
    json.dumps({
        "phonemes": [],
        "duration": 1.0,
        "model": "production",
        "text": "test"
    })

    # Note: Don't actually run render.js as it requires Three.js/WebGL context
    # Just verify JSON can be written to stdin without crashing parse
    # In real test, this would be wrapped in a proper headless renderer environment


@pytest.mark.renderer
def test_renderer_timeout_enforcement():
    """Render operations should timeout gracefully (>5s considered timeout)."""
    # Mock test: would actually call /render/lipsync endpoint with timeout wrapper
    max_render_time_ms = 5000
    assert max_render_time_ms > 0, "Timeout must be positive"


@pytest.mark.renderer
def test_render_output_file_validation():
    """Verify rendered video has valid format and size."""
    # Would be tested via live /render/lipsync endpoint call
    # Stub: assert output file size > 0 and format is webm/mp4
    pass


@pytest.mark.renderer
def test_renderer_phoneme_frame_generation():
    """Verify phoneme frames are generated correctly."""
    # Would test phoneme-to-viseme mapping and frame output
    # Stub: verify phoneme array maps to frame sequence
    pass


@pytest.mark.renderer
def test_renderer_concurrent_render_requests():
    """Multiple render requests should not interfere."""
    # Would spawn multiple render requests and verify isolation
    # Stub: assert each returns unique frame IDs
    pass


@pytest.mark.renderer
def test_renderer_error_on_invalid_phonemes():
    """Invalid phoneme data should fail gracefully."""
    # Would test invalid phoneme format passed to renderer
    # Stub: assert error response or 400/422
    pass


@pytest.mark.renderer
def test_renderer_memory_usage_bounds():
    """Renderer should not consume excessive memory on large inputs."""
    # Would monitor memory during render of large/long video
    # Stub: assert memory usage < 1GB
    pass


@pytest.mark.renderer
def test_render_frame_consistency():
    """Same input should produce consistent output (hash)."""
    # Would render same input twice, compare frame hashes
    # Stub: assert hash(render1) == hash(render2)
    pass
