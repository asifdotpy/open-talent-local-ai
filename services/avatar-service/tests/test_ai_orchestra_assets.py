"""
Sanity checks for ai-orchestra-simulation dependency files.
Does not start the service; ensures required assets are present.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.assets
def test_ai_orchestra_assets_presence():
    root = Path(__file__).resolve().parents[3] / "ai-orchestra-simulation"
    if not root.exists():
        pytest.skip("ai-orchestra-simulation directory not present")

    avatar_html = root / "avatar.html"
    assets_dir = root / "assets"
    src_dir = root / "src"

    if not avatar_html.exists():
        pytest.skip("avatar.html missing; ai-orchestra-simulation not synced")
    if not assets_dir.exists():
        pytest.skip("assets directory missing; ai-orchestra-simulation not synced")
    if not src_dir.exists():
        pytest.skip("src directory missing; ai-orchestra-simulation not synced")

    # Require at least one 3D asset file (glb/gltf)
    glb_files = list(assets_dir.rglob("*.glb")) + list(assets_dir.rglob("*.gltf"))
    assert glb_files, "No .glb/.gltf assets found in ai-orchestra-simulation/assets"


@pytest.mark.assets
def test_renderer_supporting_assets_present():
    """Check that avatar-service renderer sidecar files exist and are non-empty."""
    service_root = Path(__file__).resolve().parents[1]
    renderer_dir = service_root / "renderer"
    render_js = renderer_dir / "render.js"

    assert renderer_dir.exists(), "renderer directory missing"
    assert render_js.exists(), "render.js missing"
    assert render_js.stat().st_size > 4_000, "render.js unexpectedly small; check vendoring"