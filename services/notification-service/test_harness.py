import asyncio
import os

import httpx

BASE_URL = os.getenv("NOTIFY_BASE_URL", "http://localhost:8011")

async def main():
    async with httpx.AsyncClient(timeout=5) as client:
        await client.get(f"{BASE_URL}/")

        await client.get(f"{BASE_URL}/health")

        await client.get(f"{BASE_URL}/api/v1/provider")

        payload_email = {
            "to": os.getenv("TEST_EMAIL_TO", "alerts@example.com"),
            "subject": "Test Notification",
            "html": "<strong>Hello</strong>",
            "text": "Hello"
        }
        await client.post(f"{BASE_URL}/api/v1/notify/email", json=payload_email)

        payload_sms = {
            "to": os.getenv("TEST_SMS_TO", "+10000000000"),
            "text": "Test SMS"
        }
        await client.post(f"{BASE_URL}/api/v1/notify/sms", json=payload_sms)

        payload_push = {
            "to": os.getenv("TEST_PUSH_TO", "subscriber-1"),
            "title": "Test Push",
            "body": "Push body",
            "data": {"k": "v"}
        }
        await client.post(f"{BASE_URL}/api/v1/notify/push", json=payload_push)

        await client.get(f"{BASE_URL}/api/v1/notify/templates")

if __name__ == "__main__":
    asyncio.run(main())
