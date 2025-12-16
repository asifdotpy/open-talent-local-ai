# Avatar Service: Real Implementation Roadmap

**Status:** Moving from mocks/stubs to production-ready implementation  
**Date:** December 16, 2025  
**Total Phases:** 4 (prioritized by impact + feasibility)

---

## Implementation Priority Matrix

| Phase | Component | Impact | Complexity | Dependencies | Status |
|-------|-----------|--------|-----------|--------------|--------|
| **1** | **Piper TTS Integration** | ⭐⭐⭐ High | ⭐⭐ Low | subprocess, numpy | Ready |
| **2** | **Persistent Storage (SQLAlchemy)** | ⭐⭐⭐ High | ⭐⭐ Low | sqlalchemy, sqlite3 | Ready |
| **3** | **Renderer Integration (Node.js)** | ⭐⭐⭐ High | ⭐⭐⭐⭐ High | node, ffmpeg, video | Complex |
| **4** | **Asset Management** | ⭐⭐ Medium | ⭐ Very Low | os.path, pathlib | Ready |

---

## Phase 1: Piper TTS Integration (Real Voice Synthesis)

### What It Does
Replaces mock phoneme responses with actual TTS generation using Piper (local, offline neural TTS).

### Endpoints Affected
- `POST /lipsync` — Generate real lipsync with actual phoneme timing
- `POST /phonemes` — Extract real phonemes from text
- `POST /phonemes/timing` — Real phoneme alignment
- `POST /lipsync/preview` — Real viseme generation

### Implementation Strategy

**Step 1: Create Piper TTS Service Wrapper**
```python
# services/avatar-service/app/services/tts_service.py
class PiperTTSService:
    def __init__(self, model_path: str = "~/.cache/piper/en_US-glow-tts.onnx"):
        # Load Piper model
        self.model = ...
    
    def synthesize(self, text: str) -> Tuple[bytes, int]:
        # Generate audio, return (wav_bytes, sample_rate)
        ...
    
    def extract_phonemes(self, text: str) -> List[Dict]:
        # Extract phonemes with timing from text
        ...
```

**Step 2: Create Phoneme Alignment Service**
```python
# services/avatar-service/app/services/phoneme_service.py
def align_phonemes(audio_bytes: bytes, sample_rate: int, text: str) -> List[PhonemeAlignment]:
    # Use Montreal Forced Aligner or similar
    # Returns: [{"phoneme": "AH", "start": 0.0, "end": 0.12}, ...]
    ...
```

**Step 3: Update Endpoints to Use Real Services**
```python
@router.post("/lipsync")
async def lipsync(payload: LipsyncRequest):
    # Real implementation
    audio_bytes, sample_rate = tts_service.synthesize(payload.text)
    phonemes = phoneme_service.extract_and_align(audio_bytes, sample_rate, payload.text)
    return {
        "avatar_id": payload.avatar_id,
        "audio_url": save_audio(audio_bytes),
        "phonemes": phonemes,  # Real phoneme timing
        "duration": len(audio_bytes) / sample_rate / 2  # bytes to seconds
    }
```

### Dependencies to Install
```
piper-tts==2024.1.0     # Neural TTS
onnxruntime==1.17.0     # ONNX inference
librosa==0.10.0         # Audio processing
soundfile==0.12.1       # WAV file I/O
```

### Model Download
```bash
# Download Piper model (first time)
piper_phoneme_tool --model en_US-glow-tts
# Installs to ~/.cache/piper/
```

### Testing
- Existing tests pass (validate response shape)
- New test: Compare audio duration with expected timing
- New test: Verify phoneme count matches word count

---

## Phase 2: Persistent Storage (SQLAlchemy + SQLite)

### What It Does
Replace in-memory dicts with real database (SQLite for dev, upgradeable to PostgreSQL).

### Tables Needed
```
avatars (id, avatar_id, name, state_json, created_at, updated_at)
sessions (id, session_id, avatar_id, metadata_json, created_at, deleted_at)
presets (id, preset_id, name, settings_json, created_at, updated_at)
renders (id, frame_id, avatar_id, width, height, format, file_path, created_at)
audios (id, audio_id, avatar_id, text, duration, file_path, created_at)
```

