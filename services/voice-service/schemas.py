"""Voice Service - Pydantic Schemas
Comprehensive schema definitions for TTS, STT, WebRTC, and audio processing endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# ENUMS
# ============================================================================

class VoiceGender(str, Enum):
    """Voice gender options."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class AudioFormat(str, Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
    AAC = "aac"
    OPUS = "opus"


class VoiceQuality(str, Enum):
    """Voice quality levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class STTLanguage(str, Enum):
    """Supported STT languages."""
    EN_US = "en-US"
    EN_GB = "en-GB"
    ES_ES = "es-ES"
    FR_FR = "fr-FR"
    DE_DE = "de-DE"
    IT_IT = "it-IT"
    PT_BR = "pt-BR"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"
    ZH_CN = "zh-CN"


class EmotionType(str, Enum):
    """Emotion types for voice analytics."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"


class ProcessingStatus(str, Enum):
    """Audio processing job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# VOICE INFO & CONFIGURATION
# ============================================================================

class VoiceInfo(BaseModel):
    """Voice information model."""
    voice_id: str = Field(..., description="Unique voice identifier")
    name: str = Field(..., min_length=1, max_length=100)
    language: STTLanguage
    gender: VoiceGender
    description: str | None = Field(None, max_length=500)
    sample_url: str | None = None
    is_premium: bool = False
    quality: VoiceQuality = VoiceQuality.MEDIUM

    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "en-US-standard-1",
                "name": "US English Standard",
                "language": "en-US",
                "gender": "female",
                "description": "Standard US English female voice",
                "is_premium": False,
                "quality": "high"
            }
        }


class VoiceConfigUpdate(BaseModel):
    """Voice configuration update."""
    speaking_rate: float | None = Field(None, ge=0.25, le=4.0)
    pitch: float | None = Field(None, ge=-20.0, le=20.0)
    volume_gain_db: float | None = Field(None, ge=-96.0, le=16.0)
    sample_rate: int | None = Field(None, ge=8000, le=48000)
    audio_format: AudioFormat | None = None


# ============================================================================
# TEXT-TO-SPEECH (TTS)
# ============================================================================

class TTSRequest(BaseModel):
    """Text-to-speech synthesis request."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice_id: str = Field(..., description="Voice identifier")
    language: STTLanguage | None = STTLanguage.EN_US
    speaking_rate: float = Field(1.0, ge=0.25, le=4.0)
    pitch: float = Field(0.0, ge=-20.0, le=20.0)
    volume_gain_db: float = Field(0.0, ge=-96.0, le=16.0)
    audio_format: AudioFormat = AudioFormat.MP3
    sample_rate: int = Field(24000, ge=8000, le=48000)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a test of text-to-speech synthesis.",
                "voice_id": "en-US-standard-1",
                "language": "en-US",
                "speaking_rate": 1.0,
                "pitch": 0.0,
                "volume_gain_db": 0.0,
                "audio_format": "mp3",
                "sample_rate": 24000
            }
        }


class TTSSynthesizeRequest(BaseModel):
    """Advanced TTS synthesis with SSML support."""
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    ssml_enabled: bool = False
    effects: list[str] | None = None
    config: VoiceConfigUpdate | None = None

    @field_validator('text')
    @classmethod
    def validate_ssml(cls, v, info):
        if info.data.get('ssml_enabled') and not v.strip().startswith('<speak>'):
            raise ValueError('SSML-enabled text must start with <speak> tag')
        return v


class TTSResponse(BaseModel):
    """TTS synthesis response."""
    audio_url: str = Field(..., description="URL to generated audio file")
    audio_base64: str | None = Field(None, description="Base64-encoded audio data")
    duration_seconds: float = Field(..., ge=0)
    format: AudioFormat
    sample_rate: int
    file_size_bytes: int


# ============================================================================
# SPEECH-TO-TEXT (STT)
# ============================================================================

class STTRequest(BaseModel):
    """Speech-to-text transcription request."""
    audio_url: str | None = Field(None, description="URL to audio file")
    audio_base64: str | None = Field(None, description="Base64-encoded audio data")
    language: STTLanguage = STTLanguage.EN_US
    enable_punctuation: bool = True
    enable_word_timestamps: bool = False
    model: str = "default"

    @field_validator('audio_url')
    @classmethod
    def validate_audio_source(cls, v, info):
        # Ensure at least one audio source is provided
        if not v and not info.data.get('audio_base64'):
            raise ValueError('Either audio_url or audio_base64 must be provided')
        return v


class WordTimestamp(BaseModel):
    """Word-level timestamp."""
    word: str
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    end_time: float = Field(..., ge=0, description="End time in seconds")
    confidence: float = Field(..., ge=0.0, le=1.0)


class STTResponse(BaseModel):
    """STT transcription response."""
    transcript: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    language: STTLanguage
    duration_seconds: float = Field(..., ge=0)
    word_timestamps: list[WordTimestamp] | None = None


# ============================================================================
# AUDIO PROCESSING
# ============================================================================

class AudioProcessRequest(BaseModel):
    """Audio processing request."""
    audio_url: str
    operations: list[str] = Field(..., min_items=1)
    output_format: AudioFormat = AudioFormat.WAV


