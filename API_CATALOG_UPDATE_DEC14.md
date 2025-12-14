# API Catalog Update — Dec 14, 2025

## Notification Service — Modular Providers
- Provider selection via `NOTIFY_PROVIDER` (novu | apprise)
- Health exposure: `GET /health` includes provider connectivity
- Planned: `GET /api/v1/provider` returns active provider and status
- Existing notification endpoints will proxy to active provider

## Frontend — Novu Inbox Integration
- Component added: `desktop-app/src/renderer/components/NotificationInbox.tsx`
- Env: `NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER` required
- Optional region overrides:
  - `NEXT_PUBLIC_NOVU_BACKEND_URL`
  - `NEXT_PUBLIC_NOVU_SOCKET_URL`

## Environment Variables
```
NOTIFY_PROVIDER=novu|apprise
NOVU_API_URL=https://api.novu.co
NOVU_API_KEY=***
APPRISE_SERVICES=mailto://alerts@example.com
NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER=A0-9w6ngNiRE
# NEXT_PUBLIC_NOVU_BACKEND_URL=https://eu.api.novu.co
# NEXT_PUBLIC_NOVU_SOCKET_URL=wss://eu.ws.novu.co
```

## Impact
- No breaking API changes
- Reduced local resource usage when SaaS enabled
- Clear path to later self-hosted Novu OSS without code changes
