from typing import Dict, Optional, List
from .base import NotificationProvider

try:
    import apprise
except Exception:  # Apprise optional
    apprise = None


class AppriseProvider(NotificationProvider):
    def __init__(self, services: str = ""):
        self.services = services
        self.app = apprise.Apprise() if apprise else None
        if self.app and services:
            for url in services.split(";"):
                if url.strip():
                    self.app.add(url.strip())

    async def send_email(
        self, to: str, subject: str, html: str, text: Optional[str] = None
    ) -> Dict:
        if not self.app:
            return {"ok": False, "error": "Apprise not installed"}
        ok = self.app.notify(body=text or html, title=subject)
        return {"ok": ok}

    async def send_sms(self, to: str, text: str) -> Dict:
        if not self.app:
            return {"ok": False, "error": "Apprise not installed"}
        ok = self.app.notify(body=text)
        return {"ok": ok}

    async def send_push(self, to: str, title: str, body: str, data: Optional[Dict] = None) -> Dict:
        if not self.app:
            return {"ok": False, "error": "Apprise not installed"}
        ok = self.app.notify(body=body, title=title)
        return {"ok": ok}

    async def get_templates(self) -> List[Dict]:
        return []

    async def render(self, template_id: str, payload: Dict) -> Dict:
        return {"template_id": template_id, "payload": payload}

    async def preferences(self, user_id: str) -> Dict:
        return {"user_id": user_id, "channels": {"email": True, "sms": True, "push": True}}

    async def health(self) -> Dict:
        return {"provider": "apprise", "ok": self.app is not None}
