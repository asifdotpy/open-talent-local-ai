# OpenTalent Sourcing Workflow - Detailed Step-by-Step Analysis

**Document Purpose:** Complete technical breakdown of how agents work together to source, qualify, engage, and schedule interviews with candidates.

**Architecture:** Event-driven, asynchronous microservices with Redis message bus coordination.

---

## 🎯 High-Level Sourcing Pipeline Flow

```
User Request
    ↓
Scout Coordinator Creates Pipeline
    ↓
Scanning Phase (Proactive Scanning + Boolean Mastery)
    ↓
Candidate Found Events
    ↓
Quality Assessment Phase (Quality-Focused Agent)
    ↓
Engagement Phase (Personalized Engagement)
    ↓
Interview Phase (Interviewer Agent)
    ↓
Results & Integration (Tool Leverage Agent)
```

---

## 📋 Step-by-Step Workflow Breakdown

### **PHASE 1: PIPELINE INITIALIZATION**

#### **Step 1.1: User Initiates Sourcing via REST API**

**Endpoint:** `POST /pipelines/start` on Scout Coordinator (Port 8090)

**Request Body:**
```json
{
  "project_id": "project_123",
  "job_description": "Senior Python Backend Developer with 5+ years experience in FastAPI and microservices",
  "job_title": "Senior Backend Engineer",
  "target_platforms": ["linkedin", "github"],
  "num_candidates_target": 50,
  "priority": "medium"
}
```

