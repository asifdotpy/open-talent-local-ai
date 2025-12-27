# Contributing to OpenTalent

Thank you for your interest in contributing to the OpenTalent! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Naming Conventions](#naming-conventions)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Docker Compose Usage](#docker-compose-usage)
- [Agent Development](#agent-development)
- [Microservice Development](#microservice-development)

---

## Getting Started

### Prerequisites

- **Python**: 3.11+ with virtual environment support
- **Node.js**: 18+ for frontend and Genkit service
- **Docker**: Latest version with docker-compose
- **Git**: With submodule support
- **Redis**: For agent communication (or use Docker)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/asifdotpy/open-talent.git
cd open-talent

# Initialize submodules
git submodule update --init --recursive

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Opening the Workspace

For the best development experience, use the VS Code workspace file:

```bash
code open-talent.code-workspace
```

This opens all submodules in a multi-root workspace.

---

## Development Workflow

### Branch Strategy

We follow a **feature branch workflow**:

1. **main**: Production-ready code, protected branch
2. **feature/**: Feature development (e.g., `feature/add-candidate-scoring`)
3. **fix/**: Bug fixes (e.g., `fix/avatar-sync-issue`)
4. **docs/**: Documentation updates (e.g., `docs/update-api-specs`)
5. **refactor/**: Code refactoring (e.g., `refactor/agent-message-bus`)

### Creating a Feature Branch

```bash
# Always branch from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add candidate scoring algorithm"

# Push to remote
git push origin feature/your-feature-name
```

### Commit Message Format

We use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(agents): add boolean mastery agent for query generation"
git commit -m "fix(interview-service): resolve WebRTC signaling timeout"
git commit -m "docs(api): update OpenAPI specs for voice service"
git commit -m "test(quality-agent): add unit tests for bias detection"
```

---

## Coding Standards

### Python Code Style

We follow **PEP 8** with the following specifics:

- **Line Length**: 100 characters (not 79)
- **Formatter**: Black (configured for 100 chars)
- **Linter**: Pylint or Ruff
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Google-style docstrings for all public functions/classes

**Example:**

```python
from typing import List, Optional
from pydantic import BaseModel

class CandidateProfile(BaseModel):
    """Represents a candidate profile with scoring metadata.

    Attributes:
        candidate_id: Unique identifier for the candidate
        skills: List of technical skills
        experience_years: Total years of professional experience
        overall_score: Computed quality score (0-100)
    """
    candidate_id: str
    skills: List[str]
    experience_years: int
    overall_score: Optional[float] = None

def calculate_skill_match(
    candidate_skills: List[str],
    required_skills: List[str]
) -> float:
    """Calculate the percentage of required skills present in candidate profile.

    Args:
        candidate_skills: List of skills from candidate's profile
        required_skills: List of skills required for the job

    Returns:
        Percentage match as a float between 0 and 100

    Raises:
        ValueError: If either list is empty
    """
    if not candidate_skills or not required_skills:
        raise ValueError("Skill lists cannot be empty")

    matched = set(candidate_skills) & set(required_skills)
    return (len(matched) / len(required_skills)) * 100
```

### TypeScript/JavaScript Code Style

For frontend and Genkit service:

- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Safety**: Strict TypeScript mode
- **Naming**: camelCase for variables/functions, PascalCase for components

### Import Organization

Organize imports in three groups with blank lines between:

```python
# Standard library
import asyncio
import logging
from typing import List, Dict

# Third-party
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local/project
from shared.models import CandidateProfile, AgentMessage
from shared.message_bus import MessageBus
from shared.service_clients import ServiceClient
```

### Error Handling

Always use specific exception types and provide context:

```python
# Bad
try:
    result = await api_call()
except:
    print("Error occurred")

# Good
try:
    result = await api_call()
except httpx.TimeoutException as e:
    logger.error(f"API call timed out: {e}")
    raise HTTPException(status_code=504, detail="External service timeout")
except httpx.HTTPError as e:
    logger.error(f"HTTP error during API call: {e}")
    raise HTTPException(status_code=502, detail="External service error")
```

### Logging

Use Python's `logging` module with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Candidate profile received: %s", candidate_id)
logger.info("Scoring candidate %s with %d skills", candidate_id, len(skills))
logger.warning("Missing required skill: %s for candidate %s", skill, candidate_id)
logger.error("Failed to score candidate %s: %s", candidate_id, error)
logger.critical("Redis connection lost, cannot process candidates")
```

**Never log sensitive information:**
- ❌ API keys, passwords, tokens
- ❌ Personal candidate data (full names, emails, phone numbers)
- ❌ Salary information
- ✅ Anonymized IDs, aggregate metrics, system events

---

## Naming Conventions

### Files and Directories

| Type | Convention | Examples |
|------|-----------|----------|
| **Directories** | `kebab-case` | `boolean-mastery-agent`, `interview-service` |
| **Python files** | `snake_case.py` | `message_bus.py`, `service_clients.py` |
| **Shell scripts** | `kebab-case.sh` | `setup-voice-service.sh`, `start-agents.sh` |
| **Markdown docs** | `SCREAMING_SNAKE_CASE.md` | `CONTRIBUTING.md`, `API_SPECIFICATION.md` |
| **Config files** | `lowercase` or `kebab-case` | `Dockerfile`, `docker-compose.yml`, `.env.example` |

### Code Naming

| Element | Convention | Examples |
|---------|-----------|----------|
| **Variables** | `snake_case` | `candidate_id`, `skill_match_score` |
| **Functions** | `snake_case` | `calculate_score()`, `send_outreach()` |
| **Classes** | `PascalCase` | `CandidateProfile`, `MessageBus` |
| **Constants** | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| **Private** | `_leading_underscore` | `_internal_method()`, `_cache` |

### API Endpoints

Use RESTful naming conventions:

```
GET    /candidates           # List candidates
POST   /candidates           # Create candidate
GET    /candidates/{id}      # Get specific candidate
PUT    /candidates/{id}      # Update candidate
DELETE /candidates/{id}      # Delete candidate

POST   /pipelines/start      # Start pipeline
GET    /pipelines/{id}       # Get pipeline status
POST   /pipelines/{id}/pause # Pause pipeline
```

---

## Testing Requirements

### Test Coverage

- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 100% coverage required for scoring algorithms, data transformations
- **Integration Tests**: Required for all agent-to-agent communication

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/agents/test_quality_agent.py -v

# Run specific test
pytest tests/agents/test_quality_agent.py::test_skill_match_calculation -v
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock

@pytest.fixture
def sample_candidate():
    """Fixture providing a sample candidate profile."""
    return CandidateProfile(
        candidate_id="cand_123",
        skills=["Python", "Django", "PostgreSQL"],
        experience_years=5
    )

@pytest.mark.asyncio
async def test_calculate_skill_match(sample_candidate):
    """Test skill match calculation returns correct percentage."""
    required_skills = ["Python", "Django", "AWS"]

    result = calculate_skill_match(
        sample_candidate.skills,
        required_skills
    )

    assert result == 66.67  # 2 out of 3 skills matched

@pytest.mark.asyncio
async def test_score_candidate_api_call():
    """Test candidate scoring makes correct API calls."""
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {"score": 85}

        agent = QualityAgent()
        result = await agent.score_candidate("cand_123")

        assert result["score"] == 85
        mock_post.assert_called_once()
```

### Test Organization

```
tests/
├── unit/                    # Unit tests
│   ├── agents/
│   │   ├── test_quality_agent.py
│   │   └── test_engagement_agent.py
│   └── shared/
│       └── test_message_bus.py
├── integration/             # Integration tests
│   ├── test_agent_pipeline.py
│   └── test_service_integration.py
├── fixtures/               # Test fixtures and data
│   └── sample_candidates.json
└── conftest.py            # Shared pytest configuration
```

---

## Documentation

### Code Documentation

**Required Documentation:**
- README.md in every service/agent directory
- Docstrings for all public functions and classes
- Inline comments for complex logic
- API documentation (OpenAPI/Swagger for REST APIs)

### README Structure

Every agent and service should have a README with:

1. **Overview**: What the service does
2. **Features**: Key capabilities
3. **Installation**: Setup instructions
4. **Configuration**: Environment variables
5. **Running**: How to start the service
6. **API Endpoints**: Available endpoints with examples
7. **Event Handling**: Topics subscribed/published (for agents)
8. **Docker**: Container build and run instructions
9. **Development**: Dev mode instructions
10. **Troubleshooting**: Common issues and solutions

### Updating Documentation

When adding features:
- ✅ Update service README
- ✅ Update API specs in `docs/api-specs/`
- ✅ Add/update examples in code
- ✅ Update AGENTS.md or main README if architecture changes
- ✅ Add entry to CHANGELOG.md

---

## Pull Request Process

### Before Creating a PR

1. ✅ All tests pass locally
2. ✅ Code follows style guidelines (run linters)
3. ✅ Documentation is updated
4. ✅ No secrets or sensitive data in commits
5. ✅ Commits are logically organized

### Creating a PR

1. Push your branch to GitHub
2. Open a Pull Request to `main`
3. Fill out the PR template completely
4. Link related issues
5. Request review from team members

### PR Title Format

```
<type>(<scope>): <description>

Examples:
feat(agents): add boolean mastery agent for query generation
fix(interview-service): resolve WebRTC signaling timeout
docs(api): update OpenAPI specs for voice service
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] Code comments added

## Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No linter warnings
- [ ] No secrets in code
- [ ] Reviewed own code
```

### Review Process

- **Required Approvals**: At least 1 team member
- **Automated Checks**: All CI/CD checks must pass
- **Security Scan**: GitGuardian and CodeQL must pass
- **Test Coverage**: Must maintain or improve coverage

---

## Docker Compose Usage

The repository contains multiple `docker-compose.yml` files for different purposes:

### Main Docker Compose Files

| File | Purpose | Usage |
|------|---------|-------|
| `config/docker-compose.yml` | **Primary orchestration** - All services | `docker-compose -f config/docker-compose.yml up` |
| `agents/docker-compose.yml` | **Agent stack only** - All AI agents | `cd agents && docker-compose up` |
| `microservices/docker-compose.yml` | **Microservice stack only** - Backend services | `cd microservices && docker-compose up` |
| `microservices/interview-service/docker-compose.yml` | **Single service** - Interview service only | `cd microservices/interview-service && docker-compose up` |

### Starting Services

**Start all services (recommended for full platform):**
```bash
docker-compose -f config/docker-compose.yml up -d
```

**Start only agents:**
```bash
cd agents
docker-compose up -d
```

**Start only microservices:**
```bash
cd microservices
docker-compose up -d
```

**Start specific service:**
```bash
docker-compose -f config/docker-compose.yml up -d interview-service
```

### Development Mode

For development with hot-reload:

```bash
# Start with logs attached
docker-compose -f config/docker-compose.yml up

# Rebuild after code changes
docker-compose -f config/docker-compose.yml up --build

# Restart specific service
docker-compose -f config/docker-compose.yml restart interview-service
```

### Viewing Logs

```bash
# All services
docker-compose -f config/docker-compose.yml logs -f

# Specific service
docker-compose -f config/docker-compose.yml logs -f scout-coordinator

# Last 100 lines
docker-compose -f config/docker-compose.yml logs --tail=100 interview-service
```

### Stopping Services

```bash
# Stop all services
docker-compose -f config/docker-compose.yml down

# Stop and remove volumes (⚠️ deletes data)
docker-compose -f config/docker-compose.yml down -v

# Stop specific service
docker-compose -f config/docker-compose.yml stop interview-service
```

---

## Agent Development

### Creating a New Agent

1. **Create directory structure:**
```bash
mkdir -p agents/your-agent-name
cd agents/your-agent-name
```

2. **Create required files:**
```
your-agent-name/
├── main.py              # Entry point with FastAPI app
├── README.md            # Agent documentation
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── Dockerfile           # Container definition
└── src/
    ├── __init__.py
    ├── agent.py         # Core agent logic
    ├── models.py        # Pydantic models
    └── utils.py         # Utility functions
```

3. **Use shared infrastructure:**
```python
from shared.models import AgentMessage, CandidateProfile
from shared.message_bus import MessageBus
from shared.service_clients import ServiceClient
```

4. **Implement event handling:**
```python
async def handle_message(message: AgentMessage):
    """Process incoming messages from Redis."""
    logger.info(f"Received message: {message.message_type}")
    # Process message
    # Publish response
    await message_bus.publish("agents:response", response)
```

5. **Add health endpoint:**
```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "your-agent-name",
        "version": "1.0.0"
    }
```

### Agent Checklist

- ✅ README.md with complete documentation
- ✅ .env.example with all required variables
- ✅ Dockerfile for containerization
- ✅ Health endpoint implemented
- ✅ Redis pub/sub integration
- ✅ Error handling and logging
- ✅ Unit tests
- ✅ Integration tests with other agents

---

## Microservice Development

### Creating a New Microservice

Follow the same pattern as existing services:

1. **Directory structure:**
```
service-name/
├── main.py              # FastAPI application
├── README.md
├── requirements.txt
├── .env.example
├── Dockerfile
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── routes.py        # API routes
│   └── services.py      # Business logic
└── tests/
    └── test_service.py
```

2. **Use consistent patterns:**
- FastAPI for REST APIs
- Pydantic for validation
- SQLAlchemy for database access (if needed)
- Async/await for I/O operations

3. **Add OpenAPI documentation:**
```python
from fastapi import FastAPI

app = FastAPI(
    title="Service Name",
    description="Service description",
    version="1.0.0"
)
```

---

## Questions?

- 📖 Check [AGENTS.md](./AGENTS.md) for architecture details
- 📖 See [GEMINI.md](./GEMINI.md) for comprehensive project guide
- 💬 Open a GitHub Discussion for questions
- 🐛 Create an issue for bugs

---

Thank you for contributing to OpenTalent! 🚀
