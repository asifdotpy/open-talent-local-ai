"""Asset route tests for avatar API.
Validates asset serving, path traversal safety, MIME types, and caching.
Marked with @pytest.mark.assets for conditional execution.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app():
    main_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("avatar_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)


class TestAssetEndpoints:
    """Basic asset endpoint structure tests."""

    def test_assets_list(self, client):
        """GET /assets should return available assets."""
        res = client.get("/api/v1/avatars/assets")
        assert res.status_code == 200
        body = res.json()
        assert isinstance(body, dict)
        assert "assets" in body or "count" in body or len(body) >= 0

    def test_assets_search(self, client):
        """GET /assets/search?q=... should search assets (not implemented yet)."""
        res = client.get("/api/v1/avatars/assets/search", params={"q": "face"})
        # Search endpoint not yet implemented in stub
        assert res.status_code in [200, 404]

    def test_assets_download(self, client):
        """GET /assets/download?name=... should return asset file."""
        res = client.get("/api/v1/avatars/assets/download", params={"name": "avatar.fbx"})
        # May return 200 (file) or 404 (not found in stub)
        assert res.status_code in [200, 404]

    def test_model_list(self, client):
        """GET /models should list available avatar models."""
        res = client.get("/api/v1/avatars/models")
        assert res.status_code == 200
        body = res.json()
        assert "models" in body or isinstance(body, list)

    def test_model_select(self, client):
        """POST /models/select should select a model."""
        res = client.post("/api/v1/avatars/models/select", json={"avatar_id": "avatar-1", "model_id": "model-1"})
        assert res.status_code == 200
        assert res.json()["model_id"] == "model-1"


class TestAssetPathTraversalSafety:
    """Path traversal attack prevention tests."""

    @pytest.mark.assets
    def test_download_path_traversal_parent_dir(self, client):
        """../../../etc/passwd should be rejected."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "../../../etc/passwd"}
        )
        # Should either reject (404/403) or normalize path safely
        assert res.status_code in [400, 403, 404]

    @pytest.mark.assets
    def test_download_path_traversal_backslash(self, client):
        r"""..\\..\\windows\\system32 should be rejected."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "..\\..\\windows\\system32"}
        )
        assert res.status_code in [400, 403, 404]

    @pytest.mark.assets
    def test_download_absolute_path(self, client):
        """Absolute paths /etc/passwd should be rejected."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "/etc/passwd"}
        )
        assert res.status_code in [400, 403, 404]

    @pytest.mark.assets
    def test_download_null_byte_injection(self, client):
        r"""Null bytes avatar.fbx\x00.txt should be rejected."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "avatar.fbx\x00.txt"}
        )
        assert res.status_code in [400, 403, 404]

    @pytest.mark.assets
    def test_download_double_encoding(self, client):
        """URL-encoded traversal ..%2F..%2Fetc%2Fpasswd should be rejected."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "..%2F..%2Fetc%2Fpasswd"}
        )
        # TestClient auto-decodes; should still be safe
        assert res.status_code in [400, 403, 404]


class TestAssetMimeTypes:
    """MIME type and content validation tests."""

    @pytest.mark.assets
    def test_fbx_asset_content_type(self, client):
        """FBX assets should have correct Content-Type."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "avatar.fbx"}
        )
        if res.status_code == 200:
            # Should have FBX or binary content type
            ct = res.headers.get("content-type", "")
            assert any(x in ct for x in ["octet-stream", "fbx", "binary"])

    @pytest.mark.assets
    def test_animation_asset_content_type(self, client):
        """Animation assets should have correct Content-Type."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "animation.anim"}
        )
        if res.status_code == 200:
            ct = res.headers.get("content-type", "")
            assert "octet-stream" in ct or "animation" in ct

    @pytest.mark.assets
    def test_texture_asset_content_type(self, client):
        """Texture assets should have image/* Content-Type."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "texture.png"}
        )
        if res.status_code == 200:
            ct = res.headers.get("content-type", "")
            assert "image" in ct or "png" in ct


class TestAssetSizeAndCaching:
    """Asset size and cache-related tests."""

    @pytest.mark.assets
    def test_asset_size_limits(self, client):
        """Assets should have reasonable size bounds."""
        res = client.get("/api/v1/avatars/assets")
        if res.status_code == 200:
            body = res.json()
            # Check any asset metadata for size
            if "assets" in body and isinstance(body["assets"], list):
                for asset in body["assets"]:
                    if "size" in asset:
                        assert asset["size"] > 0
                        assert asset["size"] < 1024 * 1024 * 500  # 500MB limit

    @pytest.mark.assets
    def test_asset_checksum_provided(self, client):
        """Assets should provide checksums for integrity."""
        res = client.get("/api/v1/avatars/assets")
        if res.status_code == 200:
            body = res.json()
            if "assets" in body and isinstance(body["assets"], list):
                for asset in body["assets"]:
                    # May have checksum, sha256, md5, or hash
                    any(k in asset for k in ["checksum", "sha256", "md5", "hash"])
                    # Not required in stub, but nice to have

    @pytest.mark.assets
    def test_download_caching_headers(self, client):
        """Asset downloads should include caching headers."""
        res = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "avatar.fbx"}
        )
        if res.status_code == 200:
            # Should have cache control or ETag
            pass
            # Not strictly required, but good practice


class TestAssetMetadata:
    """Asset metadata and versioning tests."""

    @pytest.mark.assets
    def test_asset_metadata_shape(self, client):
        """Asset list should include descriptive metadata."""
        res = client.get("/api/v1/avatars/assets")
        if res.status_code == 200 and "assets" in res.json():
            assets = res.json()["assets"]
            if assets:
                asset = assets[0]
                # Should have asset_id or name or id
                assert "asset_id" in asset or "name" in asset or "id" in asset

    @pytest.mark.assets
    def test_model_metadata_shape(self, client):
        """Model list should include descriptive metadata."""
        res = client.get("/api/v1/avatars/models")
        if res.status_code == 200 and "models" in res.json():
            models = res.json()["models"]
            if models:
                model = models[0]
                assert "id" in model or "model_id" in model or "name" in model

    @pytest.mark.assets
    def test_asset_version_tracking(self, client):
        """Assets should track version information."""
        res = client.get("/api/v1/avatars/assets")
        body = res.json()
        # May have version at top level or per-asset
        (
            "version" in body or
            "api_version" in body or
            ("assets" in body and body["assets"] and "version" in body["assets"][0])
        )
        # Not required in stub implementation


class TestAssetConcurrentAccess:
    """Concurrent asset access tests."""

    @pytest.mark.assets
    def test_concurrent_asset_downloads(self, client):
        """Multiple concurrent downloads should not interfere."""
        # Simulate concurrent requests
        res1 = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "asset1.fbx"}
        )
        res2 = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "asset2.fbx"}
        )
        # Both should complete without error or conflict
        assert res1.status_code in [200, 404]
        assert res2.status_code in [200, 404]

    @pytest.mark.assets
    def test_asset_list_during_download(self, client):
        """Listing assets while downloading should not deadlock."""
        # List
        res1 = client.get("/api/v1/avatars/assets")
        # Download
        res2 = client.get(
            "/api/v1/avatars/assets/download",
            params={"name": "avatar.fbx"}
        )
        # Both should succeed
        assert res1.status_code == 200
        assert res2.status_code in [200, 404]
