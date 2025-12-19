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
        # All 14 OpenTalent Microservices + Ollama AI Engine
        base_services = {
            # Core Services (3)
            "scout-service": settings.scout_url,
            "user-service": settings.user_url,
            "candidate-service": settings.candidate_url,
            
            # AI & Conversation Services (3)
            "_granite-interview-service": settings.granite_interview_url,  # Hidden from UI
            "conversation-service": settings.conversation_url,
            "interview-service": settings.interview_url,
            
            # Voice & Avatar Services (2)
            "voice-service": settings.voice_url,
            "avatar-service": settings.avatar_url,
            
            # Analytics & Monitoring Services (4)
            "analytics-service": settings.analytics_url,
            "security-service": settings.security_url,
            "notification-service": settings.notification_url,
            "ai-auditing-service": settings.ai_auditing_url,
            
            # Explainability Service (1)
            "explainability-service": settings.explainability_url,
            
            # AI Model Engine
            "ollama": settings.ollama_url,
        }

        optional_services = {}
        if settings.enable_agents and settings.agents_url:
            optional_services["agents-service"] = settings.agents_url

        self.services = {**base_services, **optional_services}
        self.health_cache = ServiceHealthCache(ttl_seconds=settings.health_cache_ttl)
        
        logger.info(f"Initialized service discovery with {len(self.services)} services: "
                   f"{', '.join([s for s in self.services.keys() if not s.startswith('_')])}")

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

        # Calculate overall status (excluding hidden services)
        visible_statuses = {k: v for k, v in status_dict.items() if not k.startswith("_")}
        online_count = sum(1 for s in visible_statuses.values() if s["status"] == "online")
        total_count = len(visible_statuses)
        
        # Check if critical services are online
        ollama_online = status_dict.get("ollama", {}).get("status") == "online"

        if online_count >= 6:
            overall_status = "online"
        elif online_count >= 3 or ollama_online:
            # At least degraded if 3+ services OR Ollama is online (critical for interviews)
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
