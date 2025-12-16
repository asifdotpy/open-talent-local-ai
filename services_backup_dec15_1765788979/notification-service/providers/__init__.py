import os
import asyncio
from .novu import NovuProvider
from .apprise import AppriseProvider
from .base import NotificationProvider

RETRY_ATTEMPTS = int(os.getenv("NOTIFY_RETRY_ATTEMPTS", "2"))
RETRY_BACKOFF_SEC = float(os.getenv("NOTIFY_RETRY_BACKOFF_SEC", "0.3"))

class FallbackProvider(NotificationProvider):
    def __init__(self, primary: NotificationProvider, fallback: NotificationProvider):
        self.primary = primary
        self.fallback = fallback

    async def _try(self, func_name: str, *args, **kwargs):
        last_error = None
        for attempt in range(RETRY_ATTEMPTS):
            try:
                func = getattr(self.primary, func_name)
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = str(e)
                await asyncio.sleep(RETRY_BACKOFF_SEC)
        # Fallback
        func = getattr(self.fallback, func_name)
        result = await func(*args, **kwargs)
        # Annotate result to indicate fallback occurred
        if isinstance(result, dict):
            result.setdefault("fallback", True)
            result.setdefault("fallback_reason", last_error)
        return result

    async def send_email(self, *args, **kwargs):
        return await self._try("send_email", *args, **kwargs)

    async def send_sms(self, *args, **kwargs):
        return await self._try("send_sms", *args, **kwargs)

    async def send_push(self, *args, **kwargs):
        return await self._try("send_push", *args, **kwargs)

    async def get_templates(self, *args, **kwargs):
        return await self._try("get_templates", *args, **kwargs)

    async def render(self, *args, **kwargs):
        return await self._try("render", *args, **kwargs)

    async def preferences(self, *args, **kwargs):
        return await self._try("preferences", *args, **kwargs)

    async def health(self):
        try:
            status = await self.primary.health()
            return {"active": "primary", **status}
        except Exception as e:
            fb = await self.fallback.health()
            return {"active": "fallback", "error": str(e), **fb}

def get_provider() -> NotificationProvider:
    provider = os.getenv("NOTIFY_PROVIDER", "apprise").lower()
    primary: NotificationProvider
    if provider == "novu":
        primary = NovuProvider()
    else:
        primary = AppriseProvider(services=os.getenv("APPRISE_SERVICES", ""))
    fallback = AppriseProvider(services=os.getenv("APPRISE_SERVICES", ""))
    return FallbackProvider(primary=primary, fallback=fallback)
