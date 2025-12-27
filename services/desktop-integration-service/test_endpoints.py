#!/usr/bin/env python3
"""
Quick validation test for Desktop Integration Service.
Tests all Phase 0 endpoints without requiring other services.
"""

import asyncio
import json

import httpx

BASE_URL = "http://localhost:8009"


async def test_endpoint(client: httpx.AsyncClient, name: str, method: str, url: str, **kwargs) -> dict:
    """Test a single endpoint."""
    try:
        if method == "GET":
            response = await client.get(url, **kwargs)
        elif method == "POST":
            response = await client.post(url, **kwargs)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}

        return {
            "status": "success" if response.status_code < 400 else "error",
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    """Run all endpoint tests."""

    async with httpx.AsyncClient(timeout=10.0) as client:
        tests = [
            ("Root", "GET", f"{BASE_URL}/"),
            ("Health Check", "GET", f"{BASE_URL}/health"),
            ("System Status", "GET", f"{BASE_URL}/api/v1/system/status"),
            ("List Models", "GET", f"{BASE_URL}/api/v1/models"),
            ("Dashboard", "GET", f"{BASE_URL}/api/v1/dashboard"),
            ("Start Interview", "POST", f"{BASE_URL}/api/v1/interviews/start", {
                "json": {
                    "role": "Software Engineer",
                    "model": "vetta-granite-2b-gguf-v4",
                    "totalQuestions": 3
                }
            }),
        ]

        results = []
        for name, method, url, *args in tests:
            kwargs = args[0] if args else {}

            result = await test_endpoint(client, name, method, url, **kwargs)
            results.append((name, result))

            if result["status"] == "success":
                pass
            else:
                pass

            # Print response preview
            if "response" in result:
                json.dumps(result["response"], indent=2)[:300]

        # Summary

        passed = sum(1 for _, r in results if r["status"] == "success")
        total = len(results)

        for name, result in results:
            "✅" if result["status"] == "success" else "❌"


        if passed == total:
            return 0
        else:
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
