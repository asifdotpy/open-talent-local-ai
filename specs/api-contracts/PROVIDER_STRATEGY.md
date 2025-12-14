# Modular Provider Strategy (SaaS-first with Local Fallback)

## Overview
This strategy enables each service (Security, Notification, AI Auditing, Analytics, Search) to plug in a provider at runtime:
- Prefer external SaaS API when available (e.g., Novu Cloud) to reduce local resource usage.
- Fall back to self-hosted open source (e.g., Novu OSS) when offline or keys are missing.
- Provide a lightweight local adapter (e.g., Apprise) for minimal installations.

## Goals
- No vendor lock-in: switch providers via environment variables
- Reduced local RAM/CPU when SaaS is used
- Consistent API surface for the Desktop Integration Gateway
- Simple deployment: zero-code config changes per environment

## Selection Mechanism
Provider selection is environment-driven:

```
# Notification Service
NOTIFY_PROVIDER=novu|novu_oss|apprise
NOVU_API_URL=https://api.novu.co
NOVU_API_KEY=***
APPRISE_SERVICES=smtps://user:pass@server;mailto://user@domain

# Security Service (future)
AUTH_PROVIDER=keycloak|ory|builtin
KEYCLOAK_URL=http://keycloak:8080

# Auditing Service (future)
AUDIT_PROVIDER=aif360|builtin
```

## Notification Service Interface

```python
class NotificationProvider:
    async def send_email(self, to: str, subject: str, html: str, text: str | None = None): ...
    async def send_sms(self, to: str, text: str): ...
    async def send_push(self, to: str, title: str, body: str, data: dict | None = None): ...
    async def get_templates(self) -> list[dict]: ...
    async def render(self, template_id: str, payload: dict) -> dict: ...
    async def preferences(self, user_id: str) -> dict: ...
    async def health(self) -> dict: ...
```

## Factory & Fallback Logic

```python
# providers/__init__.py
import os
from .novu import NovuProvider
from .local import LocalNovuProvider
from .apprise import AppriseProvider

PROVIDER = os.getenv("NOTIFY_PROVIDER", "local")

def get_provider():
    if PROVIDER == "novu":
        return NovuProvider(api_url=os.getenv("NOVU_API_URL"), api_key=os.getenv("NOVU_API_KEY"))
    if PROVIDER == "novu_oss":
        return LocalNovuProvider(base_url=os.getenv("NOVU_API_URL", "http://novu:3000"))
    if PROVIDER == "apprise":
        return AppriseProvider(services=os.getenv("APPRISE_SERVICES", ""))
    return LocalNovuProvider(base_url="http://novu:3000")
```

On provider health failure, the service should:
- return degraded status and attempt fallback (configurable)
- log incidents and expose via `/health` and `/provider` endpoints

## FastAPI Integration Pattern

```python
from fastapi import FastAPI, Depends
from providers import get_provider

app = FastAPI()

def provider_dep():
    return get_provider()

@app.post("/api/v1/notify/email")
async def notify_email(req: dict, p=Depends(provider_dep)):
    return await p.send_email(req["to"], req["subject"], req.get("html", ""), req.get("text"))
```

## Observability
- `/health`: overall service health
- `/provider`: current provider + connectivity status
- `/metrics`: request counts per provider, failure rates, fallback events

## Security Considerations
- Store API keys via secrets manager or environment variables
- Do not log sensitive payloads
- Rate-limit outbound API calls to SaaS providers
- Implement retries with exponential backoff

## Deployment Modes
- Minimal (offline): `NOTIFY_PROVIDER=apprise` (RAM ~50MB)
- Balanced (local OSS): `NOTIFY_PROVIDER=novu_oss` (RAM ~200MB)
- SaaS-first (online): `NOTIFY_PROVIDER=novu` (RAM minimal, relies on external API)

## Roadmap
- Implement Notification providers (Novu SaaS, Novu OSS, Apprise)
- Add Security provider adapters (Keycloak, Ory)
- Add Auditing adapters (AIF360 + MLflow)
- Add Health + Fallback circuit breaker
- Document `.env` examples and compose overrides
```