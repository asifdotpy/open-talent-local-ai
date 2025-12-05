"""
TalentAI Shared Infrastructure
Provides common models, message bus, and service clients for all agents.
"""

from .models import (
    CandidateProfile,
    EngagementHistory,
    MarketInsight,
    AgentMessage,
    SourcingPipeline,
    InterviewResult,
    CandidateStatus,
    CandidateSource,
    MessageType,
    MessagePriority,
    PipelineState,
    Skill,
    WorkExperience,
    Education,
    SocialProfile,
    OutreachAttempt,
    OutreachChannel,
    OutreachStatus,
    SalaryTrend,
    CompetitorIntel,
    SkillDemand,
)

from .message_bus import (
    MessageBus,
    Topics,
)

from .service_clients import (
    ConversationServiceClient,
    VoiceServiceClient,
    AvatarServiceClient,
    InterviewServiceClient,
    GenkitServiceClient,
    ServiceClients,
)

from .config import (
    AgentConfig,
    get_config,
    config,
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
