"""
Agent Health Monitoring Module
Handles ongoing health checks and status reporting

Author: OpenTalent Team
Updated: December 13, 2025
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from agent_registry import AgentRegistry, AgentStatus, AgentMetadata

logger = logging.getLogger(__name__)

# ============================
# Models
# ============================

class HealthCheckResult(BaseModel):
    """Result of a single health check"""
    timestamp: datetime
    agent_name: str
    status: AgentStatus
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

class HealthReport(BaseModel):
    """Overall health report for all agents"""
    timestamp: datetime
    total_agents: int
    healthy_agents: int
    unhealthy_agents: int
    unreachable_agents: int
    unknown_agents: int
    agents: List[AgentMetadata]
    recent_checks: List[HealthCheckResult] = []

    @property
    def health_percentage(self) -> float:
        """Calculate percentage of healthy agents"""
        if self.total_agents == 0:
            return 0.0
        return (self.healthy_agents / self.total_agents) * 100

# ============================
# Health Monitoring
# ============================

class HealthMonitor:
    """
    Monitors agent health and provides reports
    """
    
    def __init__(self, registry: AgentRegistry, retention_hours: int = 1):
        """
        Initialize health monitor
        
        Args:
            registry: Agent registry instance
            retention_hours: How long to keep health check history
        """
        self.registry = registry
        self.retention_hours = retention_hours
        self.health_history: List[HealthCheckResult] = []
        self.last_full_check: Optional[datetime] = None

    async def perform_health_check(self) -> HealthReport:
        """
        Perform comprehensive health check of all agents
        
        Returns:
            HealthReport with current status of all agents
        """
        logger.info("Performing comprehensive health check")
        
        # Check all agents
        health_statuses = await self.registry.check_all_agents_health()
        
        # Record results
        now = datetime.now()
        self.last_full_check = now
        
        # Calculate summary
        agents = self.registry.get_all_agents()
        healthy_count = sum(1 for agent in agents if agent.status == AgentStatus.HEALTHY)
        unhealthy_count = sum(1 for agent in agents if agent.status == AgentStatus.UNHEALTHY)
        unreachable_count = sum(1 for agent in agents if agent.status == AgentStatus.UNREACHABLE)
        unknown_count = sum(1 for agent in agents if agent.status == AgentStatus.UNKNOWN)
        
        report = HealthReport(
            timestamp=now,
            total_agents=len(agents),
            healthy_agents=healthy_count,
            unhealthy_agents=unhealthy_count,
            unreachable_agents=unreachable_count,
            unknown_agents=unknown_count,
            agents=agents,
            recent_checks=self._get_recent_checks(limit=10)
        )
        
        # Log summary
        logger.info(f"Health check complete: {healthy_count}/{len(agents)} agents healthy "
                   f"({report.health_percentage:.1f}%)")
        
        return report

    def _get_recent_checks(self, limit: int = 10) -> List[HealthCheckResult]:
        """Get most recent health checks"""
        self._cleanup_old_history()
        return self.health_history[-limit:] if self.health_history else []

    def _cleanup_old_history(self):
        """Remove health check history older than retention period"""
        if not self.health_history:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        self.health_history = [check for check in self.health_history 
                              if check.timestamp > cutoff_time]

    def get_agent_status(self, agent_name: str) -> Optional[AgentStatus]:
        """Get current status of a specific agent"""
        agent = self.registry.get_agent(agent_name)
        return agent.status if agent else None

    def get_critical_agents(self) -> List[AgentMetadata]:
        """Get agents that are unhealthy or unreachable"""
        critical = []
        for agent in self.registry.get_all_agents():
            if agent.status in [AgentStatus.UNHEALTHY, AgentStatus.UNREACHABLE]:
                critical.append(agent)
        return critical

    def get_status_summary(self) -> Dict[str, int]:
        """Get summary of agent statuses"""
        agents = self.registry.get_all_agents()
        return {
            "total": len(agents),
            "healthy": sum(1 for a in agents if a.status == AgentStatus.HEALTHY),
            "unhealthy": sum(1 for a in agents if a.status == AgentStatus.UNHEALTHY),
            "unreachable": sum(1 for a in agents if a.status == AgentStatus.UNREACHABLE),
            "unknown": sum(1 for a in agents if a.status == AgentStatus.UNKNOWN)
        }

