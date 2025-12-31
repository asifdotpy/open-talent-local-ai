# OpenTalent Developer Setup Guide

This guide provides comprehensive, step-by-step instructions for setting up the OpenTalent project for development on a fresh machine. OpenTalent is a desktop-first, local-AI application, requiring both Node.js (for the Electron app) and Python (for the microservices).

## 1. Prerequisites

Ensure the following tools are installed on your system:

| Prerequisite | Minimum Version | Purpose |
| :--- | :--- | :--- |
| **Git** | Latest | Source code management |
| **Node.js** | 20.x | Electron desktop application runtime |
| **Python** | 3.12 | Backend microservices runtime |
| **Ollama** | Latest (Optional) | Local LLM server for development (bundled in production) |

### 1.1. Installing Dependencies

**Node.js:** We recommend using a version manager like `nvm` to manage Node.js versions.

```bash
# Install nvm (if not already installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# Load nvm (may require restarting your terminal)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
# Install and use the required version
nvm install 20
nvm use 20
```

**Python:** Ensure Python 3.12 is available and set up a virtual environment.

```bash
# Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
```

## 2. Project Setup

### 2.1. Clone the Repository

Clone the repository using the correct path:

```bash
git clone https://github.com/asifdotpy/open-talent-local-ai.git open-talent
cd open-talent
```

### 2.2. Install Dependencies

The project has dependencies for both the desktop application (Node.js) and the microservices (Python).

#### A. Desktop Application Dependencies (Node.js)

Navigate to the `desktop-app` directory and install the Node.js packages. Due to potential peer dependency conflicts, the `--legacy-peer-deps` flag is recommended.

```bash
cd desktop-app
npm install --legacy-peer-deps
cd .. # Return to project root
```

#### B. Microservices Dependencies (Python)

Install the Python dependencies in your activated virtual environment.

```bash
# Ensure your virtual environment is active
source .venv/bin/activate

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional, for running tests/linters)
pip install -r requirements-dev.txt
```

## 3. Running the Application

### 3.1. Start the Demo Environment (Recommended)

The repository includes scripts to start all necessary services (Ollama, Piper, Microservices) and the desktop application in a demo mode.

```bash
# Start all services and the desktop app
./start-demo.sh

# Access the application (usually at http://localhost:3000)
# open http://localhost:3000

# Stop all services when done
./stop-demo.sh
```

### 3.2. Manual Development Start

If you prefer to run the components separately:

1.  **Start Microservices:** (Requires Ollama to be running or mocked)
    ```bash
    # Example: Start all services using the run script
    ./run_all_services.sh
    ```

2.  **Start Desktop App (Electron):**
    ```bash
    cd desktop-app
    npm run dev
    ```

## 4. Running Tests

The desktop application tests use Jest, and the microservices use Pytest.

### 4.1. Desktop App Tests (TypeScript/Jest)

Run the tests from the `desktop-app` directory:

```bash
cd desktop-app
# Run all tests
./node_modules/.bin/jest --watchAll=false

# Note: If tests fail due to API contract or utility errors (e.g., B-01, B-02, B-03),
# you must resolve these blockers before the test suite will pass cleanly.
```

### 4.2. Microservices Tests (Python/Pytest)

Run the tests from the project root:

```bash
# Ensure your virtual environment is active
source .venv/bin/activate

# Run all Python tests
pytest
```

## 5. Troubleshooting Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `sh: 1: jest: not found` | Jest is installed locally in `node_modules` but not globally. | Use the local binary path: `./node_modules/.bin/jest` |
| `npm ERR! ERESOLVE` | Peer dependency conflicts in Node.js packages. | Re-run `npm install` with the `--legacy-peer-deps` flag. |
| `TypeError: AbortSignal.timeout is not a function` | Node.js version is too old or the environment is missing a polyfill. | Ensure you are using **Node.js v20+** or update the environment. |
| `Cannot find module '...'` | Missing utility files or incorrect import paths. | Check the `desktop-app/src/` directory for missing files (e.g., `lib/utils.ts`) and correct the import paths. |

---
**Document Created:** December 31, 2025
**Author:** Manus AI
**Source:** Project Audit and Repository Analysis
[1]: https://github.com/asifdotpy/open-talent-local-ai "OpenTalent Repository"
[2]: https://nodejs.org/en/download/package-manager "Node.js Installation"
[3]: https://www.python.org/downloads/ "Python Installation"
[4]: https://ollama.com/ "Ollama Local LLM Server"
