# Development Standards & Security Setup

## Quick Start

### Install Development Environment

```bash
# From project root
bash scripts/setup-dev-env.sh
```

This script will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies (base, dev, and Vetta AI)
- ✅ Verify security tools
- ✅ Install pre-commit hooks
- ✅ Configure git hooks for code quality

### Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-vetta.txt  # Optional: GPU dependencies

# Install pre-commit hooks
pre-commit install
```

## Security Standards

### Required Security Tools

#### 1. **ggshield** (GitGuardian)
Detects secrets, API keys, and sensitive data in code.

```bash
# Scan for secrets before commit (runs automatically)
ggshield secret scan pre-commit

# Manual scan of entire repository
ggshield secret scan repo .

# Scan specific files
ggshield secret scan --staged  # Staged changes
```

**Configuration:**
- Installed via pre-commit hooks
- Prevents commits with exposed secrets
- Severity level: medium and above

#### 2. **bandit**
Security issue scanner for Python code.

```bash
# Scan all Python files
bandit -r . -ll  # Only show medium+ severity

# Scan specific file
bandit myfile.py

# Output in JSON format
bandit -r . -f json -o bandit-report.json
```

**Coverage:**
- SQL injection risks
- Insecure randomness
- Hardcoded secrets
- Unsafe pickle usage
- And 30+ other security checks

#### 3. **safety**
Checks Python dependencies for known security vulnerabilities.

```bash
# Check installed packages
safety check

# Check specific requirements file
safety check -r requirements.txt

# Generate JSON report
safety check --json > safety-report.json
```

#### 4. **ruff**
Fast Python linter with security and style checks.

```bash
# Check all Python files
ruff check .

# Fix issues automatically
ruff check . --fix

# Show specific rules
ruff check . --show-fixes

# Check specific file
ruff check myfile.py
```

## Code Quality Standards

### Formatting & Linting

#### Black (Code Formatter)
Ensures consistent code formatting across the project.

```bash
# Format all Python files
black .

# Format specific file
black myfile.py

# Check without modifying
black --check .

# Set line length
black --line-length=100 .
```

#### isort (Import Sorting)
Organizes and sorts imports consistently.

```bash
# Sort imports in all Python files
isort .

# Sort specific file
isort myfile.py

# Check without modifying
isort --check-only .

# Use Black profile
isort --profile black .
```

#### pylint (Code Analysis)
Analyzes Python code for errors and bad practices.

```bash
# Analyze file
pylint myfile.py

# Analyze directory
pylint src/

# Generate report
pylint --output-format=json src/ > pylint-report.json
```

#### flake8 (Style Enforcement)
Enforces PEP 8 style guide.

```bash
# Check all files
flake8 .

# Check specific file
flake8 myfile.py

# Generate report
flake8 --format=csv . > flake8-report.csv
```

### Type Checking

#### mypy (Static Type Checking)
Verifies type hints and catches type errors.

```bash
# Type check all files
mypy .

# Type check specific file
mypy myfile.py

# Show all errors (strict mode)
mypy --strict .

# Generate report
mypy --html-report . .
```

## Testing Standards

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_voice_service.py

# Run with verbose output
pytest -v tests/

# Run tests in parallel
pytest -n auto tests/

# Run with specific markers
pytest -m "not slow" tests/
```

### Coverage Requirements

- **Minimum:** 80% coverage on new code
- **Target:** 90% coverage overall
- **Critical paths:** 100% coverage

```bash
# Generate coverage report
coverage run -m pytest
coverage report
coverage html  # Opens htmlcov/index.html
```

## Pre-commit Hooks

### Automatic Checks Before Commit

Pre-commit hooks run automatically when you commit. They check:

✅ **Security:**
- ggshield - Secrets detection
- bandit - Security issues
- Private key detection

✅ **Code Quality:**
- Black - Code formatting
- isort - Import sorting
- Ruff - Linting
- Mypy - Type checking

✅ **File Quality:**
- YAML syntax
- JSON syntax
- TOML syntax
- Merge conflicts
- Large files (>1MB)
- Trailing whitespace

✅ **Git:**
- Commitizen - Conventional commits

### Managing Pre-commit

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Skip hooks temporarily
git commit --no-verify

# Uninstall hooks
pre-commit uninstall

# Update hooks to latest versions
pre-commit autoupdate
```

## Continuous Integration Pipeline

### Before Every Commit

```bash
# 1. Format code
black .
isort .

# 2. Run security scans
ggshield secret scan pre-commit
bandit -r . -ll
safety check

# 3. Run linting
ruff check . --fix
pylint src/

# 4. Type checking
mypy .

# 5. Run tests
pytest tests/ --cov=src

# 6. Generate coverage report
coverage report
```

Or run the setup script to configure all at once:

```bash
bash scripts/setup-dev-env.sh
```

## Security Best Practices

### 1. Never Commit Secrets
- API keys
- Database passwords
- Private credentials
- Authentication tokens

**Pre-commit will block these automatically.**

If you accidentally commit a secret:
```bash
# Immediately rotate the secret in the service
# Update git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all
```

### 2. Use Environment Variables

```python
# ❌ BAD
API_KEY = "sk-1234567890abcdef"

# ✅ GOOD
import os
API_KEY = os.getenv("OPENAI_API_KEY")
```

### 3. Validate All Inputs

```python
# Use Pydantic for validation
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    username: str
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v
```

### 4. Keep Dependencies Updated

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade requests

# Update all packages
pip install --upgrade -r requirements.txt
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files, add features
nano src/myfile.py
```

### 3. Run All Checks

```bash
# Pre-commit will run automatically
# Or run manually:
pre-commit run --all-files
```

### 4. Run Tests

```bash
pytest tests/ --cov=src
```

### 5. Commit with Conventional Format

```bash
git commit -m "feat: add new feature

- Detailed description
- More details
- Bug fixes"
```

### 6. Push and Create PR

```bash
git push origin feature/my-feature
```

## Troubleshooting

### Pre-commit Hook Fails

```bash
# Check hook status
pre-commit install

# Run manually to see errors
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### Black & isort Conflict

Ensure both use consistent profiles:

```bash
# .isort.cfg
[settings]
profile=black
```

### Type Checking Too Strict

```bash
# Add type ignore comments where needed
x = some_function()  # type: ignore

# Or configure mypy in pyproject.toml
[tool.mypy]
ignore_missing_imports = true
```

### Secret Detected False Positive

Add to `.gitguardian.yaml`:

```yaml
matches-ignore:
  - name: "example pattern"
    match: "example_.*"
```

## Resources

- **ggshield Docs:** https://docs.gitguardian.com/ggshield
- **Bandit Docs:** https://bandit.readthedocs.io/
- **Black Docs:** https://black.readthedocs.io/
- **pytest Docs:** https://docs.pytest.org/
- **Pre-commit Docs:** https://pre-commit.com/

## Questions or Issues?

Refer to CONTRIBUTING.md for community support channels.

---

**Last Updated:** December 5, 2025  
**Standards Version:** 1.0
