"""Service discovery and health monitoring."""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ServiceHealthCache:
    """Simple in-memory cache for service health checks."""

    def __init__(self, ttl_seconds: int = 5):
        self.ttl = ttl_seconds
        self.cached_result = None
        self.cache_time = None

    def get(self) -> Optional[Dict]:
        """Get cached health result if not expired."""
        if self.cached_result and self.cache_time:
            elapsed = (datetime.now() - self.cache_time).total_seconds()
            if elapsed < self.ttl:
                return self.cached_result
        return None

    def set(self, result: Dict):
        """Cache health result."""
        self.cached_result = result
        self.cache_time = datetime.now()


class ServiceDiscovery:
    """Discover and monitor microservice health."""

    def __init__(self):
        self.services = {
            "conversation-service": settings.conversation_url,
            "voice-service": settings.voice_url,
            "avatar-service": settings.avatar_url,
            "interview-service": settings.interview_url,
            "analytics-service": settings.analytics_url,
            "granite-interview-service": settings.granite_interview_url,
            "ollama": settings.ollama_url,
        }
        self.health_cache = ServiceHealthCache(ttl_seconds=settings.health_cache_ttl)

    async def check_all_services(self) -> Dict:
        """Check health of all services. Returns cached result if not expired."""
        # Try cache first
        cached = self.health_cache.get()
        if cached:
            return cached

        # Perform new health checks
        result = await self._perform_health_checks()
        self.health_cache.set(result)
        return result

    async def _perform_health_checks(self) -> Dict:
        """Actually perform health checks on all services."""
        tasks = [
            self._check_service(name, url)
            for name, url in self.services.items()
        ]
        service_statuses = await asyncio.gather(*tasks, return_exceptions=False)

        status_dict = {
            status["name"]: status
            for status in service_statuses
        }

        # Calculate overall status
        online_count = sum(1 for s in status_dict.values() if s["status"] == "online")
        total_count = len(status_dict)

        if online_count >= 6:
            overall_status = "online"
        elif online_count >= 3:
            overall_status = "degraded"
        else:
            overall_status = "offline"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": status_dict,
            "summary": {
                "online": online_count,
                "total": total_count,
                "percentage": round(online_count / total_count * 100, 1) if total_count > 0 else 0,
            },
        }

    async def _check_service(self, name: str, url: str) -> Dict:
        """Check health of a single service."""
        start_time = datetime.now()

        try:
            # Determine correct health endpoint
            # Ollama doesn't have /api/health, use /api/tags instead
            if "ollama" in name.lower():
                health_url = f"{url}/api/tags"
            else:
                health_url = f"{url}/health"

            async with httpx.AsyncClient(timeout=settings.health_check_timeout) as client:
                response = await client.get(health_url)

            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                status = "online"
            else:
                status = "degraded"

            return {
                "name": name,
                "url": url,
                "status": status,
                "latencyMs": round(latency_ms, 1),
                "lastChecked": datetime.now().isoformat(),
            }

        except asyncio.TimeoutError:
            return {
                "name": name,
                "url": url,
                "status": "offline",
                "error": "timeout",
                "lastChecked": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.warning(f"Health check failed for {name}: {str(e)}")
            return {
                "name": name,
                "url": url,
                "status": "offline",
                "error": str(e),
                "lastChecked": datetime.now().isoformat(),
            }

    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get URL for a service if it's healthy."""
        health = await self.check_all_services()
        service_status = health["services"].get(service_name)

        if service_status and service_status["status"] in ["online", "degraded"]:
            return self.services.get(service_name)

        return None
