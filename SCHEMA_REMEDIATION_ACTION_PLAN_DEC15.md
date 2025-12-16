# API Schema Remediation Action Plan
**Date:** December 15, 2025  
**Status:** Ready for Implementation  

---

## 🎯 Priority-Based Action Plan

### PRIORITY 1: CRITICAL - Security Services (Must Fix Before Production)

#### 1.1 security-service - Add Comprehensive Auth Schemas
**File:** `/home/asif1/open-talent/services/security-service/schemas.py` (CREATE NEW)

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Authentication Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class VerifyTokenRequest(BaseModel):
    token: str

class UserProfile(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime

# MFA Models
class MFASetupRequest(BaseModel):
    method: str  # "totp" or "sms"

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: Optional[str]
    method: str

class MFAVerifyRequest(BaseModel):
    code: str
    method: str

# Password Management
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

# Encryption Models
class EncryptRequest(BaseModel):
    data: str
    key: Optional[str]

class EncryptResponse(BaseModel):
    encrypted: str
    algorithm: str

class DecryptRequest(BaseModel):
    encrypted: str
    key: Optional[str]

class DecryptResponse(BaseModel):
    data: str

# Authorization Models
class PermissionCheckRequest(BaseModel):
    user_id: str
    resource: str
    action: str

class PermissionCheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str]

class RoleAssignmentRequest(BaseModel):
    user_id: str
    role: str

class RoleInfo(BaseModel):
    role_id: str
    name: str
    permissions: List[str]
    created_at: datetime
```

**Endpoints to Apply Schemas:**
- POST /api/v1/auth/register → RegisterRequest, UserProfile
- POST /api/v1/auth/login → LoginRequest, LoginResponse
- POST /api/v1/auth/refresh → TokenRefreshRequest, LoginResponse
- POST /api/v1/auth/verify → VerifyTokenRequest, dict (verified: bool)
- GET /api/v1/auth/profile → UserProfile
- POST /api/v1/auth/mfa/setup → MFASetupRequest, MFASetupResponse
- POST /api/v1/auth/mfa/verify → MFAVerifyRequest, dict (verified: bool)
- DELETE /api/v1/auth/mfa → dict (status: string)
- POST /api/v1/auth/password/change → PasswordChangeRequest, dict (status: string)
- POST /api/v1/auth/password/reset-request → PasswordResetRequest, dict (status: string)
- POST /api/v1/auth/password/reset → PasswordResetConfirm, dict (status: string)
- POST /api/v1/encrypt → EncryptRequest, EncryptResponse
- POST /api/v1/decrypt → DecryptRequest, DecryptResponse
- GET /api/v1/auth/permissions → List[str]
- POST /api/v1/auth/permissions/check → PermissionCheckRequest, PermissionCheckResponse
- GET /api/v1/roles → List[RoleInfo]
- POST /api/v1/roles/assign → RoleAssignmentRequest, dict (status: string)
- DELETE /api/v1/roles/revoke → dict (status: string)

**Time Estimate:** 2-3 hours

---

#### 1.2 notification-service - Add Notification Schemas
**File:** `/home/asif1/open-talent/services/notification-service/schemas.py` (CREATE NEW)

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

# Email Notifications
class EmailRecipient(BaseModel):
    address: EmailStr
    name: Optional[str]

class EmailNotificationRequest(BaseModel):
    recipients: List[EmailRecipient]
    subject: str
    body: str
    html_body: Optional[str]
    template_id: Optional[str]
    variables: Optional[Dict[str, Any]]
    priority: Optional[str] = "normal"

class EmailNotificationResponse(BaseModel):
    notification_id: str
    status: NotificationStatus
    sent_at: str
    recipients_count: int

# SMS Notifications
class SMSNotificationRequest(BaseModel):
    phone_numbers: List[str]
    message: str
    template_id: Optional[str]
    variables: Optional[Dict[str, Any]]
    priority: Optional[str] = "normal"

class SMSNotificationResponse(BaseModel):
    notification_id: str
    status: NotificationStatus
    sent_at: str
    recipients_count: int

# Push Notifications
class PushNotificationRequest(BaseModel):
    user_ids: List[str]
    title: str
    body: str
    data: Optional[Dict[str, Any]]
    action_url: Optional[str]
    priority: Optional[str] = "high"

class PushNotificationResponse(BaseModel):
    notification_id: str
    status: NotificationStatus
    sent_at: str
    recipients_count: int

# Templates
class NotificationTemplate(BaseModel):
    template_id: str
    name: str
    subject: Optional[str]
    body: str
    type: str  # "email", "sms", "push"
    variables: List[str]

class TemplateListResponse(BaseModel):
    templates: List[NotificationTemplate]
    total: int

# Provider Info
class ProviderInfo(BaseModel):
    provider: str
    status: str
    config: Dict[str, Any]
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
```