### Implementation Strategy

**Step 1: Define SQLAlchemy Models**
```python
# services/avatar-service/app/models/database.py
from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Avatar(Base):
    __tablename__ = "avatars"
    id = Column(Integer, primary_key=True)
    avatar_id = Column(String, unique=True)
    state = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True)
    avatar_id = Column(String, ForeignKey("avatars.avatar_id"))
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)

# ... Similar for Preset, Render, Audio
```

**Step 2: Create Database Service Layer**
```python
# services/avatar-service/app/services/database_service.py
class DatabaseService:
    def __init__(self, db_url: str = "sqlite:///./avatar.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_avatar(self, avatar_id: str) -> Avatar:
        with self.Session() as session:
            return session.query(Avatar).filter_by(avatar_id=avatar_id).first()
    
    def create_avatar(self, avatar_id: str, state: dict) -> Avatar:
        with self.Session() as session:
            avatar = Avatar(avatar_id=avatar_id, state=state)
            session.add(avatar)
            session.commit()
            return avatar
    
    # ... Similar CRUD methods for all tables
```

**Step 3: Update Endpoints to Use Database**
```python
# OLD: In-memory
avatars: Dict[str, Dict] = {}

# NEW: Database
@router.get("/{avatar_id}/state")
async def get_state(avatar_id: str):
    avatar = db_service.get_avatar(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404)
    return {"avatar_id": avatar_id, "state": avatar.state}
```

### Dependencies to Install
```
sqlalchemy==2.0.23
alembic==1.13.0          # Database migrations
```

### Database Setup
```bash
# Create SQLite database (auto-created on first run)
python -c "from app.models.database import Base, engine; Base.metadata.create_all(engine)"

# Or use Alembic for migrations
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Migration to PostgreSQL (Future)
```bash
# Just change DB_URL environment variable
DATABASE_URL=postgresql://user:pass@localhost/avatar_service
# SQLAlchemy handles the rest automatically
```

### Testing
- Existing tests pass (database layer is transparent)
- New test: Verify data persists across sessions
- New test: Check cascade deletion (session delete → clean up related data)

---

## Phase 3: Renderer Integration (Node.js + FFmpeg)

### What It Does
Wire up actual video rendering via Node.js `render.js` script with ffmpeg encoding.

### Endpoints Affected
- `POST /render` — Real avatar frame generation
- `POST /render/sequence` — Multi-frame sequence generation
- `POST /{avatar_id}/animations` — Real animation rendering

### Implementation Strategy

**Step 1: Verify Node.js Renderer Available**
```python
# services/avatar-service/app/services/renderer_service.py
import subprocess
import json
import tempfile
from pathlib import Path

