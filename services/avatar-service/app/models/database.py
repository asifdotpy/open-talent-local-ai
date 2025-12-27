"""SQLAlchemy ORM models for avatar-service.
Persistent storage layer with SQLite (dev) / PostgreSQL (prod).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Avatar(Base):
    """Avatar entity — represents a virtual character."""

    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True)
    avatar_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    state = Column(JSON, default={}, nullable=False)
    traits = Column(JSON, default={}, nullable=False)
    model_id = Column(String(255), default="granite-avatar-small")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="avatar", cascade="all, delete-orphan")
    renders = relationship("Render", back_populates="avatar", cascade="all, delete-orphan")
    audios = relationship("Audio", back_populates="avatar", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Avatar {self.avatar_id}>"


class Session(Base):
    """Session entity — represents an interview/interaction session."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    avatar_id = Column(String(255), ForeignKey("avatars.avatar_id"), nullable=False)
    metadata = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    avatar = relationship("Avatar", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.session_id}>"


class Preset(Base):
    """Preset entity — stores avatar customization presets."""

    __tablename__ = "presets"

    id = Column(Integer, primary_key=True)
    preset_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    settings = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Preset {self.preset_id}>"


class Render(Base):
    """Render entity — stores generated avatar frames."""

    __tablename__ = "renders"

    id = Column(Integer, primary_key=True)
    frame_id = Column(String(255), unique=True, nullable=False, index=True)
    avatar_id = Column(String(255), ForeignKey("avatars.avatar_id"), nullable=False)
    prompt = Column(String(1024), nullable=True)
    width = Column(Integer, default=512)
    height = Column(Integer, default=512)
    format = Column(String(10), default="png")
    file_path = Column(String(1024), nullable=True)
    file_size = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    avatar = relationship("Avatar", back_populates="renders")

    def __repr__(self):
        return f"<Render {self.frame_id}>"


class Audio(Base):
    """Audio entity — stores generated TTS audio files."""

    __tablename__ = "audios"

    id = Column(Integer, primary_key=True)
    audio_id = Column(String(255), unique=True, nullable=False, index=True)
    avatar_id = Column(String(255), ForeignKey("avatars.avatar_id"), nullable=False)
    text = Column(String(2048), nullable=False)
    voice_id = Column(String(255), default="piper_en_us")
    duration_ms = Column(Integer, nullable=True)
    sample_rate = Column(Integer, default=22050)
    file_path = Column(String(1024), nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    avatar = relationship("Avatar", back_populates="audios")
    phonemes = relationship("Phoneme", back_populates="audio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Audio {self.audio_id}>"


class Phoneme(Base):
    """Phoneme entity — phoneme timing data for lipsync."""

    __tablename__ = "phonemes"

    id = Column(Integer, primary_key=True)
    audio_id = Column(String(255), ForeignKey("audios.audio_id"), nullable=False)
    phoneme = Column(String(10), nullable=False)
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    viseme = Column(String(20), nullable=True)
    confidence = Column(Float, default=1.0)

    # Relationships
    audio = relationship("Audio", back_populates="phonemes")

    def __repr__(self):
        return f"<Phoneme {self.phoneme} {self.start_ms}-{self.end_ms}ms>"


class Asset(Base):
    """Asset entity — stores uploaded/downloaded avatar assets."""

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    asset_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)  # mesh, texture, animation, etc.
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA256
    mime_type = Column(String(100), nullable=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Asset {self.asset_id}>"


class Config(Base):
    """Config entity — service-level configuration."""

    __tablename__ = "config"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(String(1024), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Config {self.key}>"