**Endpoints to Apply Schemas:**
- POST /api/v1/notify/email → EmailNotificationRequest, EmailNotificationResponse
- POST /api/v1/notify/sms → SMSNotificationRequest, SMSNotificationResponse
- POST /api/v1/notify/push → PushNotificationRequest, PushNotificationResponse
- GET /api/v1/notify/templates → TemplateListResponse
- GET /api/v1/provider → ProviderInfo

**Time Estimate:** 1-2 hours

---

### PRIORITY 2: HIGH - Voice Service WebSocket Documentation

#### 2.1 voice-service - Add WebSocket Message Schemas
**File:** `/home/asif1/open-talent/services/voice-service/schemas.py` (CREATE NEW or UPDATE main.py)

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Speech-to-Text WebSocket Messages
class STTStreamRequest(BaseModel):
    audio_chunk: bytes  # Base64 encoded audio
    sample_rate: int = 16000
    encoding: str = "linear16"
    language_code: str = "en-US"
    session_id: str

class STTStreamResponse(BaseModel):
    session_id: str
    transcript: str
    is_final: bool
    confidence: Optional[float]
    timestamp: str

# Text-to-Speech WebSocket Messages
class TTSStreamRequest(BaseModel):
    text: str
    voice_id: str
    language: str = "en-US"
    speed: float = 1.0
    session_id: str

class TTSStreamResponse(BaseModel):
    session_id: str
    audio_chunk: bytes  # Base64 encoded audio
    is_final: bool
    timestamp: str

# WebRTC Signaling Messages
class WebRTCOffer(BaseModel):
    type: str = "offer"
    sdp: str
    session_id: str

class WebRTCAnswer(BaseModel):
    type: str = "answer"
    sdp: str
    session_id: str

class WebRTCIceCandidate(BaseModel):
    type: str = "candidate"
    candidate: str
    sdp_mid: str
    sdp_mline_index: int
    session_id: str

class WebRTCSignalingMessage(BaseModel):
    type: str  # "offer", "answer", "candidate"
    data: Dict[str, Any]
    session_id: str
```

**Endpoints to Apply Schemas:**
- WebSocket /voice/ws/stt → STTStreamRequest (in), STTStreamResponse (out)
- WebSocket /voice/ws/tts → TTSStreamRequest (in), TTSStreamResponse (out)
- WebSocket /webrtc/signal → WebRTCSignalingMessage (in/out)

**Time Estimate:** 1 hour

---

### PRIORITY 3: HIGH - Avatar Service New Endpoints

#### 3.1 avatar-service - Add Schema for New Endpoints
**File:** `/home/asif1/open-talent/services/avatar-service/app/models/avatar.py` (UPDATE)

```python
from pydantic import BaseModel
from typing import Optional, List, Dict

# Lipsync Rendering
class LipsyncRequest(BaseModel):
    audio_url: str
    avatar_id: str
    animation_speed: Optional[float] = 1.0
    quality: Optional[str] = "medium"  # "low", "medium", "high"

class LipsyncResponse(BaseModel):
    animation_id: str
    duration: float
    phoneme_sequence: List[str]
    status: str = "completed"

# Avatar Generation
class AvatarGenerationRequest(BaseModel):
    style: str  # "realistic", "cartoon", "anime"
    name: str
    characteristics: Optional[Dict[str, str]]
    
class AvatarGenerationResponse(BaseModel):
    avatar_id: str
    model_url: str
    status: str = "created"

# Phoneme Mapping
class PhonemeMappingRequest(BaseModel):
    phoneme_sequence: List[str]
    animation_style: str
    
class PhonemeMappingResponse(BaseModel):
    animation_frames: List[Dict[str, float]]
    total_duration: float
```

**Endpoints to Apply Schemas:**
- POST /render/lipsync → LipsyncRequest, LipsyncResponse
- POST /generate → AvatarGenerationRequest, AvatarGenerationResponse
- POST /set-phonemes → PhonemeMappingRequest, PhonemeMappingResponse

**Time Estimate:** 1 hour

---

### PRIORITY 4: MEDIUM - Interview Service WebSocket Documentation

#### 4.1 interview-service - Document WebSocket Formats
**File:** `/home/asif1/open-talent/services/interview-service/app/schemas/websocket.py` (CREATE NEW)

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Transcription WebSocket Messages
class TranscriptionUpdate(BaseModel):
    room_id: str
    timestamp: datetime
    speaker: str
    text: str
    is_final: bool
    confidence: Optional[float]

class TranscriptionMessage(BaseModel):
    type: str  # "partial" or "final"
    data: TranscriptionUpdate

# WebRTC Signaling Messages
class WebRTCSignalingMessage(BaseModel):
    type: str  # "offer", "answer", "candidate"
    room_id: str
    from_participant: str
    to_participant: str
    payload: Dict[str, Any]
    timestamp: datetime

class WebRTCSignalData(BaseModel):
    type: str = "signal"
    data: WebRTCSignalingMessage
```

