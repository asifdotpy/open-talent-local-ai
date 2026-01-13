from typing import Optional, Dict, List


class NotificationProvider:
    async def send_email(
        self, to: str, subject: str, html: str, text: Optional[str] = None
    ) -> Dict:
        raise NotImplementedError

    async def send_sms(self, to: str, text: str) -> Dict:
        raise NotImplementedError

    async def send_push(self, to: str, title: str, body: str, data: Optional[Dict] = None) -> Dict:
        raise NotImplementedError

    async def get_templates(self) -> List[Dict]:
        raise NotImplementedError

    async def render(self, template_id: str, payload: Dict) -> Dict:
        raise NotImplementedError

    async def preferences(self, user_id: str) -> Dict:
        raise NotImplementedError

    async def health(self) -> Dict:
        raise NotImplementedError
