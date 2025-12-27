"""Avatar v1 API scaffold with in-memory state and mock responses."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.models.avatar import (
    AnimationRequest,
    ConfigUpdateRequest,
    CustomizeRequest,
    EmotionRequest,
    LipsyncRequest,
    ModelSelectRequest,
    PhonemeRequest,
    PhonemeTimingRequest,
    PresetCreateRequest,
    PresetUpdateRequest,
    RenderRequest,
    SessionCreateRequest,
    SnapshotRequest,
    StatePatch,
)

router = APIRouter(prefix="/api/v1/avatars", tags=["Avatars"])

# In-memory stores (ephemeral, for stub/testing only)
avatars: dict[str, dict[str, Any]] = {}
presets: dict[str, dict[str, Any]] = {
    "default": {"name": "default", "values": {"skin_tone": "medium", "hair": "short"}},
    "casual": {"name": "casual", "values": {"outfit": "casual", "mood": "friendly"}},
}
assets: list[dict[str, Any]] = [
    {"asset_id": "mesh_face", "type": "mesh", "label": "Base Face"},
    {"asset_id": "tex_default", "type": "texture", "label": "Default Texture"},
]
models: list[dict[str, Any]] = [
    {"model_id": "granite-avatar-small", "quality": "fast"},
    {"model_id": "granite-avatar-pro", "quality": "high"},
]
sessions: dict[str, dict[str, Any]] = {}
config: dict[str, Any] = {"quality": "medium", "fps": 30, "shading": "pbr"}
viseme_map: dict[str, str] = {
    "A": "viseme_AE",
    "B": "viseme_BM",
    "C": "viseme_CH",
}


def _ensure_avatar(avatar_id: str) -> dict[str, Any]:
    if avatar_id not in avatars:
        avatars[avatar_id] = {
            "avatar_id": avatar_id,
            "state": {"emotion": "neutral", "pose": "idle", "voice_attached": False},
            "traits": {},
        }
    return avatars[avatar_id]


@router.post("/render")
async def render_avatar(payload: RenderRequest):
    avatar_id = payload.avatar_id or "temp-avatar"
    _ensure_avatar(avatar_id)
    frame_id = str(uuid.uuid4())
    return {
        "avatar_id": avatar_id,
        "frame_id": frame_id,
        "frame_url": f"/renders/{frame_id}.{payload.format}",
        "width": payload.width,
        "height": payload.height,
        "prompt": payload.prompt,
    }


@router.post("/lipsync")
async def lipsync(payload: LipsyncRequest):
    avatar_id = payload.avatar_id or "temp-avatar"
    phonemes = [
        {"phoneme": "HH", "t": 0.0},
        {"phoneme": "AH", "t": 0.12},
        {"phoneme": "L", "t": 0.20},
    ]
    return {"avatar_id": avatar_id, "phonemes": phonemes}


@router.post("/emotions")
async def set_emotion(payload: EmotionRequest):
    avatar = _ensure_avatar(payload.avatar_id)
    avatar["state"].update({"emotion": payload.emotion, "emotion_intensity": payload.intensity})
    return {"avatar_id": payload.avatar_id, "emotion": payload.emotion, "intensity": payload.intensity}


@router.get("/presets")
async def list_presets():
    return {"presets": list(presets.values())}


@router.get("/presets/{preset_id}")
async def get_preset(preset_id: str):
    preset = presets.get(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.post("/presets")
async def create_preset(payload: PresetCreateRequest):
    preset_id = payload.name.lower().replace(" ", "-")
    presets[preset_id] = {"name": payload.name, "values": payload.values}
    return {"preset_id": preset_id, **presets[preset_id]}


@router.patch("/presets/{preset_id}")
async def update_preset(preset_id: str, payload: PresetUpdateRequest):
    preset = presets.get(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    if payload.name is not None:
        preset["name"] = payload.name
    if payload.values is not None:
        preset["values"] = payload.values
    return {"preset_id": preset_id, **preset}


@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: str):
    presets.pop(preset_id, None)
    return {"deleted": preset_id}


@router.post("/customize")
async def customize(payload: CustomizeRequest):
    avatar_id = payload.avatar_id or str(uuid.uuid4())
    avatar = _ensure_avatar(avatar_id)
    if payload.preset_id:
        preset = presets.get(payload.preset_id)
        if preset:
            avatar["traits"].update(preset.get("values", {}))
    avatar["traits"].update(payload.traits)
    return {"avatar_id": avatar_id, "traits": avatar["traits"]}


@router.get("/{avatar_id}/state")
async def get_state(avatar_id: str):
    avatar = _ensure_avatar(avatar_id)
    return {"avatar_id": avatar_id, "state": avatar.get("state", {})}


@router.patch("/{avatar_id}/state")
async def patch_state(avatar_id: str, payload: StatePatch):
    avatar = _ensure_avatar(avatar_id)
    avatar_state = avatar.setdefault("state", {})
    avatar_state.update(payload.state)
    return {"avatar_id": avatar_id, "state": avatar_state}


@router.post("/phonemes")
async def phonemes(payload: PhonemeRequest):
    phoneme_seq = [
        {"p": "AH", "t": 0.0},
        {"p": "V", "t": 0.08},
        {"p": "AA", "t": 0.16},
    ]
    return {"text": payload.text, "phonemes": phoneme_seq, "sample_rate": payload.sample_rate}


@router.post("/phonemes/timing")
async def phoneme_timing(payload: PhonemeTimingRequest):
    aligned = [{"phoneme": p, "start": i * 0.05, "end": i * 0.05 + 0.04} for i, p in enumerate(payload.phonemes)]
    return {"duration": payload.audio_duration, "alignment": aligned}


@router.post("/lipsync/preview")
async def lipsync_preview(payload: LipsyncRequest):
    return {"avatar_id": payload.avatar_id or "temp-avatar", "visemes": ["A", "B", "C"]}


@router.get("/visemes")
async def visemes():
    return {"visemes": viseme_map}


@router.get("/{avatar_id}/emotions")
async def get_emotions(avatar_id: str):
    avatar = _ensure_avatar(avatar_id)
    return {"avatar_id": avatar_id, "emotion": avatar["state"].get("emotion", "neutral")}


@router.patch("/{avatar_id}/emotions")
async def patch_emotions(avatar_id: str, payload: EmotionRequest):
    avatar = _ensure_avatar(avatar_id)
    avatar["state"].update({"emotion": payload.emotion, "emotion_intensity": payload.intensity})
    return {"avatar_id": avatar_id, "emotion": payload.emotion}


@router.post("/{avatar_id}/animations")
async def trigger_animation(avatar_id: str, payload: AnimationRequest):
    avatar = _ensure_avatar(avatar_id)
    last = {"animation": payload.animation, "loop": payload.loop, "duration": payload.duration}
    avatar["state"]["last_animation"] = last
    return {"avatar_id": avatar_id, "applied": last}


@router.get("/config")
async def get_config():
    return config


@router.put("/config")
async def update_config(payload: ConfigUpdateRequest):
    if payload.quality is not None:
        config["quality"] = payload.quality
    if payload.fps is not None:
        config["fps"] = payload.fps
    if payload.shading is not None:
        config["shading"] = payload.shading
    return config


@router.get("/performance")
async def performance():
    return {"fps": 30, "frame_time_ms": 33.3, "gpu_load": 0.2}


@router.post("/render/sequence")
async def render_sequence(payload: RenderRequest):
    frames = []
    for idx in range(3):
        frame_id = f"{uuid.uuid4()}-{idx}"
        frames.append({"frame_id": frame_id, "frame_url": f"/renders/{frame_id}.{payload.format}"})
    return {"frames": frames}


@router.get("/{avatar_id}/snapshot")
async def get_snapshot(avatar_id: str):
    return {"avatar_id": avatar_id, "snapshot_url": f"/snapshots/{avatar_id}.png"}


@router.post("/{avatar_id}/snapshot")
async def create_snapshot(avatar_id: str, payload: SnapshotRequest | None = None):
    note = payload.note if payload else None
    snap_id = str(uuid.uuid4())
    return {"avatar_id": avatar_id, "snapshot_id": snap_id, "note": note}


@router.get("/assets")
async def list_assets():
    return {"assets": assets}


@router.post("/assets/upload")
async def upload_asset():
    asset_id = f"asset-{uuid.uuid4()}"
    assets.append({"asset_id": asset_id, "type": "custom", "label": "uploaded"})
    return {"asset_id": asset_id}


@router.get("/models")
async def list_models():
    return {"models": models}


@router.post("/models/select")
async def select_model(payload: ModelSelectRequest):
    avatar = _ensure_avatar(payload.avatar_id)
    avatar["state"]["model_id"] = payload.model_id
    return {"avatar_id": payload.avatar_id, "model_id": payload.model_id}


@router.post("/session")
async def create_session(payload: SessionCreateRequest):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"session_id": session_id, "avatar_id": payload.avatar_id, "metadata": payload.metadata or {}}
    return sessions[session_id]


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    removed = sessions.pop(session_id, None)
    return {"deleted": bool(removed), "session_id": session_id}


@router.post("/voice/attach")
async def attach_voice():
    return {"voice_attached": True}


@router.delete("/voice/detach")
async def detach_voice():
    return {"voice_attached": False}


@router.get("/voice/status")
async def voice_status():
    return {"voice_attached": True, "engine": "piper"}


@router.get("/status")
async def status():
    return {"renderer": "ready", "assets": len(assets), "models": len(models)}


@router.get("/version")
async def version():
    return {"service": "avatar", "version": "0.1.0"}


@router.post("/{avatar_id}/render")
async def render_avatar_id(avatar_id: str, payload: RenderRequest):
    _ensure_avatar(avatar_id)
    frame_id = str(uuid.uuid4())
    return {"avatar_id": avatar_id, "frame_id": frame_id, "frame_url": f"/renders/{frame_id}.{payload.format}"}


@router.post("/{avatar_id}/voice/attach")
async def attach_voice_avatar(avatar_id: str):
    avatar = _ensure_avatar(avatar_id)
    avatar["state"]["voice_attached"] = True
    return {"avatar_id": avatar_id, "voice_attached": True}


@router.delete("/{avatar_id}/voice/detach")
async def detach_voice_avatar(avatar_id: str):
    avatar = _ensure_avatar(avatar_id)
    avatar["state"]["voice_attached"] = False
    return {"avatar_id": avatar_id, "voice_attached": False}


@router.get("/{avatar_id}/voice/status")
async def voice_status_avatar(avatar_id: str):
    avatar = _ensure_avatar(avatar_id)
    return {"avatar_id": avatar_id, "voice_attached": avatar["state"].get("voice_attached", False)}


@router.post("/{avatar_id}/phonemes")
async def phonemes_avatar(avatar_id: str, payload: PhonemeRequest):
    seq = [{"p": "AH", "t": 0.0}, {"p": "V", "t": 0.08}]
    return {"avatar_id": avatar_id, "phonemes": seq, "text": payload.text}


@router.websocket("/{avatar_id}/stream")
async def stream_avatar(websocket: WebSocket, avatar_id: str):
    await websocket.accept()
    _ensure_avatar(avatar_id)
    try:
        await websocket.send_json({"avatar_id": avatar_id, "event": "connected"})
        # send a heartbeat then close
        await asyncio.sleep(0.01)
        await websocket.send_json({"avatar_id": avatar_id, "event": "heartbeat", "state": avatars[avatar_id].get("state", {})})
    except WebSocketDisconnect:
        return
    finally:
        await websocket.close()


@router.websocket("/session/{session_id}/stream")
async def stream_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    await websocket.send_json({"session_id": session_id, "event": "connected"})
    await websocket.send_json({"session_id": session_id, "event": "heartbeat"})
    await websocket.close()
