"""Optional renderer sanity tests. Skipped if node is unavailable."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.renderer
def test_node_binary_available():
    node_path = shutil.which("node")
    if not node_path:
        pytest.skip("node not available in PATH; renderer tests skipped")
    # Smoke check: node --version must succeed quickly
    proc = subprocess.run([node_path, "--version"], check=False, capture_output=True, text=True, timeout=5)
    assert proc.returncode == 0, "node --version failed"
    assert proc.stdout.strip(), "node --version produced no output"


@pytest.mark.renderer
def test_render_script_exists_and_is_readable():
    render_js = Path(__file__).resolve().parents[1] / "renderer" / "render.js"
    if not render_js.exists():
        pytest.skip("render.js missing; renderer not vendored")
    assert render_js.stat().st_size > 4_000, "render.js unexpectedly small"
    with open(render_js, encoding="utf-8") as f:
        head = f.read(256)
    assert "render.js" in head or "lip-sync" in head.lower(), "render.js content looks unexpected"
