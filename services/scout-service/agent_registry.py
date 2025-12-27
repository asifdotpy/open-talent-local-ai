"""Agent Registry and Discovery Module
Handles agent discovery, metadata management, and health monitoring.

Author: OpenTalent Team
Updated: December 13, 2025
"""

import asyncio
import contextlib
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path

import aiohttp
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# ============================
# Models
# ============================


class AgentStatus(str, Enum):
    """Agent health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


class AgentMetadata(BaseModel):
    """Agent metadata and configuration."""

    name: str = Field(..., description="Agent name (e.g., 'scout-coordinator-agent')")
    port: int = Field(..., description="Port the agent runs on")
    url: str = Field(..., description="Full URL for agent API")
    purpose: str = Field(..., description="Agent's primary purpose")
    capabilities: list[str] = Field(default_factory=list, description="List of capabilities")
    status: AgentStatus = Field(default=AgentStatus.UNKNOWN, description="Current health status")
    last_health_check: datetime | None = Field(None, description="Last health check timestamp")
    endpoints: list[str] = Field(default_factory=list, description="Available endpoints")
    venv_path: str | None = Field(None, description="Path to virtual environment")
    requires_python_version: str | None = Field(None, description="Required Python version")

    class Config:
        use_enum_values = True


# ============================
# Agent Registry
# ============================


class AgentRegistry:
    """Manages agent discovery, metadata, and health monitoring."""

    # Agent configuration: name -> (port, purpose, capabilities)
    AGENT_CONFIG = {
        "scout-coordinator-agent": {
            "port": 8090,
            "purpose": "Orchestrates intelligent talent sourcing workflow across specialized agents",
            "capabilities": ["coordination", "workflow", "orchestration"],
        },
        "proactive-scanning-agent": {
            "port": 8091,
            "purpose": "Proactive candidate identification and monitoring",
            "capabilities": ["scanning", "monitoring", "identification"],
        },
        "boolean-mastery-agent": {
            "port": 8092,
            "purpose": "Boolean query optimization and search refinement",
            "capabilities": ["search", "query-optimization", "refinement"],
        },
        "personalized-engagement-agent": {
            "port": 8093,
            "purpose": "Personalized candidate engagement and outreach",
            "capabilities": ["engagement", "outreach", "personalization"],
        },
        "market-intelligence-agent": {
            "port": 8094,
            "purpose": "Market and industry intelligence gathering",
            "capabilities": ["market-research", "intelligence", "analysis"],
        },
        "tool-leverage-agent": {
            "port": 8095,
            "purpose": "Tool and skill optimization for talent matching",
            "capabilities": ["tool-optimization", "matching", "skill-assessment"],
        },
        "quality-focused-agent": {
            "port": 8096,
            "purpose": "Quality assurance and candidate assessment",
            "capabilities": ["quality-assurance", "assessment", "validation"],
        },
        "data-enrichment-agent": {
            "port": 8097,
            "purpose": "Profile enrichment with free/paid vendor APIs",
            "capabilities": ["enrichment", "data-collection", "validation"],
        },
        "interviewer-agent": {
            "port": 8080,
            "purpose": "Interview orchestration and candidate evaluation",
            "capabilities": ["interview", "evaluation", "assessment"],
        },
    }

    def __init__(self, host: str = "localhost", agents_path: str | None = None):
        """Initialize agent registry.

        Args:
            host: Host where agents are running (default: localhost)
            agents_path: Path to agents directory for venv discovery
        """
        self.host = host
        self.agents_path = (
            Path(agents_path) if agents_path else Path("/home/asif1/open-talent/agents")
        )
        self.agents: dict[str, AgentMetadata] = {}
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self._session: aiohttp.ClientSession | None = None
        self._health_check_task: asyncio.Task | None = None

    async def init_session(self):
        """Initialize aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        logger.info("Agent registry session initialized")

    async def close_session(self):
        """Close aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
        logger.info("Agent registry session closed")

    async def discover_agents(self) -> dict[str, AgentMetadata]:
        """Discover and initialize all agents from the predefined configuration.

        Scans the `AGENT_CONFIG` mapping and hydrates `AgentMetadata` objects
        for each service, including virtual environment and version detection.

        Returns:
            A dictionary mapping agent names to their initialized metadata.
        """
        logger.info(f"Discovering agents from config ({len(self.AGENT_CONFIG)} configured)")

        for agent_name, config in self.AGENT_CONFIG.items():
            try:
                # Get Python version requirement if available
                python_version = self._get_agent_python_version(agent_name)

                # Create agent metadata
                agent = AgentMetadata(
                    name=agent_name,
                    port=config["port"],
                    url=f"http://{self.host}:{config['port']}",
                    purpose=config["purpose"],
                    capabilities=config["capabilities"],
                    status=AgentStatus.UNKNOWN,
                    venv_path=self._get_venv_path(agent_name),
                    requires_python_version=python_version,
                    endpoints=[],  # Will be populated by health check
                )

                self.agents[agent_name] = agent
                logger.info(f"✓ Discovered agent: {agent_name} (port {config['port']})")

            except Exception as e:
                logger.error(f"✗ Failed to discover agent {agent_name}: {e}")

        logger.info(f"Agent discovery complete: {len(self.agents)} agents found")
        return self.agents

    def _get_venv_path(self, agent_name: str) -> str | None:
        """Locate the virtual environment for a specific agent.

        Args:
            agent_name: Unique identifier for the agent service.

        Returns:
            The absolute path to the venv directory, or None if not found.
        """
        venv_path = self.agents_path / agent_name / ".venv"
        if venv_path.exists():
            return str(venv_path)

        # Try alternative venv location
        venv_path = self.agents_path / agent_name / "venv"
        if venv_path.exists():
            return str(venv_path)

        return None

    def _get_agent_python_version(self, agent_name: str) -> str | None:
        """Detect the required Python version by inspecting the agent's main script.

        Args:
            agent_name: Unique identifier for the agent service.

        Returns:
            A string representing the required version (e.g., '3.12'), or None.
        """
        agent_path = self.agents_path / agent_name / "main.py"

        if not agent_path.exists():
            return None

        try:
            with open(agent_path) as f:
                content = f.read()

            # Check for Python version comments
            if "Python 3.12" in content or "python3.12" in content:
                return "3.12"
            elif "Python 3.13" in content or "python3.13" in content:
                return "3.13"

        except Exception as e:
            logger.debug(f"Could not read python version from {agent_name}: {e}")

        return None

    async def check_agent_health(self, agent_name: str) -> AgentStatus:
        """Perform a network-based health check on a specific agent.

        Args:
            agent_name: Unique identifier for the agent service.

        Returns:
            The detected health status (HEALTHY, UNHEALTHY, or UNREACHABLE).
        """
        if agent_name not in self.agents:
            logger.warning(f"Agent {agent_name} not found in registry")
            return AgentStatus.UNKNOWN

        agent = self.agents[agent_name]

        try:
            if not self._session:
                await self.init_session()

            health_url = f"{agent.url}/health"
            async with self._session.get(health_url, timeout=self.health_check_timeout) as response:
                if response.status == 200:
                    agent.status = AgentStatus.HEALTHY
                    agent.last_health_check = datetime.now()
                    logger.debug(f"✓ {agent_name} is healthy")
                    return AgentStatus.HEALTHY
                else:
                    agent.status = AgentStatus.UNHEALTHY
                    agent.last_health_check = datetime.now()
                    logger.warning(f"✗ {agent_name} returned status {response.status}")
                    return AgentStatus.UNHEALTHY

        except TimeoutError:
            agent.status = AgentStatus.UNREACHABLE
            agent.last_health_check = datetime.now()
            logger.warning(f"✗ {agent_name} health check timed out")
            return AgentStatus.UNREACHABLE
        except Exception as e:
            agent.status = AgentStatus.UNREACHABLE
            agent.last_health_check = datetime.now()
            logger.warning(f"✗ {agent_name} health check failed: {e}")
            return AgentStatus.UNREACHABLE

    async def check_all_agents_health(self) -> dict[str, AgentStatus]:
        """Check the health status of all registered agents in parallel.

        Returns:
            A dictionary mapping agent names to their detected AgentStatus.
        """
        logger.info("Starting health check for all agents")

        tasks = [self.check_agent_health(name) for name in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_status = {}
        for agent_name, result in zip(self.agents.keys(), results, strict=False):
            if isinstance(result, Exception):
                health_status[agent_name] = AgentStatus.UNREACHABLE
                logger.error(f"Error checking {agent_name}: {result}")
            else:
                health_status[agent_name] = result

        logger.info(
            f"Health check complete: {sum(1 for s in health_status.values() if s == AgentStatus.HEALTHY)}/{len(health_status)} agents healthy"
        )
        return health_status

    async def start_health_monitoring(self):
        """Start background health monitoring task."""
        if self._health_check_task and not self._health_check_task.done():
            logger.warning("Health monitoring task already running")
            return

        logger.info("Starting background health monitoring")
        self._health_check_task = asyncio.create_task(self._health_monitor_loop())

    async def stop_health_monitoring(self):
        """Stop background health monitoring task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_check_task
            logger.info("Health monitoring stopped")

    async def _health_monitor_loop(self):
        """Background health monitoring loop."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self.check_all_agents_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")

    def get_agent(self, agent_name: str) -> AgentMetadata | None:
        """Retrieve the metadata for a specific agent by its name.

        Args:
            agent_name: Unique identifier for the agent service.

        Returns:
            An AgentMetadata object if found, otherwise None.
        """
        return self.agents.get(agent_name)

    def get_agents_by_capability(self, capability: str) -> list[AgentMetadata]:
        """Find all registered agents that advertise a specific capability.

        Args:
            capability: The capability to filter by (e.g., 'search', 'enrichment').

        Returns:
            A list of AgentMetadata objects matching the capability.
        """
        return [agent for agent in self.agents.values() if capability in agent.capabilities]

    def get_healthy_agents(self) -> list[AgentMetadata]:
        """Retrieve a list of all agents currently marked as healthy.

        Returns:
            A list of AgentMetadata objects with status AgentStatus.HEALTHY.
        """
        return [agent for agent in self.agents.values() if agent.status == AgentStatus.HEALTHY]

    def get_all_agents(self) -> list[AgentMetadata]:
        """Get all registered agents."""
        return list(self.agents.values())

    def get_agents_by_status(self, status: AgentStatus) -> list[AgentMetadata]:
        """Retrieve a list of agents filtered by a specific health status.

        Args:
            status: The AgentStatus to filter by.

        Returns:
            A list of AgentMetadata objects matching the status.
        """
        return [agent for agent in self.agents.values() if agent.status == status]

    async def call_agent(
        self,
        agent_name: str,
        endpoint: str,
        method: str = "GET",
        data: dict | None = None,
        params: dict | None = None,
    ) -> tuple[int, dict | None]:
        """Invoke a specific endpoint on a target agent via the registry's session.

        Args:
            agent_name: Unique identifier for the agent service.
            endpoint: API path to call (e.g., '/search').
            method: HTTP method to use (defaults to 'GET').
            data: Optional dictionary for the request body.
            params: Optional dictionary for query parameters.

        Returns:
            A tuple containing the HTTP status code and the response data dictionary.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            logger.error(f"Agent {agent_name} not found")
            return 404, None

        if agent.status != AgentStatus.HEALTHY:
            logger.warning(f"Agent {agent_name} is not healthy (status: {agent.status})")
            return 503, None

        try:
            if not self._session:
                await self.init_session()

            url = f"{agent.url}{endpoint}"

            async with self._session.request(
                method=method, url=url, json=data, params=params, timeout=30
            ) as response:
                response_data = None
                if response.status in [200, 201]:
                    response_data = await response.json()

                return response.status, response_data

        except TimeoutError:
            logger.error(f"Call to {agent_name}{endpoint} timed out")
            return 504, None
        except Exception as e:
            logger.error(f"Error calling {agent_name}{endpoint}: {e}")
            return 500, None


# ============================
# Singleton Instance
# ============================

_registry_instance: AgentRegistry | None = None


def get_agent_registry(host: str = "localhost", agents_path: str | None = None) -> AgentRegistry:
    """Get or create agent registry instance."""
    global _registry_instance

    if _registry_instance is None:
        _registry_instance = AgentRegistry(host=host, agents_path=agents_path)

    return _registry_instance
