import os

import aiohttp

from .base import NotificationProvider


class NovuProvider(NotificationProvider):
    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        self.api_url = api_url or os.getenv("NOVU_API_URL", "https://api.novu.co")
        self.api_key = api_key or os.getenv("NOVU_API_KEY", "")
        self.headers = {
            "Authorization": f"ApiKey {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _post(self, path: str, json: dict) -> dict:
        async with (
            aiohttp.ClientSession() as session,
            session.post(f"{self.api_url}{path}", headers=self.headers, json=json) as resp,
        ):
            return {"status": resp.status, "data": await resp.json()}

    async def send_email(self, to: str, subject: str, html: str, text: str | None = None) -> dict:
        payload = {"to": {"email": to}, "subject": subject, "html": html, "text": text or ""}
        return await self._post("/v1/events/trigger", {"name": "email", "payload": payload})

    async def send_sms(self, to: str, text: str) -> dict:
        payload = {"to": {"phone": to}, "text": text}
        return await self._post("/v1/events/trigger", {"name": "sms", "payload": payload})

    async def send_push(self, to: str, title: str, body: str, data: dict | None = None) -> dict:
        payload = {"to": {"subscriberId": to}, "title": title, "body": body, "data": data or {}}
        return await self._post("/v1/events/trigger", {"name": "push", "payload": payload})

    async def get_templates(self) -> list[dict]:
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"{self.api_url}/v1/notification-templates", headers=self.headers) as resp,
        ):
            data = await resp.json()
            return data.get("data", [])

    async def render(self, template_id: str, payload: dict) -> dict:
        return {"template_id": template_id, "payload": payload}

    async def preferences(self, user_id: str) -> dict:
        return {"user_id": user_id, "channels": {"email": True, "sms": False, "push": True}}

    async def health(self) -> dict:
        try:
            templates = await self.get_templates()
            return {"provider": "novu", "ok": True, "templates": len(templates)}
        except Exception as e:
            return {"provider": "novu", "ok": False, "error": str(e)}
