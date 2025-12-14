# OpenAPI Verification — Update (Dec 14, 2025)

## Notification Service
New/updated endpoints introduced for modular provider strategy:
- GET /api/v1/provider — active provider + connectivity
- GET /health — includes provider-specific health info
- POST /api/v1/notify/email — proxies to provider
- POST /api/v1/notify/sms — proxies to provider
- POST /api/v1/notify/push — proxies to provider
- GET /api/v1/notify/templates — provider templates

## Frontend
- Novu Inbox component added at desktop-app/src/renderer/components/NotificationInbox.tsx using NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER
