# Complete API Endpoint Inventory - OpenTalent Platform

> **Date:** December 17, 2025  
> **Status:** Consolidated from all documentation sources  
> **Total Services:** 18  
> **Total Endpoints:** 271+ (verified from audit)

---

## 📊 Executive Summary

| Service | Endpoints | Port | Schema Coverage | Status | Tier |
|---------|-----------|------|-----------------|--------|------|
| **Candidate Service** | 76 | 8008 | 105% (40/38) | ✅ Production | 1 |
| **Interview Service** | 49 | 8004-8005 | 94% (45/48) | ✅ Production | 1 |
| **Avatar Service** | 46 (runtime) | 8001 | 88% (23/26) | 🟢 Runtime Verified | 1 |
| **Voice Service** | 60 | 8015 | 20% (6/29) | ✅ Gateway Proxy Fixed | 3 |
| **Security Service** | 42 | 8010 | 100% (21/21) | ✅ Complete | 2 |
| **User Service** | 35 | 8001/8007 | 26% (9/35) | 🟡 Partial | 3 |
| **Conversation Service** | 19 | 8003 | 58% (11/19) | 🟡 Good | 2 |
| **Scout Service** | 15 (runtime) | 8010 | 68% (15/22) | 🟢 Runtime Verified | 2 |
| **Analytics Service** | 16 (runtime) | 8017 | 78% (14/18) | 🟢 Runtime Verified | 2 |
| **Explainability Service** | 18 | 8014 | 50% (8/16) | 🟡 Partial | 2 |
| **Granite Interview** | 24 | TBD | 41% (7/17) | 🟡 Partial | 2 |
| **Desktop Integration** | 26 | 8009 | 100% (6/6) | ✅ Gateway with Schemas | 1 |
| **Notification Service** | 14 | 8011 | 100% (7/7) | ✅ Production | 1 |
| **AI-Auditing Service** | 9 | 8012 | 0% (0/15) | 🟢 Expanded | 3 |
| **Project Service** | 6 | TBD | Unknown | 🟡 Partial | 2 |
| **Audio Service** | 0 | TBD | N/A | ⚠️ No Coverage | - |
| **Shared Module** | 8 | N/A | 0% (0/8) | 🟡 Partial | 3 |

**Legend:**
- ✅ Production-Ready | 🟢 Recently Updated | 🟡 Partial Coverage | ⚠️ No Implementation
- Tier 1: 96.4% coverage | Tier 2: 59.8% coverage | Tier 3: 14.9% coverage

---

## 1. CANDIDATE SERVICE (Port 8008)

**Status:** ✅ Production-Ready | **Tier:** 1 | **Endpoints:** 76 | **Schema Coverage:** 105%

### Core Operations (8 endpoints)
```
GET    /api/v1/candidates                    # List all candidates
POST   /api/v1/candidates                    # Create new candidate
GET    /api/v1/candidates/{id}               # Get candidate by ID
PUT    /api/v1/candidates/{id}               # Update candidate
PATCH  /api/v1/candidates/{id}               # Partial update
DELETE /api/v1/candidates/{id}               # Delete candidate
GET    /api/v1/candidates/{id}/status        # Get candidate status
PUT    /api/v1/candidates/{id}/status        # Update candidate status
```

### Search & Filtering (12 endpoints)
```
POST   /api/v1/candidates/search             # Advanced search
POST   /api/v1/candidates/search/filters     # Get available filters
POST   /api/v1/candidates/search/advanced    # Complex queries
GET    /api/v1/candidates/filter             # Apply filters
POST   /api/v1/candidates/bulk-search        # Batch search
GET    /api/v1/candidates/aggregate          # Aggregation queries
POST   /api/v1/candidates/filter/save        # Save filter preset
GET    /api/v1/candidates/filter/presets     # List saved filters
DELETE /api/v1/candidates/filter/presets/{id} # Delete filter preset
GET    /api/v1/candidates/search/suggestions # Search suggestions
POST   /api/v1/candidates/search/fuzzy       # Fuzzy matching
GET    /api/v1/candidates/search/recent      # Recent searches
```

### Profile Management (18 endpoints)
```
GET    /api/v1/candidates/{id}/profile       # Get full profile
PUT    /api/v1/candidates/{id}/profile       # Update full profile
PATCH  /api/v1/candidates/{id}/profile       # Partial profile update
POST   /api/v1/candidates/{id}/profile/validate # Validate profile data
GET    /api/v1/candidates/{id}/resume        # Get resume
POST   /api/v1/candidates/{id}/resume/upload # Upload resume
DELETE /api/v1/candidates/{id}/resume        # Delete resume
GET    /api/v1/candidates/{id}/resume/parse  # Parse resume
GET    /api/v1/candidates/{id}/skills        # Get skills list
POST   /api/v1/candidates/{id}/skills        # Add skills
DELETE /api/v1/candidates/{id}/skills/{skill_id} # Remove skill
GET    /api/v1/candidates/{id}/experience    # Get work experience
POST   /api/v1/candidates/{id}/experience    # Add experience
PUT    /api/v1/candidates/{id}/experience/{exp_id} # Update experience
DELETE /api/v1/candidates/{id}/experience/{exp_id} # Delete experience
GET    /api/v1/candidates/{id}/education     # Get education
POST   /api/v1/candidates/{id}/education     # Add education
DELETE /api/v1/candidates/{id}/education/{edu_id} # Delete education
```

