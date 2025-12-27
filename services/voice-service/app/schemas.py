from __future__ import annotations

from pydantic import BaseModel, Field


class WordTiming(BaseModel):
    word: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)


class Phoneme(BaseModel):
    symbol: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)


class TTSRequest(BaseModel):
    text: str = Field(min_length=1)
    voice: str | None = None
    speed: float | None = 1.0
    extract_phonemes: bool | None = True


class TTSResponse(BaseModel):
    audio_data: str  # base64
    duration: float
    sample_rate: int
    phonemes: list[Phoneme] = []
    words: list[WordTiming] = []


class STTResponse(BaseModel):
    text: str
    words: list[WordTiming] = []
    duration: float
    confidence: float


class VADRequest(BaseModel):
    remove_silence: bool | None = False


class VADFrame(BaseModel):
    has_voice: bool
    start: float
    end: float


class WebRTCSession(BaseModel):
    session_id: str
    job_description: str | None = None


class WebSocketSTTMessage(BaseModel):
    # Audio chunk as base64 string
    audio_chunk_b64: str
    use_vad: bool | None = True


class WebSocketTTSMessage(BaseModel):
    text: str
    voice: str | None = None
    speed: float | None = 1.0
