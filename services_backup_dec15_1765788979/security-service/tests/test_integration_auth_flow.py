import os
import importlib
import httpx
from httpx import ASGITransport


def load_app():
    os.environ.setdefault("SECURITY_SECRET_KEY", "TEST_SECRET_KEY")
    os.environ.setdefault("RATE_LIMIT_ENABLED", "true")
    os.environ.setdefault("RATE_LIMIT_RULE", "5/minute")
    os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://example.com")
    if "services.security-service.main" in importlib.sys.modules:
        del importlib.sys.modules["services.security-service.main"]
    spec = importlib.util.spec_from_file_location(
        "security_service_main",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py")),
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.app


async def _register(client: httpx.AsyncClient, email: str, password: str):
    return await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
        },
        timeout=5.0,
    )


async def _login(client: httpx.AsyncClient, email: str, password: str):
    return await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=5.0,
    )


async def _logout(client: httpx.AsyncClient, token: str):
    return await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5.0,
    )


async def _refresh(client: httpx.AsyncClient, refresh_token: str):
    return await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
        timeout=5.0,
    )


async def test_cors_headers_present():
    app = load_app()
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        r = await client.get(
            "/health",
            headers={"Origin": "http://example.com"},
            timeout=5.0,
        )
        assert r.status_code == 200
        headers_lower = {k.lower(): v for k, v in r.headers.items()}
        assert "access-control-allow-origin" in headers_lower


async def test_auth_flow_and_rate_limit_behavior():
    # Ensure rate limiting is enabled and rule is strict to trigger easily
    os.environ["RATE_LIMIT_ENABLED"] = "true"
    os.environ["RATE_LIMIT_RULE"] = "5/minute"

    email = "inttest@example.com"
    password = "StrongPassw0rd!"

    app = load_app()
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Register user
        reg = await _register(client, email, password)
        assert reg.status_code in (201, 409)  # allow re-run

        # Perform multiple login attempts to reach the limit
        successes = 0
        too_many = 0
        refresh_token = None
        token = None
        for i in range(8):
            resp = await _login(client, email, password)
            if resp.status_code == 200:
                successes += 1
                data = resp.json()
                token = data.get("access_token")
                refresh_token = data.get("refresh_token")
            elif resp.status_code == 429:
                too_many += 1
            else:
                # Other codes are acceptable depending on prior state
                pass

        # Expect at least one success and at least one rate limit hit
        assert successes >= 1
        assert too_many >= 1

        if token:
            out = await _logout(client, token)
            assert out.status_code in (200, 204)

        if refresh_token:
            ref = await _refresh(client, refresh_token)
            assert ref.status_code in (200, 401)