### Interview Integration (12 endpoints)
```
GET    /api/v1/candidates/{id}/interviews    # List interviews
POST   /api/v1/candidates/{id}/interviews/schedule # Schedule interview
GET    /api/v1/candidates/{id}/interviews/{interview_id} # Get interview details
PUT    /api/v1/candidates/{id}/interviews/{interview_id} # Update interview
DELETE /api/v1/candidates/{id}/interviews/{interview_id} # Cancel interview
GET    /api/v1/candidates/{id}/interviews/history # Interview history
POST   /api/v1/candidates/{id}/interviews/feedback # Submit feedback
GET    /api/v1/candidates/{id}/interviews/feedback # Get feedback
GET    /api/v1/candidates/{id}/interviews/results # Get results
POST   /api/v1/candidates/{id}/interviews/reschedule # Reschedule
GET    /api/v1/candidates/{id}/interviews/upcoming # Upcoming interviews
GET    /api/v1/candidates/{id}/interviews/past  # Past interviews
```

### Analytics Integration (10 endpoints)
```
GET    /api/v1/candidates/{id}/analytics     # Get analytics
GET    /api/v1/candidates/{id}/performance   # Performance metrics
GET    /api/v1/candidates/{id}/scores        # Assessment scores
POST   /api/v1/candidates/{id}/assessment    # Create assessment
GET    /api/v1/candidates/{id}/assessment/{assessment_id} # Get assessment
GET    /api/v1/candidates/{id}/reports       # Generate reports
POST   /api/v1/candidates/{id}/compare       # Compare candidates
GET    /api/v1/candidates/{id}/insights      # AI insights
GET    /api/v1/candidates/{id}/trends        # Trend analysis
GET    /api/v1/candidates/{id}/predictions   # Success predictions
```

### Application Management (10 endpoints)
```
GET    /api/v1/candidates/{id}/applications  # List applications
POST   /api/v1/candidates/{id}/applications  # Create application
GET    /api/v1/candidates/{id}/applications/{app_id} # Get application
PUT    /api/v1/candidates/{id}/applications/{app_id} # Update application
DELETE /api/v1/candidates/{id}/applications/{app_id} # Delete application
PATCH  /api/v1/candidates/{id}/applications/{app_id}/status # Update status
GET    /api/v1/candidates/{id}/applications/active # Active applications
GET    /api/v1/candidates/{id}/applications/history # Application history
POST   /api/v1/candidates/{id}/applications/withdraw # Withdraw application
GET    /api/v1/candidates/{id}/applications/timeline # Application timeline
```

