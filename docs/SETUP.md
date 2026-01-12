# Local Development Setup Guide

This guide provides instructions for setting up the OpenTalent monorepo on your local machine for development and testing.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for desktop & frontend components)
- **Git**
- **Docker & Docker Compose** (optional, but recommended for database services)

## Service Port Mapping (Standardized)

All services in the monorepo follow a standardized port mapping to avoid conflicts:

| Port | Service | Description |
| :--- | :--- | :--- |
| **8001** | `user-service` | Identity and User Management |
| **8002** | `conversation-service` | AI Conversation Orchestration |
| **8004** | `avatar-service` | Real-time AI Video Avatar |
| **8005** | `interview-service` | Core Interview Lifecycle |
| **8006** | `candidate-service` | Candidate Profiling & Resumes |
| **8007** | `project-service` | Job & Project Management |
| **8008** | `granite-interview` | Granite LLM Training & Inference |
| **8009** | `desktop-integration` | Desktop App Gateway |
| **8010** | `security-service` | Authentication Gateway |
| **8011** | `notification-service` | Email, SMS, & Push |
| **8012** | `analytics-service` | Bias & Sentiment Analytics |
| **8013** | `scout-service` | Talent Sourcing & Discovery |
| **8014** | `ai-auditing-service` | Policy Enforcement |
| **8015** | `voice-service` | Voice Processing (STT/TTS) |
| **8016** | `explainability` | AI Reasoning Visualizer |

## Getting Started

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/asifdotpy/open-talent-local-ai.git
    cd open-talent
    ```

2.  **Install Dependencies**
    Each service maintains its own `requirements.txt`. You can install them individually or use the provided management scripts.
    ```bash
    # Example for Interview Service
    cd services/interview-service
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Copy `.env.example` to `.env` in each service directory and update necessary values like API keys and database URLs.

4.  **Running Services**
    You can start services individually using Uvicorn:
    ```bash
    uvicorn main:app --port 8005 --reload
    ```

## Database Initialization

Most services use SQLite by default for easy local setup. Databases are typically initialized on the first run of the service using SQLAlchemy.

- `user-service`: `users.db`
- `project-service`: `projects.db`
- `interview-service`: `interviews.db` (WIP)

## Linting & Quality

We use `ruff` for linting. Ensure your code passes ruff checks before submitting PRs:
```bash
ruff check services/
```
