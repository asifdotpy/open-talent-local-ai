# OpenTalent Testing Guide 🧪

This guide explains how to test the OpenTalent platform at different levels, from automated verification scripts to manual end-to-end testing.

## 1. Automated Release Verification (Recommended)
This is the fastest way to verify that the core system components and release requirements are met. It checks compilation, test suites, gateway routes, and schemas.

```bash
# From the project root
chmod +x verify-release.sh
./verify-release.sh
```

**What it does:**
- Verifies Desktop App TypeScript compilation.
- Runs the full Jest test suite (150+ tests).
- Checks Gateway routing for Scout and Voice services.
- Validates the presence of critical security/notification schemas.

---

## 2. Integrated Demo Mode
To see the full application running with simulated/mocked services (e.g., if you don't have all local LLMs running):

```bash
# Start all services and the desktop app
./start-demo.sh

# The desktop app window should open automatically.
# Access the web-based gateway UI (optional): http://localhost:8009

# To stop everything
./stop-demo.sh
```

---

## 3. Manual Component Testing
If you are developing a specific part of the app, you can run components individually.

### A. Desktop Application
```bash
cd desktop-app
npm install --legacy-peer-deps  # If not already done
npm run dev
```

### B. Backend API Gateway
The Gateway acts as the entry point for the desktop app to reach all other microservices.
```bash
# Ensure your venv is active
source .venv/bin/activate
cd services/desktop-integration-service
python app/main.py
```

---

## 4. Run Automated Test Suites

### Desktop App (Jest)
Comprehensive tests for React components, hooks, and services.
```bash
cd desktop-app
npm test                # Interactive mode
npm test -- --watchAll=false  # Run once
```

### Backend Microservices (Pytest)
```bash
# Run all backend tests
pytest

# Run tests for a specific service
pytest tests/scout-service/
```

---

## 5. Troubleshooting Tests

- **Connection Refused**: Many tests attempt to reach local services (ports 8000, 8009, etc.). This is normal; the app is designed to fall back to internal logic or skip E2E tests if the backend is offline.
- **Node Version**: Ensure you are using Node 20.x (`nvm use 20`).
- **Python Version**: Ensure you are using Python 3.12.

---

**Release Status**: `v1.0.0-release` is verified and tagged. ✅
