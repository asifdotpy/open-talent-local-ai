# Provider Configuration Guide

This guide shows how to configure OpenTalent to use external SaaS APIs (to reduce local resource usage) with seamless local fallbacks.

## Notification Service

### Choose a Provider
- Novu SaaS (recommended when online): `NOTIFY_PROVIDER=novu`
- Apprise (lightweight local): `NOTIFY_PROVIDER=apprise`

### Environment Variables
```
# Novu SaaS
NOTIFY_PROVIDER=novu
NOVU_API_URL=https://api.novu.co
NOVU_API_KEY=YOUR_NOVU_API_KEY

# Apprise local (fallback/offline)
# NOTIFY_PROVIDER=apprise
# APPRISE_SERVICES=mailto://alerts@example.com;smtps://user:pass@smtp.example.com
```

### Health & Fallback
- `/health` returns provider status
- `/provider` returns active provider and connectivity
- On SaaS failure, the service can be configured to fall back to Apprise

## Future Providers
- Security: Keycloak/Ory via `AUTH_PROVIDER`
- Auditing: AIF360 via `AUDIT_PROVIDER`

## Notes
- Store secrets securely (env, secret manager)
- Avoid logging sensitive payloads
- Rate limit outbound SaaS calls; use retries with backoff