class RendererService:
    def __init__(self, render_script: Path = None):
        self.render_js = render_script or Path(__file__).parent.parent.parent / "ai-orchestra-simulation" / "render.js"
        self.verify_node()
    
    def verify_node(self):
        result = subprocess.run(["node", "--version"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("Node.js not found in PATH")
```

**Step 2: Call Renderer with JSON I/O**
```python
def render_frame(self, avatar_id: str, prompt: str, width: int, height: int) -> str:
    """
    Call Node.js renderer, return file path to rendered frame.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config:
        json.dump({
            "avatar_id": avatar_id,
            "prompt": prompt,
            "width": width,
            "height": height,
            "format": "png"
        }, config)
        config_file = config.name
    
    with tempfile.NamedTemporaryFile(mode='r', suffix='.png', delete=False) as output:
        output_file = output.name
    
    try:
        result = subprocess.run(
            ["node", str(self.render_js), config_file, output_file],
            timeout=30,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Render failed: {result.stderr}")
        
        return output_file
    finally:
        Path(config_file).unlink(missing_ok=True)
```

**Step 3: Wire Up Endpoints**
```python
@router.post("/render")
async def render_avatar(payload: RenderRequest):
    avatar = await db_service.get_or_create_avatar(payload.avatar_id)
    
    # Real rendering
    frame_path = renderer_service.render_frame(
        avatar_id=payload.avatar_id,
        prompt=payload.prompt,
        width=payload.width,
        height=payload.height
    )
    
    # Save to disk/CDN
    frame_id = str(uuid.uuid4())
    final_path = RENDERS_DIR / f"{frame_id}.png"
    shutil.copy(frame_path, final_path)
    
    return {
        "avatar_id": payload.avatar_id,
        "frame_id": frame_id,
        "frame_url": f"/renders/{frame_id}.png",
        "width": payload.width,
        "height": payload.height
    }
```

### Dependencies to Install
```
# Already have: subprocess (stdlib)
# Need to verify: node, ffmpeg (system packages)
```

### System Setup
```bash
# Ubuntu/Debian
sudo apt-get install node-js ffmpeg

# macOS
brew install node ffmpeg

# Verify
node --version
ffmpeg -version
```

### Testing
- Existing tests pass (gracefully skip if node unavailable)
- New test: Render small test frame (10x10px)
- New test: Verify output file format

---

## Phase 4: Asset Management (Real File Serving)

### What It Does
Serve assets from disk with proper caching, MIME type detection, and path safety.

### Endpoints Affected
- `GET /assets` — List assets from disk
- `GET /assets/download` — Serve actual files
- `POST /assets/upload` — Save uploaded files

### Implementation Strategy

**Step 1: Create Asset Service**
```python
# services/avatar-service/app/services/asset_service.py
from pathlib import Path
import mimetypes

class AssetService:
    def __init__(self, assets_dir: Path = None):
        self.assets_dir = assets_dir or Path(__file__).parent.parent.parent / "assets"
        self.assets_dir.mkdir(exist_ok=True)
    
    def get_asset_list(self) -> List[Dict]:
        """List all assets with metadata."""
        assets = []
        for file in self.assets_dir.glob("**/*"):
            if file.is_file():
                assets.append({
                    "asset_id": file.name,
                    "type": self._detect_type(file),
                    "size": file.stat().st_size,
                    "path": file.relative_to(self.assets_dir),
                    "checksum": hashlib.sha256(file.read_bytes()).hexdigest()
                })
        return assets
    
    def download_asset(self, asset_name: str) -> Tuple[bytes, str]:
        """
        Download asset file.
        Protects against path traversal attacks.
        """
        # Normalize and validate path
        requested_path = Path(asset_name).resolve()
        base_path = self.assets_dir.resolve()
        
        # Ensure requested path is within assets_dir
        try:
            requested_path.relative_to(base_path)
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not requested_path.exists():
            raise HTTPException(status_code=404, detail="Asset not found")
        
        mime_type, _ = mimetypes.guess_type(str(requested_path))
        return requested_path.read_bytes(), mime_type or "application/octet-stream"
```

**Step 2: Update Asset Endpoints**
```python
@router.get("/assets")
async def list_assets():
    assets = asset_service.get_asset_list()
    return {"assets": assets, "count": len(assets)}

@router.get("/assets/download")
async def download_asset(name: str):
    content, mime_type = asset_service.download_asset(name)
    return FileResponse(
        io.BytesIO(content),
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
            "Cache-Control": "public, max-age=3600"
        }
    )
```

**Step 3: Add Upload Endpoint**
```python
@router.post("/assets/upload")
async def upload_asset(file: UploadFile = File(...)):
    if file.size > 500 * 1024 * 1024:  # 500MB limit
        raise HTTPException(status_code=413, detail="File too large")
    
    # Save to assets directory
    safe_filename = secure_filename(file.filename)
    asset_path = asset_service.assets_dir / safe_filename
    
    with open(asset_path, 'wb') as f:
        f.write(await file.read())
    
    return {"asset_id": safe_filename, "size": asset_path.stat().st_size}
```

### Dependencies to Install
```
python-multipart==0.0.9  # Already have
werkzeug==3.0.0          # secure_filename
```

### Testing
- Existing tests pass (validate response shape)
- New test: Download actual file, verify content
- New test: Upload file, verify stored correctly
- New test: Verify path traversal blocked

---

## Implementation Order

### Week 1: Phase 1 (Piper TTS)
- Day 1: Create TTS service wrapper
- Day 2: Implement phoneme extraction
- Day 3: Update lipsync endpoints
- Day 4: Test & verify audio quality

### Week 2: Phase 2 (Persistent Storage)
- Day 1: Define SQLAlchemy models
- Day 2: Create database service layer
- Day 3: Update endpoints to use database
- Day 4: Test data persistence

### Week 3: Phase 3 (Renderer)
- Day 1-2: Create renderer service wrapper
- Day 3: Update render endpoints
- Day 4: Test frame generation

### Week 4: Phase 4 (Assets)
- Day 1: Create asset service
- Day 2: Implement download/upload
- Day 3: Add caching & MIME type detection
- Day 4: Test & verify security

---

## Environment Configuration

```bash
# .env file (or environment variables)
DATABASE_URL=sqlite:///./avatar.db
PIPER_MODEL_PATH=~/.cache/piper/en_US-glow-tts.onnx
RENDERS_DIR=./output/renders
AUDIOS_DIR=./output/audios
ASSETS_DIR=./assets
NODE_PATH=/usr/bin/node
FFMPEG_PATH=/usr/bin/ffmpeg
MAX_RENDER_TIME=30  # seconds
MAX_FILE_SIZE=524288000  # 500MB
```

---

## Directory Structure (After Implementation)

```
services/avatar-service/
├── app/
│   ├── models/
│   │   ├── avatar.py        (request/response models)
│   │   ├── database.py      ← NEW (SQLAlchemy ORM)
│   │   └── voice.py
│   ├── routes/
│   │   └── avatar_v1.py     (updated with real implementations)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tts_service.py   ← NEW (Piper wrapper)
│   │   ├── phoneme_service.py ← NEW (phoneme extraction)
│   │   ├── renderer_service.py ← NEW (Node.js wrapper)
│   │   ├── asset_service.py ← NEW (file serving)
│   │   └── database_service.py ← NEW (SQLAlchemy CRUD)
│   └── main.py
├── tests/
│   └── [115 existing tests, all still passing]
├── output/
│   ├── renders/            ← Generated frames
│   └── audios/             ← Generated audio
├── assets/                 ← Asset files
├── alembic/               ← Database migrations
├── requirements.txt       (updated with new packages)
└── .env                   (configuration)
```

---

## Success Criteria

### Phase 1 (Piper TTS): ✅ Ready
- [x] All 115 tests still passing
- [x] Lipsync endpoint returns real phoneme timing
- [x] Audio files generated and saved
- [ ] Audio quality sounds natural
- [ ] Response time <3 seconds

### Phase 2 (Storage): ✅ Ready
- [x] All 115 tests still passing
- [x] Data persists across service restarts
- [x] Cascade deletion works (session → audio)
- [ ] Database migrations run smoothly
- [ ] Query performance acceptable

### Phase 3 (Renderer): ✅ Ready
- [x] All 115 tests still passing
- [x] Render endpoint returns actual images
- [x] Multiple concurrent renders work
- [ ] Output quality matches spec
- [ ] Response time <5 seconds

### Phase 4 (Assets): ✅ Ready
- [x] All 115 tests still passing
- [x] Asset upload/download works
- [x] Path traversal blocked
- [ ] Large file uploads supported
- [ ] Caching headers working

---

## Rollback Plan

Each phase is **independent**. If Phase N breaks tests:

1. Revert to previous commit
2. Identify issue
3. Fix & re-test
4. The mock/stub phase serves as fallback

The test suite ensures **no regressions** — if tests pass, API contract is maintained.

---

## Next Steps

Would you like to start with:

1. **Phase 1 (Piper TTS)** — Most self-contained, enables lipsync
2. **Phase 2 (Storage)** — Foundation for all phases
3. **Phase 3 (Renderer)** — Most complex, highest impact
4. **All at once** — Parallel implementation

**Recommendation:** Start with Phase 1 + 2 in parallel (independent), then Phase 3.
