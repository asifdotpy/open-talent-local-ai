"""Database service layer for avatar-service.
Provides CRUD operations and data persistence.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models.database import (
    Asset,
    Audio,
    Avatar,
    Base,
    Config,
    Phoneme,
    Preset,
    Render,
)
from app.models.database import Session as DBSession


class DatabaseService:
    """Database service for avatar-service.
    Handles all persistence operations.
    """

    def __init__(self, database_url: str = "sqlite:///./avatar.db"):
        """Initialize database service.

        Args:
            database_url: SQLAlchemy connection string
                - SQLite: sqlite:///./avatar.db
                - PostgreSQL: postgresql://user:pass@localhost/avatar
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_db(self):
        """Context manager for database sessions."""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ============= AVATAR OPERATIONS =============

    def get_avatar(self, avatar_id: str) -> Avatar | None:
        """Get avatar by ID."""
        with self.get_db() as db:
            return db.query(Avatar).filter_by(avatar_id=avatar_id).first()

    def get_or_create_avatar(self, avatar_id: str, **kwargs) -> Avatar:
        """Get existing avatar or create new one."""
        with self.get_db() as db:
            avatar = db.query(Avatar).filter_by(avatar_id=avatar_id).first()
            if avatar:
                return avatar

            avatar = Avatar(avatar_id=avatar_id, **kwargs)
            db.add(avatar)
            db.commit()
            return avatar

    def create_avatar(self, avatar_id: str, name: str | None = None, **kwargs) -> Avatar:
        """Create new avatar."""
        with self.get_db() as db:
            avatar = Avatar(avatar_id=avatar_id, name=name, **kwargs)
            db.add(avatar)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                raise ValueError(f"Avatar {avatar_id} already exists")
            return avatar

    def update_avatar(self, avatar_id: str, **kwargs) -> Avatar | None:
        """Update avatar."""
        with self.get_db() as db:
            avatar = db.query(Avatar).filter_by(avatar_id=avatar_id).first()
            if not avatar:
                return None

            for key, value in kwargs.items():
                if hasattr(avatar, key):
                    setattr(avatar, key, value)

            db.commit()
            return avatar

    def update_avatar_state(self, avatar_id: str, state_updates: dict) -> Avatar | None:
        """Merge state updates into avatar state."""
        with self.get_db() as db:
            avatar = db.query(Avatar).filter_by(avatar_id=avatar_id).first()
            if not avatar:
                return None

            avatar.state.update(state_updates)
            db.commit()
            return avatar

    def list_avatars(self, limit: int = 100, offset: int = 0) -> list[Avatar]:
        """List all avatars with pagination."""
        with self.get_db() as db:
            return db.query(Avatar).offset(offset).limit(limit).all()

    # ============= SESSION OPERATIONS =============

    def get_session(self, session_id: str) -> DBSession | None:
        """Get session by ID."""
        with self.get_db() as db:
            return db.query(DBSession).filter_by(session_id=session_id).first()

    def create_session(self, session_id: str, avatar_id: str, metadata: dict = None) -> DBSession:
        """Create new session."""
        with self.get_db() as db:
            session = DBSession(session_id=session_id, avatar_id=avatar_id, metadata=metadata or {})
            db.add(session)
            db.commit()
            return session

    def delete_session(self, session_id: str) -> bool:
        """Soft delete session (mark deleted_at)."""
        with self.get_db() as db:
            session = db.query(DBSession).filter_by(session_id=session_id).first()
            if not session:
                return False

            session.deleted_at = datetime.utcnow()
            db.commit()
            return True

    def list_sessions(self, avatar_id: str, limit: int = 100) -> list[DBSession]:
        """List sessions for avatar (excluding deleted)."""
        with self.get_db() as db:
            return db.query(DBSession).filter_by(avatar_id=avatar_id, deleted_at=None).limit(limit).all()

    # ============= PRESET OPERATIONS =============

    def get_preset(self, preset_id: str) -> Preset | None:
        """Get preset by ID."""
        with self.get_db() as db:
            return db.query(Preset).filter_by(preset_id=preset_id).first()

    def create_preset(self, preset_id: str, name: str, settings: dict) -> Preset:
        """Create new preset."""
        with self.get_db() as db:
            preset = Preset(preset_id=preset_id, name=name, settings=settings)
            db.add(preset)
            db.commit()
            return preset

    def update_preset(self, preset_id: str, **kwargs) -> Preset | None:
        """Update preset."""
        with self.get_db() as db:
            preset = db.query(Preset).filter_by(preset_id=preset_id).first()
            if not preset:
                return None

            for key, value in kwargs.items():
                if hasattr(preset, key):
                    setattr(preset, key, value)

            db.commit()
            return preset

    def delete_preset(self, preset_id: str) -> bool:
        """Delete preset."""
        with self.get_db() as db:
            preset = db.query(Preset).filter_by(preset_id=preset_id).first()
            if not preset:
                return False

            db.delete(preset)
            db.commit()
            return True

    def list_presets(self, limit: int = 100) -> list[Preset]:
        """List all presets."""
        with self.get_db() as db:
            return db.query(Preset).limit(limit).all()

    # ============= RENDER OPERATIONS =============

    def create_render(self, frame_id: str, avatar_id: str, width: int, height: int, file_path: str, **kwargs) -> Render:
        """Create render record."""
        with self.get_db() as db:
            render = Render(
                frame_id=frame_id,
                avatar_id=avatar_id,
                width=width,
                height=height,
                file_path=file_path,
                **kwargs,
            )
            db.add(render)
            db.commit()
            return render

    def get_render(self, frame_id: str) -> Render | None:
        """Get render by frame ID."""
        with self.get_db() as db:
            return db.query(Render).filter_by(frame_id=frame_id).first()

    def list_renders(self, avatar_id: str, limit: int = 50) -> list[Render]:
        """List renders for avatar (most recent first)."""
        with self.get_db() as db:
            return db.query(Render).filter_by(avatar_id=avatar_id).order_by(Render.created_at.desc()).limit(limit).all()

    # ============= AUDIO OPERATIONS =============

    def create_audio(
        self,
        audio_id: str,
        avatar_id: str,
        text: str,
        file_path: str,
        duration_ms: int = 0,
        **kwargs,
    ) -> Audio:
        """Create audio record."""
        with self.get_db() as db:
            audio = Audio(
                audio_id=audio_id,
                avatar_id=avatar_id,
                text=text,
                file_path=file_path,
                duration_ms=duration_ms,
                **kwargs,
            )
            db.add(audio)
            db.commit()
            return audio

    def get_audio(self, audio_id: str) -> Audio | None:
        """Get audio by ID."""
        with self.get_db() as db:
            return db.query(Audio).filter_by(audio_id=audio_id).first()

    def list_audios(self, avatar_id: str, limit: int = 50) -> list[Audio]:
        """List audios for avatar (most recent first)."""
        with self.get_db() as db:
            return db.query(Audio).filter_by(avatar_id=avatar_id).order_by(Audio.created_at.desc()).limit(limit).all()

    # ============= PHONEME OPERATIONS =============

    def create_phoneme(self, audio_id: str, phoneme: str, start_ms: int, end_ms: int, **kwargs) -> Phoneme:
        """Create phoneme record."""
        with self.get_db() as db:
            ph = Phoneme(audio_id=audio_id, phoneme=phoneme, start_ms=start_ms, end_ms=end_ms, **kwargs)
            db.add(ph)
            db.commit()
            return ph

    def get_phonemes(self, audio_id: str) -> list[Phoneme]:
        """Get all phonemes for audio."""
        with self.get_db() as db:
            return db.query(Phoneme).filter_by(audio_id=audio_id).order_by(Phoneme.start_ms).all()

    def create_phonemes_batch(self, audio_id: str, phonemes: list[dict]) -> list[Phoneme]:
        """Create multiple phonemes in one transaction."""
        with self.get_db() as db:
            created = []
            for ph_data in phonemes:
                ph = Phoneme(audio_id=audio_id, **ph_data)
                db.add(ph)
                created.append(ph)
            db.commit()
            return created

    # ============= ASSET OPERATIONS =============

    def create_asset(self, asset_id: str, name: str, asset_type: str, file_path: str, **kwargs) -> Asset:
        """Create asset record."""
        with self.get_db() as db:
            asset = Asset(asset_id=asset_id, name=name, asset_type=asset_type, file_path=file_path, **kwargs)
            db.add(asset)
            db.commit()
            return asset

    def get_asset(self, asset_id: str) -> Asset | None:
        """Get asset by ID."""
        with self.get_db() as db:
            return db.query(Asset).filter_by(asset_id=asset_id).first()

    def list_assets(self, asset_type: str | None = None, limit: int = 100) -> list[Asset]:
        """List assets, optionally filtered by type."""
        with self.get_db() as db:
            query = db.query(Asset)
            if asset_type:
                query = query.filter_by(asset_type=asset_type)
            return query.limit(limit).all()

    # ============= CONFIG OPERATIONS =============

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        with self.get_db() as db:
            config = db.query(Config).filter_by(key=key).first()
            return config.value if config else default

    def set_config(self, key: str, value: Any, description: str = None) -> Config:
        """Set config value."""
        with self.get_db() as db:
            config = db.query(Config).filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = Config(key=key, value=value, description=description)
                db.add(config)
            db.commit()
            return config

    def get_all_config(self) -> dict[str, Any]:
        """Get all config values as dictionary."""
        with self.get_db() as db:
            configs = db.query(Config).all()
            return {cfg.key: cfg.value for cfg in configs}

    # ============= UTILITY OPERATIONS =============

    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            with self.get_db() as db:
                db.execute("SELECT 1")
            return True
        except Exception:
            return False

    def get_stats(self) -> dict[str, int]:
        """Get database statistics."""
        with self.get_db() as db:
            return {
                "avatars": db.query(func.count(Avatar.id)).scalar() or 0,
                "sessions": db.query(func.count(DBSession.id)).filter_by(deleted_at=None).scalar() or 0,
                "presets": db.query(func.count(Preset.id)).scalar() or 0,
                "renders": db.query(func.count(Render.id)).scalar() or 0,
                "audios": db.query(func.count(Audio.id)).scalar() or 0,
                "assets": db.query(func.count(Asset.id)).scalar() or 0,
            }
