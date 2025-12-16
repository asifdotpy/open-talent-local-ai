from __future__ import annotations

from typing import List, Optional
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
    voice: Optional[str] = None
    speed: Optional[float] = 1.0
    extract_phonemes: Optional[bool] = True


class TTSResponse(BaseModel):
    audio_data: str  # base64
    duration: float
    sample_rate: int
    phonemes: List[Phoneme] = []
    words: List[WordTiming] = []


class STTResponse(BaseModel):
    text: str
    words: List[WordTiming] = []
    duration: float
    confidence: float


class VADRequest(BaseModel):
    remove_silence: Optional[bool] = False


class VADFrame(BaseModel):
    has_voice: bool
    start: float
    end: float


class WebRTCSession(BaseModel):
    session_id: str
    job_description: Optional[str] = None


class WebSocketSTTMessage(BaseModel):
    # Audio chunk as base64 string
    audio_chunk_b64: str
    use_vad: Optional[bool] = True


class WebSocketTTSMessage(BaseModel):
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = 1.0