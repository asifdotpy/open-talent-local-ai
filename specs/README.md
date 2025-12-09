# OpenTalent Specifications

Comprehensive documentation for the OpenTalent platform architecture, development guidelines, project governance, and **Specs Driven Development** implementation.

## 🎯 Specs Driven Development (SDD)

OpenTalent now uses **Specs Driven Development** methodology for AI agent mentoring and predictable implementation.

### Phase 5: Desktop App Setup - Complete SDD Implementation

**Status**: ✅ Specifications Ready for Implementation  
**Effort**: 28 hours | **Teams**: 7 task groups | **Target Accuracy**: 95%+

**Core Documents**:
- **[phase-5-desktop-app-setup.md](./phase-5-desktop-app-setup.md)** — Complete specification with requirements, acceptance criteria, architecture
- **[phase-5-task-execution-guide.md](./phase-5-task-execution-guide.md)** — Machine-readable task breakdown for AI agents
- **[phase-5-lessons-learned.md](./phase-5-lessons-learned.md)** — Living document for implementation insights

**What is SDD?**
Specs Driven Development is a comprehensive mentoring framework that:
1. Provides execution blueprints for AI agents
2. Establishes behavioral boundaries through detailed specs
3. Enables feedback loops via Lessons Learned
4. Maintains persistent context across sessions
5. Creates predictable implementation (95%+ first-attempt accuracy)

## Directory Structure

### 🚀 Phase 5: Desktop App Setup
**Specs Driven Development Implementation**
- **[phase-5-desktop-app-setup.md](./phase-5-desktop-app-setup.md)** — Executive summary, business objectives, architecture, requirements (FR1-FR5, NFR1-NFR5), task decomposition, success metrics
- **[phase-5-task-execution-guide.md](./phase-5-task-execution-guide.md)** — 22 specific tasks with acceptance criteria, implementation checklists, code patterns, validation steps
- **[phase-5-lessons-learned.md](./phase-5-lessons-learned.md)** — Template and living record for decisions, patterns, issues, recommendations

**Task Groups** (28 hours total):
- A: Project Scaffolding (4h)
- B: Hardware Detection (5h)
- C: Setup Wizard (8h)
- D: Configuration Management (3h)
- E: Binary Management (4h)
- F-G: Testing & Documentation (5h)

### 📋 [Governance](./governance/)
Community and development guidelines
- **CODE_OF_CONDUCT.md** - Community standards and behavior expectations
- **CONTRIBUTING.md** - How to contribute to the project

### 🏗️ [Project](./project/)
High-level project documentation
- **README.md** - Project overview, features, and getting started guide

### 📐 [Architectural Specs](./architectural-specs/)
System design and architecture specifications
- API contracts and service communication
- Database schemas
- System architecture diagrams
- Component interactions

### 🔌 [API Contracts](./api-contracts/)
API specifications and contracts
- REST API endpoints
- Request/response schemas
- Error handling specifications
- Authentication protocols

### 🔧 [Development](./development/)
Development guidelines and setup instructions
- Local development environment setup
- Testing frameworks and strategies
- Deployment procedures
- Development workflow

### 📖 [Protocols](./protocols/)
Technical protocols and standards
- Communication protocols
- Data formats
- Wire protocols

### 📊 [Requirements](./requirements/)
Functional and non-functional requirements
- User stories
- Feature specifications
- Performance requirements

### 👥 [User Stories](./user-stories/)
User-centric requirements and personas
- Candidate journeys
- Recruiter workflows
- Interviewer experiences

### 🚚 [Migration](./migration/)
Project migration documentation
- **MIGRATION_SUMMARY.md** - OpenTalent migration from talent-ai-platform

---

## Quick Navigation

**For Phase 5 Implementation (START HERE)**:
1. **Understand**: [phase-5-desktop-app-setup.md](./phase-5-desktop-app-setup.md) — Business objectives, architecture, requirements
2. **Execute**: [phase-5-task-execution-guide.md](./phase-5-task-execution-guide.md) — Implement specific tasks step-by-step
3. **Learn**: [phase-5-lessons-learned.md](./phase-5-lessons-learned.md) — Capture insights and document patterns
4. **Context**: [AGENTS.md](../AGENTS.md) — Architecture overview and hardware specifications

**Getting Started (General)**:
1. Review [CODE_OF_CONDUCT.md](./governance/CODE_OF_CONDUCT.md) for community standards
2. Read [CONTRIBUTING.md](./governance/CONTRIBUTING.md) for contribution guidelines
3. Check [README.md](./project/README.md) for project overview

**Development**:
- See [Development](./development/) for setup and testing guides
- Check [API Contracts](./api-contracts/) for API specifications
- Review [Architectural Specs](./architectural-specs/) for system design

**Project History**:
- See [Migration](./migration/) for migration documentation and status

---

## 🎓 SDD Principles Applied in Phase 5

### Precision Over Ambiguity
- Every requirement is specific and measurable
- Edge cases and constraints explicitly listed
- Acceptance criteria are verifiable checkboxes

### Specification as Contract
- Success metrics quantified (e.g., "<5s startup time")
- AI agents validate directly against specs
- Requirements map to specific tasks

### Orchestration Over Implementation
- Specs define WHAT, not HOW (mostly)
- Code patterns provided as templates
- Developers have flexibility within boundaries

### Iterative Spec Evolution
- Lessons Learned captures change drivers
- Decisions documented with rationales
- Future phases incorporate learnings

### Predictable Execution
- 22 small tasks beat 1 large task
- 95%+ target accuracy on first attempt
- Dependency sequencing ensures efficiency

---

**Last Updated:** December 6, 2025  
**Current Phase**: 5 (Desktop App Setup)  
**Framework**: Specs Driven Development (SDD)  
**Status**: Ready for Implementation