### Health & Utilities (6 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/candidates/stats              # Global statistics
POST   /api/v1/candidates/batch              # Batch operations
POST   /api/v1/candidates/export             # Export candidates
POST   /api/v1/candidates/import             # Import candidates
```

---

## 2. INTERVIEW SERVICE (Port 8004-8005)

**Status:** ✅ Production-Ready | **Tier:** 1 | **Endpoints:** 49 | **Schema Coverage:** 94%

### Room Management (12 endpoints)
```
POST   /api/v1/rooms/create                  # Create interview room
POST   /api/v1/rooms/{room_id}/join          # Join room
POST   /api/v1/rooms/{room_id}/leave         # Leave room
POST   /api/v1/rooms/{room_id}/end           # End room session
GET    /api/v1/rooms/{room_id}/status        # Get room status
GET    /api/v1/rooms/{room_id}/participants  # List participants
POST   /api/v1/rooms/{room_id}/invite        # Invite participant
POST   /api/v1/rooms/{room_id}/remove-participant # Remove participant
GET    /api/v1/rooms/active                  # List active rooms
GET    /api/v1/rooms/{room_id}/metadata      # Get room metadata
PUT    /api/v1/rooms/{room_id}/settings      # Update room settings
DELETE /api/v1/rooms/{room_id}               # Delete room
```

### WebRTC Signaling (8 endpoints)
```
POST   /api/v1/rooms/{room_id}/webrtc/offer  # Send WebRTC offer
POST   /api/v1/rooms/{room_id}/webrtc/answer # Send WebRTC answer
POST   /api/v1/rooms/{room_id}/webrtc/ice-candidate # Exchange ICE candidate
GET    /api/v1/rooms/{room_id}/webrtc/status # Get WebRTC status
POST   /api/v1/rooms/{room_id}/webrtc/renegotiate # Renegotiate connection
POST   /api/v1/rooms/{room_id}/webrtc/stats  # Get connection stats
POST   /api/v1/rooms/{room_id}/webrtc/restart # Restart connection
DELETE /api/v1/rooms/{room_id}/webrtc/peer/{peer_id} # Remove peer
```

### Transcription (6 endpoints)
```
POST   /api/v1/rooms/{room_id}/transcription/start # Start transcription
POST   /api/v1/rooms/{room_id}/transcription/stop # Stop transcription
GET    /api/v1/rooms/{room_id}/transcription # Get transcription
PUT    /api/v1/rooms/{room_id}/transcription # Update transcription
DELETE /api/v1/rooms/{room_id}/transcription # Delete transcription
GET    /api/v1/rooms/{room_id}/transcription/export # Export transcription
```

### Question Generation (7 endpoints)
```
POST   /api/v1/rooms/{room_id}/next-question # Generate next question
GET    /api/v1/rooms/{room_id}/questions     # List all questions
GET    /api/v1/rooms/{room_id}/questions/{question_id} # Get specific question
POST   /api/v1/rooms/{room_id}/questions/history # Question history
POST   /api/v1/rooms/{room_id}/analyze-response # Analyze candidate response
POST   /api/v1/rooms/{room_id}/adapt-interview # Adapt interview strategy
GET    /api/v1/rooms/{room_id}/questions/suggested # Get suggested questions
```

### Assessment & Scoring (10 endpoints)
```
POST   /api/v1/rooms/{room_id}/assessment    # Create assessment
GET    /api/v1/rooms/{room_id}/assessment    # Get assessment
PUT    /api/v1/rooms/{room_id}/assessment    # Update assessment
POST   /api/v1/rooms/{room_id}/scoring       # Submit scores
GET    /api/v1/rooms/{room_id}/scoring       # Get scores
POST   /api/v1/rooms/{room_id}/feedback      # Submit feedback
GET    /api/v1/rooms/{room_id}/feedback      # Get feedback
POST   /api/v1/rooms/{room_id}/evaluation    # Final evaluation
GET    /api/v1/rooms/{room_id}/report        # Generate report
GET    /api/v1/rooms/{room_id}/summary       # Get session summary
```

### Health & Utilities (6 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/rooms/statistics              # Global statistics
POST   /api/v1/rooms/batch                   # Batch operations
GET    /api/v1/rooms/history                 # Historical data
GET    /api/v1/system/config                 # System configuration
```

---

## 3. AVATAR SERVICE (Port 8001)

**Status:** ✅ Refactored (Dec 16) | **Tier:** 1 | **Endpoints:** 43+ | **Schema Coverage:** 88%

### Root Level (13 endpoints)
```
GET    /                                     # Service info (US English voice)
GET    /ping                                 # Load balancer health check
GET    /doc                                  # Redirect to /docs
GET    /api-docs                             # API documentation
GET    /health                               # Health check with voice integration
POST   /render/lipsync                       # Render avatar with lip-sync
POST   /api/v1/generate-voice                # Generate US English voice
GET    /api/v1/voices                        # List US voices
GET    /docs                                 # Swagger UI
GET    /redoc                                # ReDoc documentation
GET    /openapi.json                         # OpenAPI schema
GET    /src/{path:path}                      # Serve source files (secure)
GET    /assets/{path:path}                   # Serve asset files
```

### Avatar V1 Router (/api/v1/avatars) (30+ endpoints)

#### Rendering (5 endpoints)
```
POST   /api/v1/avatars/render                # Render avatar
POST   /api/v1/avatars/{avatar_id}/render    # Render specific avatar
POST   /api/v1/avatars/render/sequence       # Render animation sequence
POST   /api/v1/avatars/render/batch          # Batch rendering
GET    /api/v1/avatars/render/status/{job_id} # Get render status
```

#### Lip-Sync (4 endpoints)
```
POST   /api/v1/avatars/lipsync               # Generate lip-sync
POST   /api/v1/avatars/lipsync/preview       # Preview lip-sync
POST   /api/v1/avatars/{avatar_id}/lipsync   # Avatar-specific lip-sync
GET    /api/v1/avatars/lipsync/phonemes      # Get phoneme mappings
```

#### Phonemes (4 endpoints)
```
POST   /api/v1/avatars/phonemes              # Generate phonemes from audio
POST   /api/v1/avatars/phonemes/timing       # Get phoneme timing
POST   /api/v1/avatars/{avatar_id}/phonemes  # Set avatar phonemes
GET    /api/v1/avatars/phonemes/list         # List supported phonemes
```

#### Presets (4 endpoints)
```
GET    /api/v1/avatars/presets               # List avatar presets
POST   /api/v1/avatars/presets               # Create preset
GET    /api/v1/avatars/presets/{preset_id}   # Get preset
PATCH  /api/v1/avatars/presets/{preset_id}   # Update preset
DELETE /api/v1/avatars/presets/{preset_id}   # Delete preset
```

#### Customization (3 endpoints)
```
POST   /api/v1/avatars/customize             # Customize avatar appearance
GET    /api/v1/avatars/{avatar_id}/config    # Get avatar config
PUT    /api/v1/avatars/{avatar_id}/config    # Update avatar config
```

