class NotificationProvider:
    async def send_email(self, to: str, subject: str, html: str, text: str | None = None) -> dict:
        raise NotImplementedError

    async def send_sms(self, to: str, text: str) -> dict:
        raise NotImplementedError

    async def send_push(self, to: str, title: str, body: str, data: dict | None = None) -> dict:
        raise NotImplementedError

    async def get_templates(self) -> list[dict]:
        raise NotImplementedError

    async def render(self, template_id: str, payload: dict) -> dict:
        raise NotImplementedError

    async def preferences(self, user_id: str) -> dict:
        raise NotImplementedError

    async def health(self) -> dict:
        raise NotImplementedError
