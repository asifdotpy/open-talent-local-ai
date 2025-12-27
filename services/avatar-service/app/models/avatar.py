"""Avatar Service - Pydantic V2 schemas (requests + responses)
Created: December 17, 2025
Coverage: ~23 schemas for avatar rendering, lip-sync, presets, sessions, and health
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RenderFormat(str, Enum):
    png = "png"
    jpeg = "jpeg"
    webp = "webp"
    mp4 = "mp4"


class AvatarQuality(str, Enum):
    fast = "fast"
    medium = "medium"
    high = "high"
    ultra = "ultra"


class ShadingMode(str, Enum):
    pbr = "pbr"
    toon = "toon"
    flat = "flat"


class RenderRequest(BaseModel):
    avatar_id: Optional[str] = None
    width: int = Field(512, ge=64, le=4096)
    height: int = Field(512, ge=64, le=4096)
    format: str = Field("png", description="Output format (not constrained to enum)")
    prompt: Optional[str] = None
    background: Optional[str] = Field(None, description="Background style or color")
    camera: Optional[str] = Field(None, description="Camera preset identifier")
    quality: AvatarQuality = AvatarQuality.medium
    shading: ShadingMode = ShadingMode.pbr
    seed: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(from_attributes=True)


class RenderResponse(BaseModel):
    avatar_id: str
    frame_id: str
    frame_url: str
    width: int
    height: int
    prompt: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LipsyncRequest(BaseModel):
    avatar_id: Optional[str] = None
    text: Optional[str] = None
    audio_url: Optional[str] = None
    voice_id: Optional[str] = None
    sample_rate: int = Field(16000, ge=8000, le=48000)

    model_config = ConfigDict(from_attributes=True)


class VisemeTiming(BaseModel):
    viseme: str
    start: float = Field(..., ge=0.0)
    end: float = Field(..., ge=0.0)


class LipsyncResponse(BaseModel):
    avatar_id: str
    visemes: list[VisemeTiming]
    phonemes: list[dict[str, Any]]
    duration: float

    model_config = ConfigDict(from_attributes=True)


class EmotionRequest(BaseModel):
    avatar_id: str
    emotion: str = Field(default="neutral", description="Emotion label")
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)


class CustomizeRequest(BaseModel):
    avatar_id: Optional[str] = None
    preset_id: Optional[str] = None
    traits: dict[str, Any] = Field(default_factory=dict)
    persist: bool = False

    model_config = ConfigDict(from_attributes=True)


class StatePatch(BaseModel):
    state: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class PhonemeRequest(BaseModel):
    text: str
    sample_rate: int = 16000
    language: Optional[str] = Field(None, description="Language code for alignment")


class PhonemeTimingRequest(BaseModel):
    phonemes: list[str]
    audio_duration: float


class PresetCreateRequest(BaseModel):
    name: str
    values: dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PresetUpdateRequest(BaseModel):
    name: Optional[str] = None
    values: Optional[dict[str, Any]] = None
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ModelSelectRequest(BaseModel):
    avatar_id: str
    model_id: str

    model_config = {"protected_namespaces": ()}


class ModelInfo(BaseModel):
    model_id: str
    quality: AvatarQuality
    size_mb: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ModelListResponse(BaseModel):
    models: list[ModelInfo]
    default_model: Optional[str] = None


class SessionCreateRequest(BaseModel):
    avatar_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    ttl_seconds: int = Field(3600, ge=60, le=86400)

    model_config = ConfigDict(from_attributes=True)


class SessionResponse(BaseModel):
    session_id: str
    avatar_id: str
    created_at: datetime
    expires_at: datetime
    metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AnimationRequest(BaseModel):
    animation: str
    loop: bool = False
    duration: Optional[float] = None
    intensity: Optional[float] = Field(None, ge=0.0, le=1.0)
    avatar_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SnapshotRequest(BaseModel):
    note: Optional[str] = None
    camera: Optional[str] = None
    resolution: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConfigUpdateRequest(BaseModel):
    quality: Optional[str] = None
    fps: Optional[int] = None
    shading: Optional[str] = None
    resolution: Optional[str] = None
    antialiasing: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class PresetResponse(BaseModel):
    preset_id: str
    name: str
    values: dict[str, Any]
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PresetListResponse(BaseModel):
    presets: list[PresetResponse]


class StateResponse(BaseModel):
    avatar_id: str
    state: dict[str, Any]


class PhonemeResponse(BaseModel):
    text: str
    phonemes: list[dict[str, Any]]
    sample_rate: int


class PhonemeAlignmentResponse(BaseModel):
    duration: float
    alignment: list[dict[str, Any]]


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    models_loaded: int
    renderer_ready: bool


class ServiceInfoResponse(BaseModel):
    name: str
    version: str
    supported_formats: list[RenderFormat]
    supported_qualities: list[AvatarQuality]
    renderer: str
    voice_integration: bool
