import importlib
import importlib.util
import os

import httpx
from httpx import ASGITransport


def reload_security_module(env: dict | None = None):
    # Allow tests to inject env for PEPPER/BCRYPT_ROUNDS
    if env:
        for k, v in env.items():
            os.environ[k] = str(v)
    # Disable rate limiting for hashing unit tests
    os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
    if "services.security-service.main" in list(importlib.sys.modules.keys()):
        importlib.invalidate_caches()
        del importlib.sys.modules["services.security-service.main"]
    # Module path uses hyphen in folder name; import via relative path alias
    spec = importlib.util.spec_from_file_location(
        "security_service_main",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py")),
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_bcrypt_hash_and_verify_default_rounds():
    mod = reload_security_module({"BCRYPT_ROUNDS": "12", "PEPPER": ""})
    pw = "StrongPassw0rd!"
    h = mod.hash_password(pw)
    assert h.startswith("$2"), "Expected bcrypt hash prefix"
    assert mod.verify_password(pw, h) is True
    assert mod.verify_password("wrong", h) is False


def test_bcrypt_with_pepper_changes_hash_and_verification():
    pw = "AnotherStrong1!"
    mod_no_pepper = reload_security_module({"BCRYPT_ROUNDS": "12", "PEPPER": ""})
    h1 = mod_no_pepper.hash_password(pw)
    mod_peppered = reload_security_module({"BCRYPT_ROUNDS": "12", "PEPPER": "pepper123"})
    h2 = mod_peppered.hash_password(pw)
    assert h1 != h2, "Pepper should change resulting hash"
    assert mod_peppered.verify_password(pw, h2) is True
    assert (
        mod_peppered.verify_password(pw, h1) is False
    ), "Hash generated without pepper should not verify with pepper"


def test_legacy_sha256_verification_still_supported():
    mod = reload_security_module({"PEPPER": ""})
    legacy_hash = mod.sha256(b"LegacyPass123!").hexdigest()
    assert mod.verify_password("LegacyPass123!", legacy_hash) is True
    assert mod.verify_password("wrong", legacy_hash) is False


def test_login_migrates_legacy_hash_to_bcrypt(tmp_path, monkeypatch):
    mod = reload_security_module({"BCRYPT_ROUNDS": "12", "PEPPER": ""})

    # Prepare a test user with legacy hash
    email = "legacy@example.com"
    password = "LegacyPass123!"
    mod.users_db[email] = {
        "email": email,
        "password_hash": mod.sha256(password.encode()).hexdigest(),
        "first_name": "Legacy",
        "last_name": "User",
        "roles": ["user"],
        "permissions": [],
        "mfa_enabled": False,
        "mfa_secret": None,
    }

    # Simulate FastAPI handler call through ASGI client to supply a real Request object
    import asyncio

    async def _login_via_client():
        transport = ASGITransport(app=mod.app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver", timeout=5.0
        ) as client:
            return await client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password},
            )

    resp = asyncio.get_event_loop().run_until_complete(_login_via_client())
    assert resp.status_code == 200

    # After successful login, password should be migrated to bcrypt
    new_hash = mod.users_db[email]["password_hash"]
    assert new_hash.startswith("$2"), "Expected bcrypt hash after migration"
    assert mod.verify_password(password, new_hash) is True
