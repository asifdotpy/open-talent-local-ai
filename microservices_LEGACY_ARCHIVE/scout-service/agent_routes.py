"""
Agent Routing Module
Handles request routing to appropriate agents

Author: OpenTalent Team
Updated: December 13, 2025
"""

import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from agent_registry import AgentRegistry, AgentMetadata

logger = logging.getLogger(__name__)

# ============================
# Models
# ============================


class AgentRequest(BaseModel):
    """Request routed to an agent"""

    agent_name: Optional[str] = Field(None, description="Specific agent to route to")
    capability: Optional[str] = Field(None, description="Required capability")
    endpoint: str = Field(..., description="Agent endpoint to call")
    method: str = Field(default="POST", description="HTTP method")
    payload: Optional[Dict[str, Any]] = Field(None, description="Request payload")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")


class AgentResponse(BaseModel):
    """Response from an agent"""

    agent_name: str
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class MultiAgentResponse(BaseModel):
    """Response from multiple agents"""

    requested_agents: List[str]
    responses: List[AgentResponse]
    total_execution_time_ms: Optional[float] = None
    successful_count: int
    failed_count: int


# ============================
# Router
# ============================


class AgentRouter:
    """
    Routes requests to appropriate agents
    """

    def __init__(self, registry: AgentRegistry):
        """
        Initialize agent router

        Args:
            registry: Agent registry instance
        """
        self.registry = registry

    async def route_to_agent(
        self,
        agent_name: str,
        endpoint: str,
        method: str = "POST",
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> AgentResponse:
        """
        Route request to a specific agent

        Args:
            agent_name: Name of the target agent
            endpoint: API endpoint
            method: HTTP method
            payload: Request payload
            params: Query parameters

        Returns:
            AgentResponse with results
        """
        agent = self.registry.get_agent(agent_name)
        if not agent:
            logger.error(f"Agent {agent_name} not found")
            return AgentResponse(
                agent_name=agent_name, status_code=404, error=f"Agent {agent_name} not found"
            )

        logger.info(f"Routing request to {agent_name}{endpoint}")

        status_code, response_data = await self.registry.call_agent(
            agent_name=agent_name, endpoint=endpoint, method=method, data=payload, params=params
        )

        return AgentResponse(
            agent_name=agent_name,
            status_code=status_code,
            data=response_data,
            error=None if status_code in [200, 201] else f"Agent returned {status_code}",
        )

    async def route_to_agents(
        self,
        agent_names: List[str],
        endpoint: str,
        method: str = "POST",
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> MultiAgentResponse:
        """
        Route request to multiple agents in parallel

        Args:
            agent_names: List of agent names
            endpoint: API endpoint
            method: HTTP method
            payload: Request payload
            params: Query parameters

        Returns:
            MultiAgentResponse with results from all agents
        """
        logger.info(f"Routing request to {len(agent_names)} agents: {agent_names}")

        tasks = [
            self.route_to_agent(name, endpoint, method, payload, params) for name in agent_names
        ]

        responses = await asyncio.gather(*tasks)

        successful = sum(1 for r in responses if r.status_code in [200, 201])
        failed = len(responses) - successful

        return MultiAgentResponse(
            requested_agents=agent_names,
            responses=responses,
            successful_count=successful,
            failed_count=failed,
        )

    async def route_by_capability(
        self,
        capability: str,
        endpoint: str,
        method: str = "POST",
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
        healthy_only: bool = True,
    ) -> MultiAgentResponse:
        """
        Route request to all agents with specific capability

        Args:
            capability: Required capability
            endpoint: API endpoint
            method: HTTP method
            payload: Request payload
            params: Query parameters
            healthy_only: Only route to healthy agents

        Returns:
            MultiAgentResponse with results
        """
        if healthy_only:
            agents = self.registry.get_agents_by_capability(capability)
            agents = [a for a in agents if a.status.value == "healthy"]
        else:
            agents = self.registry.get_agents_by_capability(capability)

        if not agents:
            logger.warning(f"No agents found with capability '{capability}'")
            return MultiAgentResponse(
                requested_agents=[], responses=[], successful_count=0, failed_count=0
            )

        agent_names = [a.name for a in agents]
        logger.info(f"Routing to {len(agent_names)} agents with capability '{capability}'")

        return await self.route_to_agents(agent_names, endpoint, method, payload, params)

    async def route_search_request(
        self, query: str, location: str = "Ireland", max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Route search request through agents (multi-agent search)

        Args:
            query: Search query
            location: Search location
            max_results: Maximum results to return

        Returns:
            Aggregated search results from multiple agents
        """
        logger.info(f"Routing search request: query='{query}', location='{location}'")

        # Route to search-capable agents
        search_agents = self.registry.get_agents_by_capability("search")

        if not search_agents:
            logger.warning("No search-capable agents found")
            return {"candidates": [], "total_found": 0, "error": "No search agents available"}

        # Prepare search payload
        search_payload = {
            "query": query,
            "location": location,
            "max_results": max_results,
            "use_ai_formatting": True,
        }

        # Route to primary search endpoint
        response = await self.route_to_agents(
            agent_names=[a.name for a in search_agents[:2]],  # Use top 2 search agents
            endpoint="/search",
            method="POST",
            payload=search_payload,
        )

        # Aggregate results
        aggregated = {
            "candidates": [],
            "total_found": 0,
            "query": query,
            "location": location,
            "agents_queried": [],
        }

        for agent_response in response.responses:
            if agent_response.status_code == 200 and agent_response.data:
                aggregated["agents_queried"].append(agent_response.agent_name)
                candidates = agent_response.data.get("candidates", [])
                aggregated["candidates"].extend(candidates)
                aggregated["total_found"] += len(candidates)

        # Remove duplicates by profile URL
        seen_urls = set()
        unique_candidates = []
        for candidate in aggregated["candidates"]:
            url = candidate.get("profile_url")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_candidates.append(candidate)

        aggregated["candidates"] = unique_candidates[:max_results]
        aggregated["total_found"] = len(unique_candidates)

        logger.info(
            f"Search aggregation complete: {aggregated['total_found']} unique candidates from {len(aggregated['agents_queried'])} agents"
        )

        return aggregated

    async def route_interview_handoff(
        self, search_criteria: Dict[str, Any], candidate_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route interview handoff through appropriate agents

        Args:
            search_criteria: Search criteria for the role
            candidate_profile: Candidate profile information

        Returns:
            Interview handoff result from interviewer agent
        """
        logger.info(f"Routing interview handoff for candidate: {candidate_profile.get('fullName')}")

        # Get interviewer agent
        interviewer = self.registry.get_agent("interviewer-agent")
        if not interviewer:
            logger.error("Interviewer agent not found")
            return {"error": "Interviewer agent not available"}

        # Prepare handoff payload
        handoff_payload = {"searchCriteria": search_criteria, "candidateProfile": candidate_profile}

        # Route to interviewer agent
        response = await self.route_to_agent(
            agent_name="interviewer-agent",
            endpoint="/interview/start",
            method="POST",
            payload=handoff_payload,
        )

        if response.status_code == 200:
            logger.info(f"Interview handoff successful for {candidate_profile.get('fullName')}")
            return response.data
        else:
            logger.error(f"Interview handoff failed: {response.error}")
            return {"error": response.error, "status_code": response.status_code}


# ============================
# Imports needed
# ============================

import asyncio
