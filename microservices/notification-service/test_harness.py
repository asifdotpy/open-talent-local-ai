import asyncio
import os
import json
import httpx

BASE_URL = os.getenv("NOTIFY_BASE_URL", "http://localhost:8011")

async def main():
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{BASE_URL}/")
        print("ROOT:", r.status_code, r.json())

        r = await client.get(f"{BASE_URL}/health")
        print("HEALTH:", r.status_code, r.json())

        r = await client.get(f"{BASE_URL}/api/v1/provider")
        print("PROVIDER:", r.status_code, r.json())

        payload_email = {
            "to": os.getenv("TEST_EMAIL_TO", "alerts@example.com"),
            "subject": "Test Notification",
            "html": "<strong>Hello</strong>",
            "text": "Hello"
        }
        r = await client.post(f"{BASE_URL}/api/v1/notify/email", json=payload_email)
        print("EMAIL:", r.status_code, r.json())

        payload_sms = {
            "to": os.getenv("TEST_SMS_TO", "+10000000000"),
            "text": "Test SMS"
        }
        r = await client.post(f"{BASE_URL}/api/v1/notify/sms", json=payload_sms)
        print("SMS:", r.status_code, r.json())

        payload_push = {
            "to": os.getenv("TEST_PUSH_TO", "subscriber-1"),
            "title": "Test Push",
            "body": "Push body",
            "data": {"k": "v"}
        }
        r = await client.post(f"{BASE_URL}/api/v1/notify/push", json=payload_push)
        print("PUSH:", r.status_code, r.json())

        r = await client.get(f"{BASE_URL}/api/v1/notify/templates")
        print("TEMPLATES:", r.status_code, r.json())

if __name__ == "__main__":
    asyncio.run(main())