class AudioEnhanceRequest(BaseModel):
    """Audio enhancement request."""
    audio_url: str
    denoise: bool = True
    normalize: bool = True
    enhance_speech: bool = False
    target_loudness_db: float = Field(-16.0, ge=-30.0, le=0.0)


class AudioConvertRequest(BaseModel):
    """Audio format conversion request."""
    audio_url: str
    target_format: AudioFormat
    target_sample_rate: int | None = Field(None, ge=8000, le=48000)
    target_bitrate: int | None = Field(None, ge=32, le=320)


class AudioMetadata(BaseModel):
    """Audio file metadata."""
    duration_seconds: float
    format: str
    sample_rate: int
    channels: int
    bitrate: int | None = None
    file_size_bytes: int


# ============================================================================
# WEBRTC
# ============================================================================

class WebRTCOffer(BaseModel):
    """WebRTC offer."""
    sdp: str = Field(..., description="Session Description Protocol")
    type: Literal["offer"] = "offer"


class WebRTCAnswer(BaseModel):
    """WebRTC answer."""
    sdp: str = Field(..., description="Session Description Protocol")
    type: Literal["answer"] = "answer"


class ICECandidate(BaseModel):
    """ICE candidate for WebRTC."""
    candidate: str
    sdp_mid: str | None = None
    sdp_m_line_index: int | None = None


class WebRTCConnectionRequest(BaseModel):
    """WebRTC connection establishment."""
    peer_id: str
    offer: WebRTCOffer | None = None
    ice_servers: list[dict[str, Any]] | None = None


class WebRTCStatus(BaseModel):
    """WebRTC connection status."""
    peer_id: str
    connection_state: str
    ice_connection_state: str
    signaling_state: str
    connected_at: datetime | None = None


# ============================================================================
# PHONEME EXTRACTION
# ============================================================================

class PhonemeExtractionRequest(BaseModel):
    """Extract phonemes from audio."""
    audio_url: str
    language: STTLanguage = STTLanguage.EN_US
    include_timing: bool = True


class PhonemeTiming(BaseModel):
    """Phoneme with timing information."""
    phoneme: str
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)
    duration: float = Field(..., ge=0)


class PhonemeExtractionResponse(BaseModel):
    """Phoneme extraction response."""
    phonemes: list[str]
    timing: list[PhonemeTiming] | None = None
    language: STTLanguage
    duration_seconds: float


class PhonemeMapping(BaseModel):
    """Phoneme mapping information."""
    phoneme: str
    ipa: str = Field(..., description="International Phonetic Alphabet representation")
    example: str
    description: str | None = None


# ============================================================================
# VOICE ANALYTICS
# ============================================================================

class VoiceQualityAnalysisRequest(BaseModel):
    """Voice quality analysis request."""
    audio_url: str
    analyze_pitch: bool = True
    analyze_volume: bool = True
    analyze_clarity: bool = True


class VoiceQualityAnalysisResponse(BaseModel):
    """Voice quality analysis result."""
    overall_quality_score: float = Field(..., ge=0.0, le=10.0)
    pitch_mean: float | None = None
    pitch_std: float | None = None
    volume_mean_db: float | None = None
    volume_std_db: float | None = None
    clarity_score: float | None = Field(None, ge=0.0, le=1.0)
    signal_to_noise_ratio: float | None = None


class SpeechRateAnalysisRequest(BaseModel):
    """Speech rate analysis request."""
    audio_url: str
    transcript: str | None = None


class SpeechRateAnalysisResponse(BaseModel):
    """Speech rate analysis result."""
    words_per_minute: float
    syllables_per_second: float
    pause_count: int
    average_pause_duration: float
    speech_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of speech to silence")


class EmotionDetectionRequest(BaseModel):
    """Emotion detection request."""
    audio_url: str
    granular: bool = False


class EmotionDetectionResponse(BaseModel):
    """Emotion detection response."""
    primary_emotion: EmotionType
    confidence: float = Field(..., ge=0.0, le=1.0)
    emotion_scores: dict[EmotionType, float]


# ============================================================================
# BATCH & HISTORY
# ============================================================================

class BatchProcessRequest(BaseModel):
    """Batch processing request."""
    operations: list[dict[str, Any]] = Field(..., min_length=1, max_length=100)
    callback_url: str | None = None


class BatchProcessResponse(BaseModel):
    """Batch processing response."""
    batch_id: str
    total_operations: int
    status: ProcessingStatus
    created_at: datetime


class VoiceHistoryEntry(BaseModel):
    """Voice service usage history entry."""
    operation_id: str
    operation_type: str
    timestamp: datetime
    duration_seconds: float | None = None
    status: ProcessingStatus
    user_id: str | None = None


# ============================================================================
# SERVICE INFO & HEALTH
# ============================================================================

class VoiceServiceInfo(BaseModel):
    """Voice service information."""
    service_name: str = "Voice Service"
    version: str
    supported_languages: list[STTLanguage]
    supported_formats: list[AudioFormat]
    available_voices: int
    webrtc_enabled: bool
    features: list[str]


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    tts_available: bool
    stt_available: bool
    webrtc_available: bool
    audio_processing_available: bool
    uptime_seconds: float


# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str | None = None
    code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
