import asyncio

import httpx

SERVICES = {
    8001: "user-service",
    8002: "conversation-service",
    8004: "avatar-service",
    8005: "interview-service",
    8006: "candidate-service",
    8007: "project-service",
    8008: "granite-interview",
    8009: "desktop-integration",
    8010: "security-service",
    8011: "notification-service",
    8012: "analytics-service",
    8013: "scout-service",
    8014: "ai-auditing-service",
    8015: "voice-service",
    8016: "explainability",
    8017: "voice-webrtc-worker",
}


async def check_service(port, name):
    url = f"http://127.0.0.1:{port}/health"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                print(f"[PASSED] {name:<20} (Port {port}): {response.json().get('status', 'OK')}")
                return True
            else:
                print(f"[FAILED] {name:<20} (Port {port}): Status {response.status_code}")
    except Exception:
        # Try root if /health fails
        url = f"http://127.0.0.1:{port}/"
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.get(url)
                print(f"[PASSED] {name:<20} (Port {port}): Root reachable")
                return True
        except Exception:
            print(f"[DOWN  ] {name:<20} (Port {port}): Unreachable")
    return False


async def main():
    print(f"{'=' * 60}")
    print(f"{'OpenTalent Service Health Sweep':^60}")
    print(f"{'=' * 60}")

    tasks = [check_service(port, name) for port, name in SERVICES.items()]
    results = await asyncio.gather(*tasks)

    alive = sum(1 for r in results if r)
    total = len(SERVICES)

    print(f"{'=' * 60}")
    print(f"Summary: {alive}/{total} services are reachable.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
