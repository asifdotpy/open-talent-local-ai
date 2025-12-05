# TalentAI Platform

[![Status: In Dev](https://img.shields.io/badge/status-in_dev-blue)](./GEMINI.md)

Welcome to the TalentAI Platform, a web-based recruitment system that uses AI agents to automate and enhance the hiring process. This repository is the root of the entire platform, containing all microservice code, infrastructure configurations, and technical specifications.

---

## 🚀 Project Overview

The TalentAI platform is built on a modern, scalable architecture designed for rapid dev and long-term maintainability. Our primary goal is to deliver a robust MVP that showcases the power of AI in streamlining recruitment workflows.

This `README.md` serves as the central dashboard for the project. Use the links below to navigate to our key sources of truth.

## 💡 VS Code & Git Submodules

This project uses Git submodules for modular dev. If you see a VS Code warning about submodules not being opened automatically, this is normal behavior for performance and security reasons.

**Quick Solutions:**
- 📖 **[Complete VS Code Submodule Guide](./docs/VSCODE_SUBMODULE_GUIDE.md)** - Detailed explanation and solutions
- 🔧 **Use the workspace file**: Open `talent-ai-platform.code-workspace` for multi-repo dev
- 🛠️ **Management script**: Run `./scripts/manage-submodules.sh help` for submodule operations

**Quick Start:**
```bash
# Open the multi-root workspace
code talent-ai-platform.code-workspace

# Or manage submodules with our helper script
./scripts/manage-submodules.sh status
./scripts/manage-submodules.sh open talent-ai-microservices
```

## 📂 Directory Structure

The project is organized into multiple submodules:

-   **[`microservices/`](./microservices/)**: Contains the source code for all backend microservices (FastAPI, Python) with EU AI compliance features.
-   **[`agents/`](./agents/)**: AI agents for specialized recruitment tasks (scouting, engagement, quality assessment).
-   **[`infrastructure/`](./infrastructure/)**: Contains the Infrastructure as Code (Terraform) for our Google Cloud Platform environment.
-   **[`frontend/`](./frontend/)**: React-based frontend applications (admin panel, dashboard, landing page).
-   **[`ai-orchestra-simulation/`](./ai-orchestra-simulation/)**: AI avatar simulation and testing environment.

---

## 📚 Key Documents & Knowledgebase

This is the master index for our project's knowledgebase. For any questions about architecture, standards, or current tasks, start here.

| Document / Section | Description |
| :--- | :--- |
| 📖 **[Dev Guide](./DEVELOPMENT_GUIDE.md)** | **Your first stop.** The authoritative guide for local setup, Git workflow, coding standards, and testing procedures. |
| 🤗 **[Hugging Face Setup](./docs/development/HUGGINGFACE_SETUP_GUIDE.md)** | Complete guide for Hugging Face model management, dataset handling, and large file configuration. |
| 💎 **[Detailed Project Guide](./quarkdown-specs/GEMINI.md)** | The comprehensive guide to the project's architecture, full tech stack, and dev principles. |
| 🗺️ **[System Architecture Diagrams](./quarkdown-specs/architecture/diagrams/)** | Visual diagrams illustrating the high-level system context and microservice interactions. |
| ⚖️ **[Architectural Decision Records](./quarkdown-specs/architecture/decisions/)** | The official log of all significant technical decisions and their rationale. |
| ✅ **[Current Task Plans](./quarkdown-specs/TASKS/)** | Detailed plans and status updates for ongoing dev tasks. |

---

## 🎯 Current Dev Focus

Our current efforts are concentrated on the following high-priority workstreams:

1.  **✅ AI Avatar Interview Platform MVP:** **COMPLETE** - All four core microservices implemented with full end-to-end integration
2.  **Frontend Integration:** Connecting React dashboard to interview APIs
3.  **Production API Research:** Investigating OpenAI TTS and Anam.ai avatar platform integration
4.  **Agent-Microservice Integration:** Connecting AI agents with microservices for end-to-end recruitment workflows
5.  **Infrastructure Deployment:** Preparing for the initial deployment of our GCP infrastructure with microservices orchestration

---

## 🛠️ Core Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | FastAPI (Python 3.11+) |
| **Frontend** | React (TypeScript), Vite, Tailwind CSS |
| **Infrastructure** | Google Cloud Platform (GCP), GKE, Terraform |
| **Authentication** | Keycloak |
| **AI / Media** | Remotion, LangChain, OpenAI |
| **Database** | PostgreSQL, SQLAlchemy |

---

## 🔒 Security & Compliance

| Tool | Purpose | Status |
| :--- | :--- | :--- |
| **GitGuardian** | Pre-commit secret scanning | ✅ Active |
| **GitHub CodeQL** | Automated vulnerability scanning | ✅ Active |
| **License Compliance** | MIT license enforcement | ✅ Resolved |
| **Security Policy** | Vulnerability reporting process | ✅ Published |

### Security Setup
- **GitGuardian**: Pre-commit secret scanning on all commits
- **CodeQL Analysis**: Automated vulnerability scanning on PRs and pushes
- **Security Policy**: Published vulnerability reporting process
- **CI Security**: GitHub Actions use secure secret references

📖 **[GitGuardian Setup Guide](./docs/GITGUARDIAN_SETUP.md)** - Complete security configuration and usage instructions
📖 **[Security Policy](./SECURITY.md)** - Vulnerability reporting and security measures

---

## 📖 User Documentation

Comprehensive user guides for all platform users:

| User Type | Guide | Description |
|-----------|-------|-------------|
| 👥 **All Users** | **[Getting Started](./docs/user-guides/getting-started.md)** | Platform basics and initial setup |
| 🎯 **Candidates** | **[Candidate Guide](./docs/user-guides/candidates/README.md)** | Complete interview preparation and process |
| 👔 **Recruiters** | **[Recruiter Guide](./docs/user-guides/recruiters/README.md)** | Hiring workflows and candidate management |
| 👨‍💼 **Interviewers** | **[Interviewer Guide](./docs/user-guides/interviewers/README.md)** | Interview monitoring and customization |
| ⚙️ **Administrators** | **[Admin Guide](./docs/user-guides/administrators/README.md)** | System management and configuration |
| ❓ **FAQ** | **[Frequently Asked Questions](./docs/user-guides/faq.md)** | Answers to common questions |
| 🔧 **Troubleshooting** | **[Technical Support](./docs/user-guides/troubleshooting.md)** | Solutions for common issues |

📖 **[Documentation Overview](./docs/user-guides/overview.md)** - Complete navigation guide for all documentation