#### State Management (4 endpoints)
```
GET    /api/v1/avatars/{avatar_id}/state     # Get avatar state
PATCH  /api/v1/avatars/{avatar_id}/state     # Update avatar state
POST   /api/v1/avatars/{avatar_id}/reset     # Reset avatar state
GET    /api/v1/avatars/{avatar_id}/history   # Get state history
```

#### Emotions (3 endpoints)
```
GET    /api/v1/avatars/{avatar_id}/emotions  # Get current emotions
PATCH  /api/v1/avatars/{avatar_id}/emotions  # Update emotions
POST   /api/v1/avatars/{avatar_id}/emotions/transition # Transition emotion
```

#### Animations (3 endpoints)
```
POST   /api/v1/avatars/{avatar_id}/animations # Trigger animation
GET    /api/v1/avatars/animations/list       # List available animations
GET    /api/v1/avatars/{avatar_id}/animations/current # Get current animation
```

---

## 4. VOICE SERVICE (Port 8015)

**Status:** 🟡 Partial Coverage | **Tier:** 3 | **Endpoints:** 60 | **Schema Coverage:** 14%

### Core Voice Operations (12 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /voices                               # List available TTS voices
GET    /info                                 # Detailed service info
POST   /voice/stt                            # Speech-to-Text
POST   /voice/tts                            # Text-to-Speech
POST   /voice/tts/synthesize                 # Advanced TTS
GET    /voice/tts/voices                     # TTS voice catalog
POST   /voice/tts/preview                    # Preview voice
GET    /voice/stt/languages                  # Supported languages
POST   /voice/stt/transcribe                 # Transcribe audio file
GET    /voice/stt/models                     # Available STT models
```

### Voice Configuration (8 endpoints)
```
GET    /voice/config                         # Get configuration
PUT    /voice/config                         # Update configuration
GET    /voice/config/defaults                # Get default config
POST   /voice/config/validate                # Validate configuration
GET    /voice/config/voices/{voice_id}       # Get voice details
PUT    /voice/config/voices/{voice_id}       # Update voice settings
POST   /voice/config/voices/test             # Test voice settings
GET    /voice/config/quality                 # Get quality settings
```

### Audio Processing (10 endpoints)
```
POST   /audio/process                        # Process audio file
POST   /audio/enhance                        # Enhance audio quality
POST   /audio/normalize                      # Normalize volume
POST   /audio/denoise                        # Remove background noise
POST   /audio/convert                        # Convert audio format
GET    /audio/formats                        # Supported formats
POST   /audio/split                          # Split audio file
POST   /audio/merge                          # Merge audio files
POST   /audio/extract                        # Extract audio features
GET    /audio/metadata                       # Get audio metadata
```

### WebRTC Integration (8 endpoints)
```
POST   /webrtc/connect                       # Establish WebRTC connection
POST   /webrtc/disconnect                    # Close WebRTC connection
POST   /webrtc/offer                         # Send WebRTC offer
POST   /webrtc/answer                        # Send WebRTC answer
POST   /webrtc/ice-candidate                 # Exchange ICE candidate
GET    /webrtc/status                        # Get connection status
POST   /webrtc/audio/stream                  # Stream audio via WebRTC
GET    /webrtc/peers                         # List connected peers
```

### Phoneme Extraction (6 endpoints)
```
POST   /phonemes/extract                     # Extract phonemes from audio
POST   /phonemes/extract/text                # Extract from text
GET    /phonemes/mappings                    # Get phoneme mappings
POST   /phonemes/timing                      # Get phoneme timing
POST   /phonemes/validate                    # Validate phoneme sequence
GET    /phonemes/languages                   # Supported languages
```

### Voice Analytics (8 endpoints)
```
POST   /analytics/voice-quality              # Analyze voice quality
POST   /analytics/speech-rate                # Calculate speech rate
POST   /analytics/pitch                      # Analyze pitch
POST   /analytics/volume                     # Analyze volume
POST   /analytics/emotions                   # Detect emotions
POST   /analytics/sentiment                  # Sentiment analysis
POST   /analytics/accent                     # Detect accent
GET    /analytics/reports                    # Generate analytics report
```

### Documentation (3 endpoints)
```
GET    /docs                                 # Swagger UI
GET    /redoc                                # ReDoc documentation
GET    /openapi.json                         # OpenAPI schema
```

### Additional Utilities (5 endpoints)
```
POST   /voice/clone                          # Voice cloning (experimental)
GET    /voice/samples                        # Sample audio files
POST   /voice/compare                        # Compare voices
GET    /voice/history                        # Usage history
POST   /voice/batch                          # Batch processing
```

---

## 5. SECURITY SERVICE (Port 8010)

**Status:** ✅ Complete Schemas | **Tier:** 2 | **Endpoints:** 42 | **Schema Coverage:** 100%

### Authentication (10 endpoints)
```
POST   /api/v1/auth/register                 # User registration
POST   /api/v1/auth/login                    # User login
POST   /api/v1/auth/logout                   # User logout
POST   /api/v1/auth/refresh                  # Refresh access token
POST   /api/v1/auth/verify-email             # Verify email
POST   /api/v1/auth/forgot-password          # Request password reset
POST   /api/v1/auth/reset-password           # Reset password
POST   /api/v1/auth/change-password          # Change password
GET    /api/v1/auth/me                       # Get current user
POST   /api/v1/auth/revoke                   # Revoke token
```

### Authorization (8 endpoints)
```
GET    /api/v1/auth/roles                    # List roles
POST   /api/v1/auth/roles                    # Create role
GET    /api/v1/auth/roles/{role_id}          # Get role
PUT    /api/v1/auth/roles/{role_id}          # Update role
DELETE /api/v1/auth/roles/{role_id}          # Delete role
POST   /api/v1/auth/roles/{role_id}/permissions # Assign permissions
GET    /api/v1/auth/permissions              # List permissions
POST   /api/v1/auth/check-permission         # Check user permission
```

### User Management (10 endpoints)
```
GET    /api/v1/users                         # List users
POST   /api/v1/users                         # Create user
GET    /api/v1/users/{user_id}               # Get user
PUT    /api/v1/users/{user_id}               # Update user
DELETE /api/v1/users/{user_id}               # Delete user
PATCH  /api/v1/users/{user_id}/status        # Update user status
POST   /api/v1/users/{user_id}/roles         # Assign roles
DELETE /api/v1/users/{user_id}/roles/{role_id} # Remove role
GET    /api/v1/users/{user_id}/permissions   # Get user permissions
POST   /api/v1/users/bulk                    # Bulk user operations
```

### Session Management (6 endpoints)
```
GET    /api/v1/sessions                      # List active sessions
GET    /api/v1/sessions/{session_id}         # Get session
DELETE /api/v1/sessions/{session_id}         # Terminate session
DELETE /api/v1/sessions/user/{user_id}       # Terminate all user sessions
GET    /api/v1/sessions/current              # Get current session
POST   /api/v1/sessions/validate             # Validate session
```

### API Keys (4 endpoints)
```
POST   /api/v1/api-keys                      # Create API key
GET    /api/v1/api-keys                      # List API keys
DELETE /api/v1/api-keys/{key_id}             # Revoke API key
POST   /api/v1/api-keys/{key_id}/rotate      # Rotate API key
```

### Health & Utilities (4 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/security/audit-log            # Security audit log
GET    /api/v1/security/config               # Security configuration
```