**WebSocket Endpoints to Document:**
- WebSocket /ws/transcription/{room_id} → TranscriptionMessage (out)
- WebSocket /webrtc/signal → WebRTCSignalingMessage (in/out)

**Time Estimate:** 30 minutes

---

### PRIORITY 5: MEDIUM - Low Coverage Services

#### 5.1 voice-service - Add Missing Request Models
**Add to main.py or create voice_models.py:**

```python
class TTSOptions(BaseModel):
    language: str = "en-US"
    gender: Optional[str]  # "male", "female"
    speed: float = 1.0  # 0.5 to 2.0
    pitch: float = 1.0  # 0.5 to 2.0
    volume: float = 1.0  # 0.0 to 2.0

class VADOptions(BaseModel):
    threshold: float = 0.5
    min_duration: float = 0.3
    max_silence: float = 1.0

class WebRTCAudioConfig(BaseModel):
    codec: str = "opus"
    bitrate: int = 32000
    sample_rate: int = 16000
    channels: int = 1
```

**Endpoints to Update:**
- POST /voice/tts → Add full request model with TTSOptions
- POST /voice/vad → Update VADRequest with complete fields

**Time Estimate:** 30 minutes

---

#### 5.2 user-service - Add Contact Info Models
**File:** `/home/asif1/open-talent/services/user-service/app/schemas.py` (UPDATE)

```python
class EmailAddress(BaseModel):
    address: EmailStr
    is_primary: bool = False
    is_verified: bool = False
    verified_at: Optional[datetime]

class PhoneNumber(BaseModel):
    number: str
    country_code: str
    is_primary: bool = False
    is_verified: bool = False
    verified_at: Optional[datetime]

class ContactInfo(BaseModel):
    emails: List[EmailAddress]
    phones: List[PhoneNumber]
```

**Time Estimate:** 30 minutes

---

#### 5.3 avatar-service - Complete Schema Coverage
**Add missing endpoint schemas:**

```python
class GenerateAvatarRequest(BaseModel):
    name: str
    style: str
    gender: str

class SetPhonemesRequest(BaseModel):
    avatar_id: str
    phoneme_mapping: Dict[str, str]

class GenerateFromAudioRequest(BaseModel):
    audio_url: str
    avatar_style: str
```

**Time Estimate:** 30 minutes

---

## Implementation Timeline

| Priority | Service | Task | Time | Status |
|----------|---------|------|------|--------|
| 1 | security-service | Create schemas.py | 2-3h | 🔴 PENDING |
| 1 | notification-service | Create schemas.py | 1-2h | 🔴 PENDING |
| 2 | voice-service | Add WebSocket schemas | 1h | 🔴 PENDING |
| 2 | interview-service | Document WebSocket | 30m | 🔴 PENDING |
| 3 | avatar-service | Update for new endpoints | 1h | 🔴 PENDING |
| 4 | voice-service | Add request models | 30m | 🔴 PENDING |
| 4 | user-service | Add contact models | 30m | 🔴 PENDING |
| 4 | avatar-service | Complete coverage | 30m | 🔴 PENDING |

**Total Estimated Time:** 7-9 hours for full implementation

---

## Testing Checklist

### For Each Schema Addition:
- [ ] Create test file for schema validation
- [ ] Test valid request/response serialization
- [ ] Test invalid data rejection
- [ ] Update API documentation
- [ ] Update Swagger/OpenAPI spec
- [ ] Test endpoint returns correct status code
- [ ] Verify response conforms to schema

### Example Test:
```python
def test_auth_register_schema():
    valid_request = {
        "email": "user@example.com",
        "password": "securepass123",
        "first_name": "John",
        "last_name": "Doe"
    }
    schema = RegisterRequest(**valid_request)
    assert schema.email == "user@example.com"

def test_auth_register_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="invalid-email",
            password="securepass123",
            first_name="John",
            last_name="Doe"
        )
```

---

## Deployment Strategy

1. **Week 1:** Priority 1 schemas (security, notification)
2. **Week 2:** Priority 2 schemas (voice, interview WebSocket)
3. **Week 3:** Priority 3-5 (avatar, user, voice remaining)
4. **Week 4:** Testing, documentation, and validation

---

## Success Criteria

- [ ] All 271 endpoints have associated response_model
- [ ] All endpoints with body payloads have request schemas
- [ ] All schemas documented in OpenAPI spec
- [ ] 100% schema coverage (from current 66.8%)
- [ ] All WebSocket message formats documented
- [ ] Integration tests for all new schemas passing
- [ ] API documentation auto-generated and current

---

**Generated:** December 15, 2025  
**Next Review:** After completing Priority 1 items