**Code Location:** [scout-coordinator-agent/main.py#L350](../agents/scout-coordinator-agent/main.py#L350)

---

#### **Step 1.2: Scout Coordinator Creates Pipeline State**

**Process:**
```python
# In start_pipeline() endpoint:
pipeline_id = f"pipeline_{project_id}_{timestamp}"
pipeline = SourcingPipeline(
    id=pipeline_id,
    project_id=project_id,
    job_description=job_description,
    state=PipelineState.INITIATED,  # Initial state
    candidates_found=0,
    candidates_contacted=0,
    candidates_responded=0,
    interviews_scheduled=0
)
active_pipelines[pipeline_id] = pipeline
```

**What Happens:**
- Pipeline object created and stored in memory (`active_pipelines` dict)
- Status: `INITIATED` (ready to start scanning)
- All metrics initialized to 0

**Response to User:**
```json
{
  "pipeline_id": "pipeline_project_123_1733740234",
  "project_id": "project_123",
  "state": "INITIATED",
  "active_agents": [],
  "candidates_found": 0,
  "candidates_contacted": 0,
  "candidates_responded": 0,
  "interviews_scheduled": 0,
  "progress_percentage": 0.0,
  "started_at": "2025-12-09T10:30:34Z",
  "updated_at": "2025-12-09T10:30:34Z"
}
```

---

### **PHASE 2: SCANNING & QUERY GENERATION**

#### **Step 2.1: Scout Coordinator Publishes Pipeline Started Event**

**What Happens:**
```python
await message_bus.publish_event(
    topic=Topics.PIPELINE_EVENTS,
    source_agent="scout-coordinator",
    message_type=MessageType.PIPELINE_UPDATE,
    payload={
        "pipeline_id": pipeline_id,
        "project_id": project_id,
        "action": "started",
        "job_description": request.job_description,
        "platforms": request.target_platforms,
        "timestamp": "2025-12-09T10:30:35Z"
    },
    priority=MessagePriority.HIGH
)
```

**Message Bus Location:** Redis topic `PIPELINE_EVENTS`

---

#### **Step 2.2: Scout Coordinator Triggers Scanning Phase (Background Task)**

**Code Location:** [scout-coordinator-agent/main.py#L413-L448](../agents/scout-coordinator-agent/main.py#L413-L448)

**Process in `initiate_scanning()` function:**

**Step 2.2a: Transition to SCANNING state**
```python
await transition_pipeline(pipeline_id, PipelineState.SCANNING)
# Publishes: PIPELINE_UPDATE event with state change
```

**Step 2.2b: Publish Scanning Request to Proactive Scanning Agent**
```python
await message_bus.publish_event(
    topic="agents:scanning",
    source_agent="scout-coordinator",
    message_type=MessageType.CANDIDATE_FOUND,
    payload={
        "pipeline_id": pipeline_id,
        "action": "start_scanning",
        "job_description": "Senior Python Backend Developer...",
        "platforms": ["linkedin", "github"],
        "target_count": 50,
        "timestamp": "2025-12-09T10:30:35Z"
    }
)
```

**Step 2.2c: Publish Boolean Query Generation Request**
```python
await message_bus.publish_event(
    topic="agents:boolean",
    source_agent="scout-coordinator",
    message_type=MessageType.PIPELINE_UPDATE,
    payload={
        "pipeline_id": pipeline_id,
        "action": "generate_queries",
        "job_description": "Senior Python Backend Developer...",
        "platforms": ["linkedin", "github"],
        "timestamp": "2025-12-09T10:30:35Z"
    }
)
```

**Result:** Both agents now have work to do (async, parallel processing)

---

#### **Step 2.3: Boolean Mastery Agent Receives Query Request**

**Code Location:** [boolean-mastery-agent/main.py#L106-L132](../boolean-mastery-agent/main.py#L106-L132)

**Process:**

**Step 2.3a: Message Bus Listener Receives Event**
```python
async def handle_query_request(message):
    """Message arrives from Redis topic 'agents:boolean'"""
    job_description = message.payload.get("job_description")
    platforms = message.payload.get("platforms", ["linkedin"])
    pipeline_id = message.payload.get("pipeline_id")
```

**Step 2.3b: Generate Boolean Query for Each Platform**

For **LinkedIn:**
```python
# Extract keywords from job description
keywords = extract_keywords(job_description)
# Returns: 
# {
#   "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis"],
#   "titles": ["Software Engineer", "Backend Developer", "Python Developer"],
#   "languages": ["python", "javascript", "typescript"],
#   "frameworks": ["Django", "FastAPI", "Flask"]
# }

# Build LinkedIn boolean query
skills = '"Python" OR "FastAPI" OR "PostgreSQL" OR "Redis" OR "Django"'
titles = '"Backend Engineer" OR "Software Engineer" OR "Python Developer"'
query = f"({titles}) AND ({skills})"

# Result: 
# ("Backend Engineer" OR "Software Engineer" OR "Python Developer") 
# AND ("Python" OR "FastAPI" OR "PostgreSQL" OR "Redis" OR "Django")
```

For **GitHub:**
```python
# GitHub search syntax (different from LinkedIn)
languages = "language:python language:typescript"
skills = "FastAPI microservices architecture"
query = f"{skills} {languages}"

# Result: 
# FastAPI microservices architecture language:python language:typescript
```

**Step 2.3c: Publish Query Generated Event**
```python
await message_bus.publish_event(
    topic=Topics.PIPELINE_EVENTS,
    source_agent="boolean-mastery",
    message_type=MessageType.PIPELINE_UPDATE,
    payload={
        "pipeline_id": pipeline_id,
        "platform": "linkedin",
        "query": '("Backend Engineer" OR "Software Engineer") AND ("Python" OR "FastAPI")',
        "keywords": ["Python", "FastAPI", "Backend Engineer"],
        "timestamp": "2025-12-09T10:30:36Z"
    },
    priority=MessagePriority.MEDIUM
)
```

**Output:** Boolean query is now available for scanning agents to use (but note: in current impl, they generate mock data)

---

#### **Step 2.4: Proactive Scanning Agent Receives Scanning Request**

**Code Location:** [proactive-scanning-agent/main.py#L95-L180](../proactive-scanning-agent/main.py#L95-L180)

**Process:**

**Step 2.4a: Message Bus Listener Receives Event**
```python
async def handle_scanning_request(message):
    """Message from Redis topic 'agents:scanning'"""
    pipeline_id = message.payload.get("pipeline_id")
    job_description = message.payload.get("job_description")
    platforms = message.payload.get("platforms", ["linkedin", "github"])
    target_count = message.payload.get("target_count", 50)
    
    # Trigger scanning in background
    asyncio.create_task(
        scan_platforms(pipeline_id, job_description, platforms, target_count)
    )
```

**Step 2.4b: Scan Each Platform in Parallel**

For **LinkedIn:**
```python
async def scan_linkedin(pipeline_id, job_description, target):
    # In production: Use LinkedIn API with boolean query
    # In current: Mock data generation
    
    for i in range(min(target, 10)):
        candidate = CandidateProfile(
            id=f"linkedin_{pipeline_id}_{i}",
            name=f"LinkedIn Candidate {i}",
            email=f"candidate{i}@linkedin.example.com",
            location="San Francisco, CA",
            current_role="Software Engineer",
            experience_years=5 + i,
            skills=["Python", "Django", "PostgreSQL", "AWS"],
            source=CandidateSource.LINKEDIN,
            status=CandidateStatus.NEW,
            social_profiles=[
                SocialProfile(
                    platform="linkedin",
                    url=f"https://linkedin.com/in/candidate{i}",
                    followers=1000 + i * 100
                )
            ]
        )
```

For **GitHub:**
```python
async def scan_github(pipeline_id, job_description, target):
    # In production: Use GitHub API search
    # In current: Mock data generation
    
    for i in range(min(target, 10)):
        candidate = CandidateProfile(
            id=f"github_{pipeline_id}_{i}",
            name=f"GitHub Developer {i}",
            email=f"dev{i}@github.example.com",
            current_role="Full Stack Engineer",
            skills=["Python", "FastAPI", "React", "Kubernetes"],
            source=CandidateSource.GITHUB,
            status=CandidateStatus.NEW,
            social_profiles=[
                SocialProfile(
                    platform="github",
                    url=f"https://github.com/user{i}",
                    followers=500 + i * 50
                )
            ]
        )
```

**Step 2.4c: Publish Candidate Found Events**

For each candidate discovered:
```python
await message_bus.publish_event(
    topic=Topics.CANDIDATE_EVENTS,
    source_agent="proactive-scanning",
    message_type=MessageType.CANDIDATE_FOUND,
    payload={
        "pipeline_id": "pipeline_project_123_1733740234",
        "candidate": {
            "id": "linkedin_pipeline_123_0",
            "name": "LinkedIn Candidate 0",
            "email": "candidate0@linkedin.example.com",
            "location": "San Francisco, CA",
            "current_role": "Software Engineer",
            "experience_years": 5,
            "skills": ["Python", "Django", "PostgreSQL", "AWS"],
            "source": "LINKEDIN",
            "status": "NEW"
        },
        "platform": "linkedin",
        "timestamp": "2025-12-09T10:30:37Z"
    },
    priority=MessagePriority.MEDIUM
)
```

**Timing:** One event per 0.5 seconds (rate limiting), 10 per platform = ~20 total candidates

---

### **PHASE 3: CANDIDATE QUALITY ASSESSMENT**

#### **Step 3.1: Quality-Focused Agent Receives Candidate Found Events**

**Code Location:** [quality-focused-agent/main.py#L101-L130](../quality-focused-agent/main.py#L101-L130)

**Process:**

**Step 3.1a: Message Listener Subscribes to Candidate Events**
```python
# During agent startup (lifespan):
await message_bus.subscribe(
    ["agents:quality", Topics.CANDIDATE_EVENTS],
    handle_scoring_request
)
```

**Step 3.1b: Auto-Score New Candidates**
```python
async def handle_scoring_request(message):
    if message.message_type == MessageType.CANDIDATE_FOUND:
        candidate_data = message.payload.get("candidate")
        pipeline_id = message.payload.get("pipeline_id")
        
        # Trigger scoring in background
        asyncio.create_task(
            score_candidate(pipeline_id, candidate_data)
        )
```

**Step 3.1c: Score Individual Candidate Using Genkit AI**

```python
async def score_candidate(pipeline_id, candidate_data):
    candidate_id = candidate_data.get("id")
    
    # Call Genkit service (Google AI LLM) for scoring
    score_data = await service_clients.genkit.score_candidate_quality(
        candidate_profile={
            "name": "LinkedIn Candidate 0",
            "email": "candidate0@linkedin.example.com",
            "experience_years": 5,
            "skills": ["Python", "Django", "PostgreSQL", "AWS"],
            "current_role": "Software Engineer",
            "location": "San Francisco, CA"
        },
        job_description="Senior Python Backend Developer with 5+ years"
    )
    
    # Genkit returns scoring breakdown
    overall_score = score_data.get("quality_score", 0)  # 0-100
    skill_match = score_data.get("skill_match", 0)      # 0-100
    experience_match = score_data.get("experience_match", 0)  # 0-100
```

**Step 3.1d: Detect Bias in Candidate Data**

```python
async def detect_bias(candidate_data):
    bias_flags = []
    
    # Check for name-based bias
    name = candidate_data.get("name", "").lower()
    if any(marker in name for marker in ["jr", "sr", "iii"]):
        # Could indicate age discrimination concerns
        bias_flags.append("potential_age_marker")
    
    # Check for gender indicators
    pronouns = candidate_data.get("pronouns", "").lower()
    if pronouns:
        # Monitor gender-specific evaluation
        bias_flags.append("gender_identified")
    
    # Check for location-based bias
    location = candidate_data.get("location", "")
    if location and "sf" in location.lower():
        # All candidates from same location
        bias_flags.append("geographic_clustering")
    
    return bias_flags
```

**Step 3.1e: Determine Recommendation Based on Score**

```python
recommendation = "reject"
if overall_score >= 80:
    recommendation = "strong_hire"
elif overall_score >= 70:
    recommendation = "hire"
elif overall_score >= 60:
    recommendation = "maybe"

# Example for candidate with 78 score:
# recommendation = "hire"
```

**Step 3.1f: Publish Candidate Scored Event**

```python
await message_bus.publish_event(
    topic=Topics.CANDIDATE_EVENTS,
    source_agent="quality-focused",
    message_type=MessageType.CANDIDATE_SCORED,
    payload={
        "pipeline_id": "pipeline_project_123_1733740234",
        "candidate_id": "linkedin_pipeline_123_0",
        "quality_score": 78,
        "skill_match": 82,
        "experience_match": 75,
        "bias_flags": ["geographic_clustering"],
        "recommendation": "hire",
        "timestamp": "2025-12-09T10:30:38Z"
    },
    priority=MessagePriority.HIGH  # HIGH if score >= 80, else MEDIUM
)
```

**Result:** Each candidate now has a quality score and hiring recommendation

---

#### **Step 3.2: Scout Coordinator Reacts to High-Quality Candidates**

**Code Location:** [scout-coordinator-agent/main.py#L178-L186](../scout-coordinator-agent/main.py#L178-L186)

**Process:**

**Step 3.2a: Coordinator Receives Scored Event**
```python
async def handle_candidate_scored(message: AgentMessage):
    pipeline_id = message.payload.get("pipeline_id")
    quality_score = message.payload.get("quality_score", 0)
    
    # If high quality candidate, trigger engagement
    if quality_score >= 70 and pipeline_id in active_pipelines:
        await trigger_engagement(pipeline_id, message.payload.get("candidate_id"))
```

**Step 3.2b: For Candidates Scoring >= 70, Trigger Engagement**

```python
async def trigger_engagement(pipeline_id, candidate_id):
    """Trigger engagement for qualified candidate"""
    await message_bus.publish_event(
        topic=Topics.ENGAGEMENT_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.OUTREACH_SENT,
        payload={
            "pipeline_id": pipeline_id,
            "candidate_id": candidate_id,
            "action": "send_outreach",
            "timestamp": "2025-12-09T10:30:39Z"
        }
    )
```

**Result:** High-quality candidates automatically move to engagement phase

**Low-Quality Candidates:** Score < 70, no action (stored for later review if needed)

---

### **PHASE 4: PERSONALIZED ENGAGEMENT**

#### **Step 4.1: Personalized Engagement Agent Receives Outreach Trigger**

**Code Location:** [personalized-engagement-agent/main.py#L113-L170](../personalized-engagement-agent/main.py#L113-L170)

**Process:**

**Step 4.1a: Message Listener Subscribes to Engagement Events**
```python
# During agent startup:
await message_bus.subscribe(
    [Topics.ENGAGEMENT_EVENTS, "agents:engagement"],
    handle_engagement_request
)
```

**Step 4.1b: Engagement Request Received**
```python
async def handle_engagement_request(message):
    pipeline_id = message.payload.get("pipeline_id")
    candidate_id = message.payload.get("candidate_id")
    
    # Trigger engagement in background
    asyncio.create_task(
        send_outreach(pipeline_id, candidate_id)
    )
```

**Step 4.1c: Fetch Candidate Data (Mock Implementation)**

In production, would fetch from candidate database:
```python
candidate_data = {
    "name": "LinkedIn Candidate 0",
    "email": "candidate0@linkedin.example.com",
    "current_role": "Software Engineer",
    "skills": ["Python", "Django", "PostgreSQL", "AWS"]
}
```

**Step 4.1d: Generate Personalized Message Using Genkit AI**

```python
message_data = await service_clients.genkit.generate_engagement_message(
    candidate_name="LinkedIn Candidate 0",
    candidate_role="Software Engineer",
    job_title="Senior Backend Engineer",
    company_name="TalentAI"
)

# Genkit generates:
message_data = {
    "subject": "Exciting Opportunity - Senior Backend Engineer at TalentAI",
    "message": """
    Hi LinkedIn Candidate 0,

    We came across your profile and were impressed by your experience as a Software Engineer 
    with expertise in Python and Django. We're currently hiring for a Senior Backend Engineer 
    position at TalentAI, and we believe your skills would be a perfect fit.

    The role involves:
    - Building scalable microservices with FastAPI and PostgreSQL
    - Architecting distributed systems
    - Mentoring junior developers

    Would you be interested in a quick conversation about this opportunity?

    Best regards,
    TalentAI Recruiting
    """
}
```

**Step 4.1e: Send Email (Mock)**

```python
success = await send_email(
    to_email="candidate0@linkedin.example.com",
    subject="Exciting Opportunity - Senior Backend Engineer at TalentAI",
    body=message_data.get("message")
)

# In production: Use SMTP (Gmail, SendGrid, etc.)
# Current: Mock returns success = True
```

**Step 4.1f: Publish Outreach Sent Event**

```python
await message_bus.publish_event(
    topic=Topics.ENGAGEMENT_EVENTS,
    source_agent="personalized-engagement",
    message_type=MessageType.OUTREACH_SENT,
    payload={
        "pipeline_id": "pipeline_project_123_1733740234",
        "candidate_id": "linkedin_pipeline_123_0",
        "channel": "email",
        "message": message_data.get("message"),
        "timestamp": "2025-12-09T10:30:40Z"
    },
    priority=MessagePriority.HIGH
)
```

**Step 4.1g: Scout Coordinator Tracks Outreach**

```python
async def handle_outreach_sent(message: AgentMessage):
    pipeline_id = message.payload.get("pipeline_id")
    if pipeline_id in active_pipelines:
        active_pipelines[pipeline_id].candidates_contacted += 1
        active_pipelines[pipeline_id].updated_at = datetime.utcnow()
```

**Result:** Candidate now has "outreach in flight", waiting for response

---

#### **Step 4.2: Simulate Candidate Response (Real Flow Would Use Email/SMS)**

**In Production:**
- Candidate receives email
- Clicks link in email → replies positively
- Email service triggers webhook → POST to engagement API

**In Current Mock:**
- Candidate response simulated manually or via API
- Would trigger: `MessageType.OUTREACH_RESPONSE` event

```python
# Manual trigger to simulate response:
await message_bus.publish_event(
    topic=Topics.ENGAGEMENT_EVENTS,
    source_agent="email-handler",  # Would come from email webhook
    message_type=MessageType.OUTREACH_RESPONSE,
    payload={
        "pipeline_id": "pipeline_project_123_1733740234",
        "candidate_id": "linkedin_pipeline_123_0",
        "response": "positive",
        "response_message": "Yes, I'm interested in learning more!",
        "timestamp": "2025-12-09T10:30:50Z"
    },
    priority=MessagePriority.HIGH
)
```

---

### **PHASE 5: INTERVIEW SCHEDULING & EXECUTION**

#### **Step 5.1: Scout Coordinator Reacts to Positive Response**

**Code Location:** [scout-coordinator-agent/main.py#L188-L201](../scout-coordinator-agent/main.py#L188-201)

**Process:**

**Step 5.1a: Coordinator Receives Response Event**
```python
async def handle_outreach_response(message: AgentMessage):
    pipeline_id = message.payload.get("pipeline_id")
    if pipeline_id in active_pipelines:
        # Track response
        active_pipelines[pipeline_id].candidates_responded += 1
        active_pipelines[pipeline_id].updated_at = datetime.utcnow()
        
        # Trigger interview scheduling
        await trigger_interview(pipeline_id, message.payload.get("candidate_id"))
```

**Step 5.1b: Trigger Interview Scheduling**

```python
async def trigger_interview(pipeline_id, candidate_id):
    await message_bus.publish_event(
        topic=Topics.INTERVIEW_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.INTERVIEW_SCHEDULED,
        payload={
            "pipeline_id": pipeline_id,
            "candidate_id": candidate_id,
            "action": "schedule_interview",
            "timestamp": "2025-12-09T10:30:51Z"
        }
    )
```

---

#### **Step 5.2: Interviewer Agent Receives Interview Trigger**

**Code Location:** [interviewer-agent/main.py#L383-L425](../interviewer-agent/main.py#L383-L425)

**Process:**

**Step 5.2a: Interview Request Received**

REST API endpoint: `POST /interviews/start`

```json
{
  "candidate_id": "linkedin_pipeline_123_0",
  "pipeline_id": "pipeline_project_123_1733740234",
  "job_title": "Senior Backend Engineer",
  "company_name": "TalentAI"
}
```

**Step 5.2b: Create Interview Session**

```python
interview_session = InterviewSession(
    id=f"interview_{candidate_id}_{timestamp}",
    candidate_id=candidate_id,
    pipeline_id=pipeline_id,
    status=InterviewStatus.STARTED,
    questions_asked=0,
    questions_total=5,
    current_question=None,
    responses=[],
    start_time=datetime.utcnow(),
    avatar_enabled=True,  # Enable 3D avatar
    voice_enabled=True    # Enable voice synthesis
)
```

**Step 5.2c: Generate First Interview Question Using Genkit**

```python
question_data = await service_clients.genkit.generate_interview_question(
    candidate_profile={
        "name": "LinkedIn Candidate 0",
        "role": "Software Engineer",
        "skills": ["Python", "Django", "PostgreSQL"],
        "experience_years": 5
    },
    job_title="Senior Backend Engineer",
    question_number=1,
    total_questions=5
)

# Genkit generates contextual question:
question_data = {
    "question": "Tell me about your experience with designing scalable backend systems. Can you walk us through a complex system you've architected?",
    "difficulty": "medium",
    "category": "system_design",
    "expected_keywords": ["scalability", "microservices", "database", "caching", "load_balancing"]
}
```

**Step 5.2d: Call Avatar Service to Render 3D Avatar**

```python
avatar_response = await service_clients.avatar.generate_avatar(
    interview_id=interview_session.id,
    text=question_data["question"],
    persona="professional_recruiter"  # Friendly but professional
)

# Avatar service returns:
avatar_response = {
    "avatar_url": "http://avatar-service:8001/avatars/interview_123/avatar.glb",
    "animation_clip": "talking_question_1",
    "duration_seconds": 12.5,
    "ready": True
}
```

**Step 5.2e: Generate Voice (Piper TTS) for Question**

```python
voice_response = await service_clients.voice.synthesize(
    text=question_data["question"],
    voice="professional_english_female",
    quality="high"  # High-quality synthesis
)

# Voice service returns:
voice_response = {
    "audio_url": "http://voice-service:8002/audio/interview_123_q1.mp3",
    "audio_file": b"<mp3_binary_data>",
    "duration_seconds": 12.5,
    "ready": True
}
```

**Step 5.2f: Send Interview Question to Candidate**

Frontend receives:
```json
{
  "interview_id": "interview_linkedin_123_0_1733740251",
  "question": "Tell me about your experience with designing scalable backend systems...",
  "question_number": 1,
  "total_questions": 5,
  "audio_url": "http://voice-service:8002/audio/interview_123_q1.mp3",
  "avatar_url": "http://avatar-service:8001/avatars/interview_123/avatar.glb",
  "time_limit_seconds": 120,  # 2 minutes to answer
  "status": "waiting_for_response"
}
```

**Frontend/Desktop App Displays:**
1. 3D avatar (Three.js) with animated lip-sync
2. Audio plays (voice service)
3. Candidate has 2 minutes to record answer
4. Next button when done

---

#### **Step 5.3: Candidate Submits Answer**

**REST API endpoint:** `POST /interviews/{interview_id}/answer`

```json
{
  "interview_id": "interview_linkedin_123_0_1733740251",
  "question_number": 1,
  "answer_text": "Well, I've worked on several microservices architectures...",
  "answer_audio": "<base64_encoded_audio>"
}
```

**Step 5.3a: Store Answer in Interview Session**

```python
interview_session.responses.append({
    "question_number": 1,
    "question": "Tell me about your experience...",
    "answer": "Well, I've worked on several microservices...",
    "answer_audio": "<audio_data>",
    "timestamp": datetime.utcnow()
})
```

**Step 5.3b: Evaluate Response Using Genkit AI**

```python
evaluation = await service_clients.genkit.evaluate_interview_response(
    question="Tell me about your experience with designing scalable backend systems...",
    candidate_answer="Well, I've worked on several microservices architectures. We used Kubernetes for orchestration...",
    expected_keywords=["scalability", "microservices", "database", "caching"],
    job_role="Senior Backend Engineer"
)

# Genkit evaluation:
evaluation = {
    "answer_score": 82,  # 0-100
    "keyword_coverage": 85,  # Hit 3 of 4 keywords
    "relevance": 90,
    "articulation": 80,
    "strengths": ["Good understanding of microservices", "Practical experience"],
    "areas_for_improvement": ["Could mention caching strategies"],
    "follow_up_question": "You mentioned using Kubernetes - can you tell us about the auto-scaling strategy you implemented?"
}
```

**Step 5.3c: Generate Follow-Up Question (If Applicable)**

```python
if evaluation.get("answer_score") >= 70:
    # Strong answer - generate follow-up
    follow_up = await service_clients.genkit.generate_interview_question(
        candidate_profile=candidate_data,
        previous_question=question_data["question"],
        previous_answer=answer_text,
        follow_up_suggestion=evaluation.get("follow_up_question"),
        question_number=2
    )
    
    # Repeat steps 5.2d-5.2f (voice + avatar + send)
else:
    # Weak answer - redirect or skip to next topic
    follow_up = await service_clients.genkit.generate_interview_question(
        candidate_profile=candidate_data,
        job_title="Senior Backend Engineer",
        question_number=2,
        difficulty="easier"  # Adjust difficulty
    )
```

**Step 5.3d: Store Response Evaluation**

```python
interview_session.response_evaluations.append({
    "question_number": 1,
    "answer_score": 82,
    "keyword_coverage": 85,
    "articulation": 80,
    "strengths": ["Good understanding of microservices"],
    "areas_for_improvement": ["Could mention caching strategies"],
    "timestamp": datetime.utcnow()
})
```

---

#### **Step 5.4: Repeat for Remaining Questions**

**Process repeats for questions 2-5:**
1. Generate question (or follow-up)
2. Call avatar service (lip-sync animation)
3. Call voice service (TTS)
4. Send to candidate
5. Receive answer
6. Evaluate with Genkit
7. Store evaluation
8. Generate next question

---

#### **Step 5.5: Interview Complete - Generate Assessment Report**

**REST API endpoint:** `GET /interviews/{interview_id}` (after all 5 questions)

**Process:**

**Step 5.5a: Calculate Overall Interview Score**

```python
overall_score = sum(
    evaluation["answer_score"] 
    for evaluation in interview_session.response_evaluations
) / len(interview_session.response_evaluations)

# Example:
# Q1: 82, Q2: 78, Q3: 85, Q4: 80, Q5: 88
# Overall: (82+78+85+80+88) / 5 = 82.6
```

**Step 5.5b: Generate Interview Report Using Genkit**

```python
report = await service_clients.genkit.generate_interview_report(
    interview_session={
        "candidate": candidate_data,
        "job_title": "Senior Backend Engineer",
        "questions_asked": [q1, q2, q3, q4, q5],
        "answers": [a1, a2, a3, a4, a5],
        "evaluations": [e1, e2, e3, e4, e5],
        "overall_score": 82.6
    }
)

# Genkit generates comprehensive report:
report = {
    "overall_assessment": "Strong candidate with excellent technical knowledge",
    "strengths": [
        "Deep understanding of distributed systems",
        "Practical experience with modern tech stack",
        "Clear communication of complex concepts"
    ],
    "weaknesses": [
        "Limited experience with specific caching patterns",
        "Could improve on system design trade-offs explanation"
    ],
    "recommendation": "STRONG_HIRE",
    "interview_score": 82.6,
    "next_steps": "Proceed to technical assessment round"
}
```

**Step 5.5c: Create Interview Result**

```python
interview_result = InterviewResult(
    interview_id=interview_session.id,
    candidate_id=candidate_id,
    pipeline_id=pipeline_id,
    overall_score=82.6,
    technical_score=85,
    communication_score=80,
    cultural_fit_score=78,
    recommendation="STRONG_HIRE",
    report_summary=report.get("overall_assessment"),
    strengths=report.get("strengths"),
    weaknesses=report.get("weaknesses"),
    next_steps=report.get("next_steps"),
    completed_at=datetime.utcnow()
)

active_interviews[interview_id] = interview_result
```

**Step 5.5d: Publish Interview Complete Event**

```python
await message_bus.publish_event(
    topic=Topics.INTERVIEW_EVENTS,
    source_agent="interviewer-agent",
    message_type=MessageType.INTERVIEW_COMPLETED,
    payload={
        "pipeline_id": pipeline_id,
        "interview_id": interview_id,
        "candidate_id": candidate_id,
        "overall_score": 82.6,
        "recommendation": "STRONG_HIRE",
        "report": report,
        "timestamp": "2025-12-09T10:31:05Z"
    },
    priority=MessagePriority.HIGH
)
```

---

### **PHASE 6: CANDIDATE INTEGRATION & FOLLOW-UP**

#### **Step 6.1: Scout Coordinator Tracks Interview Completion**

```python
if pipeline_id in active_pipelines:
    active_pipelines[pipeline_id].interviews_completed += 1
    active_pipelines[pipeline_id].interviews_scheduled += 1  # Already scheduled
    active_pipelines[pipeline_id].updated_at = datetime.utcnow()
```

#### **Step 6.2: Tool Leverage Agent Syncs Candidate to ATS/CRM**

**Code Location:** [tool-leverage-agent/main.py](../agents/tool-leverage-agent/main.py)

**When:** Triggered by interview completion or candidate acceptance

**Process:**

```python
async def sync_candidate_to_ats(candidate_id, interview_result):
    """Sync candidate and interview results to ATS"""
    
    # In production: Call ATS API
    ats_payload = {
        "candidate": {
            "name": "LinkedIn Candidate 0",
            "email": "candidate0@linkedin.example.com",
            "phone": "+1-555-0100",
            "location": "San Francisco, CA",
            "current_role": "Software Engineer",
            "experience_years": 5,
            "skills": ["Python", "Django", "PostgreSQL"],
            "source": "linkedin",
            "stage": "interview_completed"
        },
        "interview_results": {
            "score": 82.6,
            "recommendation": "STRONG_HIRE",
            "report_summary": "...",
            "completed_at": "2025-12-09T10:31:05Z"
        },
        "next_action": "schedule_technical_assessment"
    }
    
    # Call ATS (Workable, Greenhouse, Lever, Taleo, etc.)
    response = await ats_client.post(
        "candidates/import",
        json=ats_payload,
        headers={"Authorization": f"Bearer {ATS_API_KEY}"}
    )
```

---

## 📊 Complete Sourcing Pipeline Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                  REST API Request                            │
│  POST /pipelines/start                                       │
│  {project_id, job_description, platforms, target_count}      │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│          Scout Coordinator (Port 8090)                       │
│  - Creates pipeline state                                    │
│  - Stores in active_pipelines{}                              │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────────┐ │
│   Publishes  │ │  Publishes  │ │
│ SCANNING REQ │ │ QUERY REQ   │ │
└───────┬──────┘ └──┬──────────┘ │
        │           │            │
┌───────▼─────────────┐  ┌───────▼────────────────────┐
│ Proactive Scanning  │  │  Boolean Mastery Agent     │
│    (8091)           │  │      (8092)                │
│                     │  │                            │
│ scan_linkedin()     │  │ Extract keywords:          │
│ scan_github()       │  │ - Build boolean query      │
│ scan_stackoverflow()│  │ - Publish query event      │
│                     │  │                            │
│ Publishes:          │  │ Example query:             │
│ CANDIDATE_FOUND×20  │  │ ("Engineer" OR "Dev")     │
│ per platform        │  │ AND ("Python" OR "Go")    │
└─────────┬───────────┘  └────────────────────────────┘
          │
          │ CANDIDATE_FOUND events
          │
┌─────────▼─────────────────────────────────────────┐
│   Quality-Focused Agent (8096)                    │
│                                                   │
│   For each candidate:                             │
│   - Call Genkit.score_candidate_quality()         │
│   - Detect bias (age, gender, location)           │
│   - Generate recommendation (hire/maybe/reject)   │
│                                                   │
│   Publish: CANDIDATE_SCORED (quality_score ≥ 70) │
└─────────┬─────────────────────────────────────────┘
          │
          │ CANDIDATE_SCORED (high quality)
          │
┌─────────▼──────────────────────────────────────────────┐
│   Scout Coordinator (Engagement Trigger)               │
│                                                        │
│   if score >= 70:                                      │
│     trigger_engagement()                               │
│     Publish: ENGAGEMENT_EVENTS                         │
└─────────┬──────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────┐
│  Personalized Engagement Agent (8093)         │
│                                                │
│  For each candidate:                          │
│  - Call Genkit.generate_engagement_message()  │
│  - send_email() via SMTP                      │
│  - Track engagement history                   │
│                                                │
│  Publish: OUTREACH_SENT                       │
└─────────┬──────────────────────────────────────┘
          │
          │ [Candidate receives email and replies]
          │ Publish: OUTREACH_RESPONSE (positive)
          │
┌─────────▼──────────────────────────────────────────┐
│   Scout Coordinator (Interview Trigger)            │
│                                                    │
│   if response == "positive":                       │
│     trigger_interview()                            │
│     Publish: INTERVIEW_EVENTS                      │
└─────────┬──────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────┐
│   Interviewer Agent (8091) + Services              │
│                                                    │
│   For each of 5 questions:                         │
│   ┌─────────────────────────────────────────────┐  │
│   │ 1. Genkit.generate_interview_question()     │  │
│   │ 2. Avatar.generate_avatar() → 3D avatar    │  │
│   │ 3. Voice.synthesize() → TTS audio          │  │
│   │ 4. Send to candidate with time limit       │  │
│   │ 5. Receive answer                           │  │
│   │ 6. Genkit.evaluate_interview_response()     │  │
│   │ 7. Store evaluation & response              │  │
│   └─────────────────────────────────────────────┘  │
│                                                    │
│   After 5 questions:                               │
│   - Generate interview report (Genkit)             │
│   - Calculate overall_score (avg of evaluations)   │
│   - Generate recommendation                        │
│   - Publish: INTERVIEW_COMPLETED                   │
└─────────┬──────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────┐
│   Tool Leverage Agent (8095)                  │
│                                                │
│   Sync to external systems:                   │
│   - ATS (Workable, Greenhouse, etc.)         │
│   - CRM (Salesforce, HubSpot, etc.)          │
│   - Send candidate to next stage              │
│                                                │
│   Publish: TOOL_SYNCED                        │
└────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────┐
│   Scout Coordinator (Pipeline Complete)       │
│                                                │
│   Pipeline State Machine:                     │
│   INITIATED → SCANNING → SCORING →            │
│   ENGAGING → INTERVIEWING → COMPLETED         │
│                                                │
│   Track metrics:                               │
│   - candidates_found: 20                       │
│   - candidates_contacted: 15                   │
│   - candidates_responded: 10                   │
│   - interviews_scheduled: 10                   │
│   - interviews_completed: 10                   │
│   - strong_hires: 8                            │
└────────────────────────────────────────────────┘
```

---

## 🔑 Key Architectural Patterns

### **1. Event-Driven Architecture**
- All agents communicate via Redis Pub/Sub
- No direct REST calls between agents (loose coupling)
- Message bus routes events to subscribers

### **2. State Machine (Scout Coordinator)**
- Pipeline states: `INITIATED` → `SCANNING` → `SCORING` → `ENGAGING` → `INTERVIEWING` → `COMPLETED`
- State transitions publish events that trigger downstream agents
- Each state transition is logged and trackable

### **3. Async Task Processing**
- Long-running operations run in background (`asyncio.create_task()`)
- API endpoints return immediately with status
- Client polls endpoint or receives webhooks for updates

### **4. Conditional Triggering**
- Quality scoring triggers engagement only if score >= 70
- Engagement triggers interview only on positive response
- Allows filtering of low-quality candidates early

### **5. AI/LLM Integration (Genkit Bridge)**
- All intelligent operations use Google Genkit:
  - Query generation (Boolean Mastery)
  - Scoring (Quality-Focused)
  - Message generation (Personalized Engagement)
  - Question generation (Interviewer)
  - Response evaluation (Interviewer)
  - Report generation (Interviewer)

### **6. Avatar + Voice Synchronization**
- Voice service generates TTS with duration
- Avatar service creates matching animation
- Frontend syncs both for realistic experience
- Lip-sync driven by audio phonemes

---

## 📈 Performance & Scalability Considerations

| Operation | Duration | Bottleneck | Solution |
|-----------|----------|-----------|----------|
| Candidate scanning | 20-30s | Platform API rate limits | Pagination + caching |
| Quality scoring | 2-5s per candidate | Genkit API latency | Batch scoring |
| Message generation | 1-2s | Genkit LLM latency | Pre-caching common templates |
| Voice synthesis | 5-10s | TTS model inference | Async processing, caching |
| Avatar rendering | Real-time | GPU memory | WebGL optimization |
| Interview flow | 10-15 min | User response time | Timeout handling |

---

## 🔒 Data Security & Privacy

1. **Local Processing:** All Granite model inference happens on-device (no data to cloud)
2. **Candidate Data:** Stored locally, encrypted at rest
3. **Voice Recordings:** Can be discarded after interview or encrypted
4. **Interview Transcripts:** Optional, controlled by user settings
5. **API Keys:** Stored in environment variables, never in code

---

This completes the full sourcing workflow from initial request to final interview completion and ATS integration.