---

## 6. USER SERVICE (Port 8001/8007)

**Status:** 🟡 Partial Coverage | **Tier:** 3 | **Endpoints:** 35 | **Schema Coverage:** 26%

### Core User Operations (8 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/users                         # List users
POST   /api/v1/users                         # Create user
GET    /api/v1/users/{user_id}               # Get user
PUT    /api/v1/users/{user_id}               # Update user
DELETE /api/v1/users/{user_id}               # Delete user
PATCH  /api/v1/users/{user_id}               # Partial update
```

### Profile Management (9 endpoints)
```
GET    /api/v1/users/{user_id}/profile       # Get profile
PUT    /api/v1/users/{user_id}/profile       # Update profile
PATCH  /api/v1/users/{user_id}/profile       # Partial profile update
POST   /api/v1/users/{user_id}/profile/photo # Upload profile photo
DELETE /api/v1/users/{user_id}/profile/photo # Delete profile photo
GET    /api/v1/users/{user_id}/preferences   # Get preferences
PUT    /api/v1/users/{user_id}/preferences   # Update preferences
GET    /api/v1/users/{user_id}/settings      # Get settings
PUT    /api/v1/users/{user_id}/settings      # Update settings
```

### Activity Tracking (6 endpoints)
```
GET    /api/v1/users/{user_id}/activity      # Get activity log
POST   /api/v1/users/{user_id}/activity      # Log activity
GET    /api/v1/users/{user_id}/sessions      # List sessions
GET    /api/v1/users/{user_id}/login-history # Login history
GET    /api/v1/users/{user_id}/actions       # Action history
GET    /api/v1/users/{user_id}/timeline      # User timeline
```

### Search & Filtering (6 endpoints)
```
POST   /api/v1/users/search                  # Search users
POST   /api/v1/users/filter                  # Filter users
GET    /api/v1/users/active                  # List active users
GET    /api/v1/users/recent                  # Recently joined users
POST   /api/v1/users/bulk-lookup             # Bulk user lookup
GET    /api/v1/users/statistics              # User statistics
```

### Integration (6 endpoints)
```
POST   /api/v1/users/{user_id}/notifications # Send notification
GET    /api/v1/users/{user_id}/notifications # Get notifications
POST   /api/v1/users/{user_id}/invite        # Invite user
GET    /api/v1/users/{user_id}/integrations  # List integrations
POST   /api/v1/users/{user_id}/export        # Export user data
POST   /api/v1/users/import                  # Import users
```

---

## 7. CONVERSATION SERVICE (Port 8003)

**Status:** 🟡 Good Progress | **Tier:** 2 | **Endpoints:** 19 | **Schema Coverage:** 58%

### Conversation Management (5 endpoints)
```
POST   /conversation/start                   # Start conversation
POST   /conversation/message                 # Send message
GET    /conversation/status/{session_id}     # Get conversation status
POST   /conversation/end/{session_id}        # End conversation
POST   /conversation/generate-questions      # Generate interview questions
```

### Adaptive Interaction (6 endpoints)
```
POST   /api/v1/conversation/generate-adaptive-question # Generate adaptive question
POST   /api/v1/conversation/generate-followup # Generate follow-up question
POST   /api/v1/conversation/adapt-interview  # Adapt interview strategy
POST   /api/v1/conversation/analyze-response # Analyze candidate response
POST   /api/v1/conversation/suggest-topics   # Suggest discussion topics
GET    /api/v1/conversation/context          # Get conversation context
```

### Persona Management (4 endpoints)
```
POST   /api/v1/persona/switch                # Switch interviewer persona
GET    /api/v1/persona/current               # Get current persona
GET    /api/v1/persona/available             # List available personas
POST   /api/v1/persona/customize             # Customize persona
```

### Health & Utilities (4 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/conversation/history          # Get conversation history
POST   /api/v1/conversation/export           # Export conversation
```

