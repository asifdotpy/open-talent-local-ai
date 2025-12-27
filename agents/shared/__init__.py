"""
OpenTalent Shared Infrastructure
Provides common models, message bus, and service clients for all agents.
"""

from .config import AgentConfig, config, get_config
from .message_bus import MessageBus, Topics
from .models import (
    AgentMessage,
    CandidateProfile,
    CandidateSource,
    CandidateStatus,
    CompetitorIntel,
    Education,
    EngagementHistory,
    InterviewResult,
    MarketInsight,
    MessagePriority,
    MessageType,
    OutreachAttempt,
    OutreachChannel,
    OutreachStatus,
    PipelineState,
    SalaryTrend,
    Skill,
    SkillDemand,
    SocialProfile,
    SourcingPipeline,
    WorkExperience,
)
from .service_clients import (
    AvatarServiceClient,
    ConversationServiceClient,
    GenkitServiceClient,
    InterviewServiceClient,
    ServiceClients,
    VoiceServiceClient,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "CandidateProfile",
    "EngagementHistory",
    "MarketInsight",
    "AgentMessage",
    "SourcingPipeline",
    "InterviewResult",
    "CandidateStatus",
    "CandidateSource",
    "MessageType",
    "MessagePriority",
    "PipelineState",
    "Skill",
    "WorkExperience",
    "Education",
    "SocialProfile",
    "OutreachAttempt",
    "OutreachChannel",
    "OutreachStatus",
    "SalaryTrend",
    "CompetitorIntel",
    "SkillDemand",
    # Message Bus
    "MessageBus",
    "Topics",
    # Service Clients
    "ConversationServiceClient",
    "VoiceServiceClient",
    "AvatarServiceClient",
    "InterviewServiceClient",
    "GenkitServiceClient",
    "ServiceClients",
    # Config
    "AgentConfig",
    "get_config",
    "config",
]