---

## 8. SCOUT SERVICE (Port 8010)

**Status:** 🟡 Good Progress | **Tier:** 2 | **Endpoints:** 22 | **Schema Coverage:** 68%

### Talent Search (6 endpoints)
```
POST   /search                               # Search for talent
POST   /search/advanced                      # Advanced search
POST   /search/multi-agent                   # Multi-agent orchestrated search
POST   /agents/search-multi                  # Multi-agent search
POST   /agents/capability/{capability}       # Search by capability
GET    /search/results/{search_id}           # Get search results
```

### API v1 Router (Compatibility) (3 endpoints)
```
GET    /api/v1/search                        # Query-based search (compatibility)
POST   /api/v1/search/advanced               # Advanced search (compatibility)
POST   /api/v1/lists                         # Create sourced list (compatibility)
```

### Agent Management (8 endpoints)
```
POST   /handoff                              # Handoff to agents
POST   /agents/call                          # Call specific agent
GET    /agents/registry                      # List available agents
GET    /agents/health                        # Agent health status
GET    /agents/{agent_name}                  # Get agent details
POST   /agents/execute                       # Execute agent task
GET    /agents/capabilities                  # List agent capabilities
POST   /agents/orchestrate                   # Orchestrate multiple agents
```

### Integration & Discovery (5 endpoints)
```
POST   /discover/talent                      # Discover talent
POST   /match/candidates                     # Match candidates to roles
POST   /recommend/skills                     # Recommend skill development
GET    /insights/market                      # Market insights
GET    /trends/skills                        # Skill trends
```

### Health & Utilities (3 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /statistics                           # Service statistics
```

---

## 9. ANALYTICS SERVICE (Port 8017)

**Status:** 🟡 Good Progress | **Tier:** 2 | **Endpoints:** 18 | **Schema Coverage:** 78%

### Analysis Endpoints (8 endpoints)
```
POST   /api/v1/analyze/sentiment             # Sentiment analysis
POST   /api/v1/analyze/quality               # Response quality assessment
POST   /api/v1/analyze/bias                  # Bias detection
POST   /api/v1/analyze/expertise             # Expertise evaluation
POST   /api/v1/analyze/performance           # Performance metrics
POST   /api/v1/analyze/communication         # Communication analysis
POST   /api/v1/analyze/technical             # Technical skill assessment
POST   /api/v1/analyze/behavioral            # Behavioral analysis
```

### Reporting (6 endpoints)
```
POST   /api/v1/analyze/report                # Generate comprehensive report
GET    /api/v1/reports/{report_id}           # Get report
GET    /api/v1/reports/list                  # List reports
POST   /api/v1/reports/export                # Export report
POST   /api/v1/reports/compare               # Compare reports
GET    /api/v1/reports/templates             # List report templates
```

### Analytics (Implemented v1 stubs) (5 endpoints)
```
GET    /api/v1/analytics/interviews          # Interview analytics overview
GET    /api/v1/analytics/interviews/{id}     # Interview performance summary
GET    /api/v1/analytics/metrics             # Aggregate metrics
GET    /api/v1/analytics/metrics/timeseries  # Metrics time series
GET    /api/v1/analytics/reports/{report_id} # Get report (analytics namespace)
GET    /api/v1/analytics/reports/{report_id}/export # Export report (analytics namespace)
```

### Health & Utilities (4 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/analytics/models              # List analytics models
POST   /api/v1/analytics/calibrate           # Calibrate models
```

---

## 10. NOTIFICATION SERVICE (Port 8011)

**Status:** ✅ Production-Ready | **Tier:** 1 | **Endpoints:** 14 | **Schema Coverage:** 100%

### Core Notifications (6 endpoints)
```
POST   /api/v1/notify/email                  # Send email notification
POST   /api/v1/notify/sms                    # Send SMS notification (E.164 format)
POST   /api/v1/notify/push                   # Send push notification
POST   /api/v1/notify/batch                  # Send batch notifications
GET    /api/v1/notify/templates              # List notification templates
POST   /api/v1/notify/schedule               # Schedule notification
```

### Provider Management (4 endpoints)
```
GET    /api/v1/provider                      # Get active provider info
POST   /api/v1/provider/switch               # Switch provider
GET    /api/v1/provider/status               # Get provider status
POST   /api/v1/provider/test                 # Test provider connection
```

### Health & Utilities (4 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check with provider status
GET    /api/v1/notify/history                # Notification history
GET    /api/v1/notify/statistics             # Notification statistics
```

---

## 11. EXPLAINABILITY SERVICE (Port 8014)

**Status:** 🟡 Partial Coverage | **Tier:** 2 | **Endpoints:** 18 | **Schema Coverage:** 50%

### AI Explainability (6 endpoints)
```
POST   /api/v1/explain/interview             # Explain interview decision
POST   /api/v1/explain/scoring               # Explain scoring decision
POST   /api/v1/explain/recommendation        # Explain recommendation
POST   /api/v1/explain/model                 # Explain model behavior
POST   /api/v1/explain/prediction            # Explain prediction
GET    /api/v1/explain/{explanation_id}      # Get explanation
```

### Bias Detection (4 endpoints)
```
POST   /api/v1/bias/check                    # Check for bias
POST   /api/v1/bias/analyze                  # Analyze bias patterns
GET    /api/v1/bias/report/{report_id}       # Get bias report
POST   /api/v1/bias/mitigate                 # Suggest bias mitigation
```

### Compliance (4 endpoints)
```
GET    /api/v1/compliance/requirements       # Get compliance requirements
POST   /api/v1/compliance/audit              # Generate compliance audit
GET    /api/v1/compliance/report/{report_id} # Get compliance report
POST   /api/v1/compliance/validate           # Validate compliance
```

### Health & Utilities (4 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/explain/models                # List explainability models
POST   /api/v1/explain/configure             # Configure explainability
```

---

## 12. AI-AUDITING SERVICE (Port 8012)

**Status:** 🟢 Expanded (Dec 16) | **Tier:** 3 | **Endpoints:** 9 | **Schema Coverage:** 0%

### Audit Operations (9 endpoints)
```
GET    /                                     # Service root
GET    /health                               # Health check
POST   /api/v1/audit/run                     # Run audit job
GET    /api/v1/audit/status/{job_id}         # Check audit status
GET    /api/v1/audit/report/{job_id}         # Get audit report
GET    /api/v1/audit/rules                   # List audit rules
GET    /api/v1/audit/config                  # Get audit configuration
PUT    /api/v1/audit/config                  # Update audit configuration
GET    /api/v1/audit/history                 # Get audit history
```

---

## 13. GRANITE INTERVIEW SERVICE (Port TBD)

**Status:** 🟡 Partial Coverage | **Tier:** 2 | **Endpoints:** 24 | **Schema Coverage:** 41%

### Interview Orchestration (8 endpoints)
```
POST   /api/v1/interview/start               # Start Granite-powered interview
POST   /api/v1/interview/continue            # Continue interview
POST   /api/v1/interview/pause               # Pause interview
POST   /api/v1/interview/resume              # Resume interview
POST   /api/v1/interview/end                 # End interview
GET    /api/v1/interview/{interview_id}      # Get interview status
PUT    /api/v1/interview/{interview_id}      # Update interview
DELETE /api/v1/interview/{interview_id}      # Delete interview
```

### Granite AI Integration (8 endpoints)
```
POST   /api/v1/granite/query                 # Query Granite model
POST   /api/v1/granite/generate              # Generate content
POST   /api/v1/granite/analyze               # Analyze response
POST   /api/v1/granite/suggest               # Get suggestions
GET    /api/v1/granite/models                # List available models
POST   /api/v1/granite/switch-model          # Switch Granite model
GET    /api/v1/granite/model-info            # Get model information
POST   /api/v1/granite/fine-tune             # Fine-tune model
```

### Question Management (4 endpoints)
```
POST   /api/v1/questions/generate            # Generate questions
GET    /api/v1/questions/bank                # Question bank
POST   /api/v1/questions/validate            # Validate question
POST   /api/v1/questions/adapt               # Adapt question difficulty
```

### Health & Utilities (4 endpoints)
```
GET    /                                     # Root endpoint
GET    /health                               # Health check
GET    /api/v1/interview/statistics          # Interview statistics
POST   /api/v1/interview/export              # Export interview data
```

---

## 14. DESKTOP INTEGRATION SERVICE (Port TBD)

**Status:** 🟡 Partial Coverage | **Tier:** 2 | **Endpoints:** 26 | **Schema Coverage:** Unknown

### Gateway Operations (5 endpoints)
```
GET    /                                     # Root service info
GET    /health                               # Gateway + all services health
GET    /api/v1/system/status                 # System status (13 services)
GET    /api/v1/services                      # Complete service registry
GET    /api/v1/dashboard                     # Aggregated dashboard data
```

### Model Management (3 endpoints)
```
GET    /api/v1/models                        # Available AI models
POST   /api/v1/models/select                 # Select model for interviews
POST   /api/v1/models/configure              # Configure model settings
```

### Service Proxy (8 endpoints)
```
POST   /api/v1/voice/synthesize              # TTS proxy to Voice Service
POST   /api/v1/analytics/sentiment           # Sentiment proxy to Analytics
POST   /api/v1/agents/execute                # Agent orchestration
POST   /api/v1/interviews/start              # Start interview proxy
POST   /api/v1/interviews/respond            # Submit interview response
POST   /api/v1/interviews/summary            # Get interview summary
POST   /api/v1/candidates/search             # Candidate search proxy
POST   /api/v1/security/authenticate         # Authentication proxy
```

### Desktop Integration (6 endpoints)
```
POST   /api/v1/desktop/connect               # Connect desktop client
POST   /api/v1/desktop/disconnect            # Disconnect desktop client
GET    /api/v1/desktop/status                # Get desktop client status
POST   /api/v1/desktop/sync                  # Sync desktop data
GET    /api/v1/desktop/settings              # Get desktop settings
PUT    /api/v1/desktop/settings              # Update desktop settings
```

### Health & Utilities (4 endpoints)
```
GET    /api/v1/system/health                 # Comprehensive health check
GET    /api/v1/system/metrics                # System metrics
GET    /api/v1/system/logs                   # System logs
POST   /api/v1/system/restart-service        # Restart specific service
```

---

## 15. PROJECT SERVICE (Port TBD)

**Status:** 🟡 Partial Coverage | **Tier:** 2 | **Endpoints:** 6 | **Schema Coverage:** Unknown

### Project Management (6 endpoints)
```
GET    /api/v1/projects                      # List projects
POST   /api/v1/projects                      # Create project
GET    /api/v1/projects/{project_id}         # Get project
PUT    /api/v1/projects/{project_id}         # Update project
DELETE /api/v1/projects/{project_id}         # Delete project
GET    /api/v1/projects/{project_id}/members # List project members
```

---

## 16. AUDIO SERVICE (Port TBD)

**Status:** ⚠️ No Coverage | **Endpoints:** 0 | **Schema Coverage:** N/A

**Note:** Service may not be implemented or functionality merged into Voice Service

---

## 17. SHARED MODULE (N/A)

**Status:** 🟡 Partial Coverage | **Endpoints:** 8 | **Schema Coverage:** 0%

### Shared Utilities (8 endpoints)
```
# Middleware endpoints
# Authentication helpers
# Database utilities
# Configuration management
# Logging services
# Error handling
# Validation utilities
# Common schemas
```

---

## 📊 Summary Statistics

### By Tier
- **Tier 1 (Production):** 4 services, 182 endpoints, 96.4% schema coverage
- **Tier 2 (Good):** 7 services, 133 endpoints, 59.8% schema coverage
- **Tier 3 (Critical):** 4 services, 112 endpoints, 14.9% schema coverage

### By Status
- ✅ **Production-Ready:** 4 services (Candidate, Interview, Avatar, Notification)
- 🟢 **Recently Updated:** 2 services (AI-Auditing, Avatar)
- 🟡 **Partial Coverage:** 10 services
- ⚠️ **No Implementation:** 1 service (Audio)

### Schema Coverage
- **100% Coverage:** 2 services (Security, Notification)
- **80-99% Coverage:** 3 services
- **50-79% Coverage:** 5 services
- **<50% Coverage:** 5 services
- **0% Coverage:** 2 services (AI-Auditing, Shared)

### Total Counts
- **Total Services:** 18
- **Total Endpoints:** 427+ (consolidated count)
- **Documented Endpoints:** 271 (from audit)
- **Schema Coverage:** 77.1% overall (209/271)
- **Port Range:** 8000-8015

---

## 🎯 Next Actions

1. **Runtime Verification:** Start all services and run `extract-all-endpoints.sh`
2. **Schema Remediation:** Address 62 missing schemas (15.5 hours estimated)
3. **Port Standardization:** Resolve 9 port conflicts
4. **Documentation Update:** Reconcile 128-endpoint discrepancy
5. **Type Safety:** Apply enum fixes to Security and User services (7-10 hours)

---

**Runtime Verification (Dec 17, 2025):**
- Services running: Avatar (8001), Analytics (8017), Scout (8010)
- Extracted endpoints: Avatar 46, Analytics 16, Scout 15
- Output directory: `endpoint-extraction-YYYYMMDD-HHMMSS` with `SUMMARY.md` and per-service files.

---

**Document Status:** Ready for Runtime Verification  
**Last Updated:** December 17, 2025  
**Verification Required:** Yes - Run extraction script to confirm actual endpoints
