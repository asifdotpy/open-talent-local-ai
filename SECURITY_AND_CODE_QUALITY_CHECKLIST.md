# Security and Code Quality Checklist - OpenTalent Platform

**Date:** December 14, 2025  
**Purpose:** Comprehensive security, type safety, and code quality verification  
**Status:** 🟡 Implementation Guide

---

## Table of Contents

1. [Automated Tools Setup](#automated-tools-setup)
2. [Security Checklist](#security-checklist)
3. [Type Safety & Validation Checklist](#type-safety--validation-checklist)
4. [API Security Checklist](#api-security-checklist)
5. [Code Quality Checklist](#code-quality-checklist)
6. [CI/CD Integration](#cicd-integration)
7. [Pre-Commit Hooks](#pre-commit-hooks)

---

## Automated Tools Setup

### 1. Security Scanning Tools

#### **Bandit** - Python Security Linter
```bash
# Install
pip install bandit[toml]

# Run security scan
bandit -r services/ -f json -o bandit-report.json

# Run with specific severity
bandit -r services/ -ll -ii

# Configuration file: pyproject.toml
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv", ".venv-1"]
skips = ["B101", "B601"]  # Skip assert and shell=True warnings if justified
```

**What it catches:**
- Hardcoded passwords/secrets
- SQL injection vulnerabilities
- Use of `exec()`, `eval()`
- Insecure cryptographic functions
- Weak random number generation
- Unsafe YAML loading

#### **Safety** - Dependency Vulnerability Scanner
```bash
# Install
pip install safety

# Check dependencies
safety check --json

# Check specific requirements file
safety check -r requirements.txt

# Auto-fix known vulnerabilities
pip-audit --fix
```

**What it catches:**
- Known CVEs in dependencies
- Outdated packages with security fixes
- Malicious packages

#### **Semgrep** - Advanced Pattern Matching
```bash
# Install
pip install semgrep

# Run security rules
semgrep --config=auto services/

# Run specific rulesets
semgrep --config "p/python" services/
semgrep --config "p/security-audit" services/
semgrep --config "p/jwt" services/

# Custom rules for FastAPI
semgrep --config custom-rules.yaml services/
```

**What it catches:**
- Authentication bypasses
- Authorization flaws
- Injection vulnerabilities
- Cryptographic issues
- Custom anti-patterns (like loose enum validation)

#### **Trivy** - Container/Filesystem Scanner
```bash
# Install
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan filesystem
trivy fs .

# Scan for secrets
trivy fs --scanners secret .

# Scan Docker images (when you containerize)
trivy image your-image:tag
```

---

### 2. Type Safety & Validation Tools

#### **MyPy** - Static Type Checker
```bash
# Install
pip install mypy

# Run type checking
mypy services/ --strict

# Configuration: mypy.ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
```

**What it catches:**
- Missing type annotations
- Type mismatches
- None/Optional issues
- Return type inconsistencies

#### **Pydantic Validator** - Model Validation
```bash
# Already using Pydantic, ensure all models have:
# 1. Field validation
# 2. Custom validators
# 3. Proper Enum types (not loose strings)

# Add Pydantic strict mode
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)
```

#### **Pyright** - Microsoft's Type Checker (Alternative to MyPy)
```bash
# Install
npm install -g pyright

# Run
pyright services/

# Configuration: pyrightconfig.json
{
  "include": ["services"],
  "exclude": ["**/node_modules", "**/__pycache__"],
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.12"
}
```

---

### 3. Code Quality Tools

#### **Ruff** - Fast Python Linter (Replaces Flake8, isort, pylint)
```bash
# Install
pip install ruff

# Run linter
ruff check services/

# Run with auto-fix
ruff check --fix services/

# Configuration: pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "S",   # flake8-bandit (security)
    "T20", # flake8-print
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # function call in argument defaults
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
```

**What it catches:**
- Code style violations
- Unused imports/variables
- Security issues (via bandit rules)
- Complexity issues
- Anti-patterns

#### **Black** - Code Formatter
```bash
# Install
pip install black

# Format code
black services/

# Check without changing
black --check services/

# Configuration: pyproject.toml
[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'
```

#### **Pylint** - Comprehensive Linter
```bash
# Install
pip install pylint

# Run
pylint services/

# Configuration: .pylintrc
[MASTER]
disable=
    C0111,  # missing-docstring
    R0903,  # too-few-public-methods
    
[FORMAT]
max-line-length=100
```

---

## Security Checklist

### 🔐 Authentication & Authorization

- [ ] **No Hardcoded Secrets**
  ```bash
  # Check with multiple tools
  bandit -r services/ -f json | jq '.results[] | select(.issue_confidence == "HIGH")'
  trivy fs --scanners secret .
  git secrets --scan-history  # Install git-secrets first
  ```
  
- [ ] **JWT Token Security**
  - [ ] Secret key stored in environment variables (not hardcoded)
  - [ ] Token expiration implemented (ACCESS_TOKEN_EXPIRE_MINUTES)
  - [ ] Token blacklist/revocation mechanism exists
  - [ ] Algorithm explicitly set (e.g., HS256, not "none")
  - [ ] Token signature verification enforced
  ```python
  # ❌ BAD
  SECRET_KEY = "your-secret-key-change-in-production"
  
  # ✅ GOOD
  import os
  SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
  if not SECRET_KEY:
      raise ValueError("JWT_SECRET_KEY environment variable required")
  ```

- [ ] **Password Security**
  - [ ] Passwords hashed with secure algorithm (bcrypt, argon2, not SHA256)
  - [ ] Minimum password complexity enforced
  - [ ] Password reset tokens expire
  - [ ] Rate limiting on login attempts
  ```python
  # ❌ BAD: SHA256 is NOT a password hashing algorithm
  from hashlib import sha256
  hash_password = lambda p: sha256(p.encode()).hexdigest()
  
  # ✅ GOOD: Use bcrypt or passlib
  from passlib.context import CryptContext
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  hash_password = lambda p: pwd_context.hash(p)
  ```

- [ ] **Authorization Checks**
  - [ ] Every protected endpoint requires authentication
  - [ ] Role-based access control (RBAC) implemented
  - [ ] Resource ownership verified (user can only access their data)
  - [ ] No authorization bypass via parameter manipulation
  ```python
  # ✅ GOOD: Verify ownership
  @app.get("/api/v1/candidates/{candidate_id}")
  async def get_candidate(
      candidate_id: str,
      current_user: str = Depends(get_current_user)
  ):
      candidate = candidates_db.get(candidate_id)
      if not candidate:
          raise HTTPException(404)
      
      # Verify user owns this resource or is admin
      if candidate["user_id"] != current_user and not is_admin(current_user):
          raise HTTPException(403, "Forbidden")
      
      return candidate
  ```

### 🛡️ Input Validation & Injection Prevention

- [ ] **No SQL Injection** (if using SQL)
  - [ ] Parameterized queries used (no string concatenation)
  - [ ] ORM used correctly (SQLAlchemy, Tortoise ORM)
  - [ ] Raw SQL properly escaped
  ```python
  # ❌ BAD
  query = f"SELECT * FROM users WHERE email = '{email}'"
  
  # ✅ GOOD
  query = "SELECT * FROM users WHERE email = :email"
  result = await database.fetch_one(query, values={"email": email})
  ```

- [ ] **No Command Injection**
  - [ ] No `os.system()`, `subprocess.run(shell=True)` with user input
  - [ ] Shell commands sanitized
  - [ ] Use subprocess safely
  ```python
  # ❌ BAD
  os.system(f"convert {user_file} output.png")
  
  # ✅ GOOD
  import subprocess
  subprocess.run(["convert", user_file, "output.png"], check=True)
  ```

- [ ] **Pydantic Validation on ALL Inputs**
  - [ ] No `dict` payloads (use Pydantic models)
  - [ ] Enums used for known values (not loose strings)
  - [ ] Email validation with `EmailStr`
  - [ ] URL validation with `HttpUrl`
  - [ ] Length limits on all string fields
  ```python
  # ❌ BAD
  @app.post("/api/v1/users")
  async def create_user(payload: dict = Body(...)):
      ...
  
  # ✅ GOOD
  class UserCreate(BaseModel):
      email: EmailStr
      status: UserStatus  # Enum, not str
      name: str = Field(..., min_length=1, max_length=100)
  
  @app.post("/api/v1/users")
  async def create_user(payload: UserCreate):
      ...
  ```

- [ ] **File Upload Security**
  - [ ] File size limits enforced
  - [ ] File type validation (whitelist, not blacklist)
  - [ ] Filename sanitization (no path traversal)
  - [ ] Virus scanning on uploads
  - [ ] Files stored outside web root
  ```python
  ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
  MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
  
  async def validate_upload(file: UploadFile):
      # Check extension
      ext = os.path.splitext(file.filename)[1].lower()
      if ext not in ALLOWED_EXTENSIONS:
          raise HTTPException(400, "Invalid file type")
      
      # Check size
      contents = await file.read()
      if len(contents) > MAX_FILE_SIZE:
          raise HTTPException(400, "File too large")
      
      # Sanitize filename
      safe_filename = secure_filename(file.filename)
      return safe_filename, contents
  ```

### 🌐 API Security

- [ ] **CORS Configuration**
  - [ ] CORS whitelist configured (not wildcard `*` in production)
  - [ ] Credentials allowed only for specific origins
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  
  # ❌ BAD (production)
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True
  )
  
  # ✅ GOOD
  ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
  app.add_middleware(
      CORSMiddleware,
      allow_origins=ALLOWED_ORIGINS,
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE"],
      allow_headers=["Authorization", "Content-Type"]
  )
  ```

- [ ] **Rate Limiting**
  - [ ] Rate limits on authentication endpoints
  - [ ] Rate limits on expensive operations
  - [ ] Per-IP and per-user limits
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  
  @app.post("/api/v1/auth/login")
  @limiter.limit("5/minute")
  async def login(request: Request, ...):
      ...
  ```

- [ ] **HTTPS Enforced**
  - [ ] Redirect HTTP to HTTPS
  - [ ] HSTS header set
  - [ ] Secure cookies (Secure, HttpOnly, SameSite)
  ```python
  from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
  
  if os.getenv("ENVIRONMENT") == "production":
      app.add_middleware(HTTPSRedirectMiddleware)
  ```

- [ ] **Security Headers**
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] Content-Security-Policy configured
  - [ ] Strict-Transport-Security (HSTS)
  ```python
  from fastapi.middleware.trustedhost import TrustedHostMiddleware
  
  @app.middleware("http")
  async def add_security_headers(request: Request, call_next):
      response = await call_next(request)
      response.headers["X-Content-Type-Options"] = "nosniff"
      response.headers["X-Frame-Options"] = "DENY"
      response.headers["X-XSS-Protection"] = "1; mode=block"
      response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
      return response
  ```

### 🔒 Data Protection

- [ ] **Sensitive Data Handling**
  - [ ] PII (Personally Identifiable Information) encrypted at rest
  - [ ] Sensitive fields not logged
  - [ ] Secure random generation (secrets module, not random)
  - [ ] Credentials not in error messages/stack traces
  ```python
  # ❌ BAD
  import random
  token = random.randint(100000, 999999)
  
  # ✅ GOOD
  import secrets
  token = secrets.randbelow(900000) + 100000
  ```

- [ ] **Logging Security**
  - [ ] No passwords/tokens in logs
  - [ ] Sanitize user input before logging
  - [ ] Log retention policy
  - [ ] Audit trail for sensitive operations
  ```python
  # ❌ BAD
  logger.info(f"Login attempt: {email} with password {password}")
  
  # ✅ GOOD
  logger.info(f"Login attempt: {email}")
  if login_failed:
      logger.warning(f"Failed login for {email} from {ip_address}")
  ```

- [ ] **Dependency Security**
  - [ ] All dependencies up to date
  - [ ] No known CVEs in dependencies
  - [ ] Minimal dependency tree
  - [ ] Dependencies pinned to specific versions
  ```bash
  # Check vulnerabilities
  pip-audit
  safety check
  
  # Update dependencies
  pip list --outdated
  pip install --upgrade <package>
  ```

### 🚨 Error Handling & Information Disclosure

- [ ] **No Information Leakage**
  - [ ] Generic error messages to users
  - [ ] Detailed errors only in logs (not responses)
  - [ ] Debug mode disabled in production
  - [ ] Stack traces not exposed
  ```python
  # ❌ BAD
  @app.exception_handler(Exception)
  async def generic_exception_handler(request, exc):
      return JSONResponse(
          status_code=500,
          content={"error": str(exc), "traceback": traceback.format_exc()}
      )
  
  # ✅ GOOD
  @app.exception_handler(Exception)
  async def generic_exception_handler(request, exc):
      logger.error(f"Unhandled exception: {exc}", exc_info=True)
      return JSONResponse(
          status_code=500,
          content={"error": "Internal server error"}
      )
  ```

- [ ] **Resource Limits**
  - [ ] Request size limits
  - [ ] Timeout on long-running operations
  - [ ] Connection limits
  - [ ] Memory/CPU monitoring

---

## Type Safety & Validation Checklist

### ✅ Pydantic Model Quality

- [ ] **No Loose String Validation** (Issue identified in your audit)
  ```bash
  # Find loose string fields
  rg 'str.*Field\(.*min_length.*max_length' services/
  
  # Should use Enums instead:
  rg 'status.*str|type.*str|kind.*str|level.*str' services/ --type py
  ```

- [ ] **All Models Have:**
  - [ ] Field descriptions via `Field(..., description="...")`
  - [ ] Examples in `Config.json_schema_extra`
  - [ ] Proper validation (min/max, patterns, custom validators)
  - [ ] Enums for known value sets
  ```python
  class ApplicationUpdate(BaseModel):
      """Schema for updating an application"""
      status: ApplicationStatus = Field(
          ..., 
          description="Application status must be one of: applied, reviewing, interview_scheduled, accepted, rejected"
      )
      
      class Config:
          json_schema_extra = {
              "example": {
                  "status": "interview_scheduled"
              }
          }
  ```

- [ ] **Email Fields Use EmailStr**
  ```python
  from pydantic import EmailStr
  
  email: EmailStr  # Not str with pattern validation
  ```

- [ ] **Phone Fields Validated**
  ```python
  phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
  ```

- [ ] **URLs Validated**
  ```python
  from pydantic import HttpUrl
  
  website: HttpUrl  # Not str
  ```

### 🎯 Endpoint Type Safety

- [ ] **All Endpoints Have:**
  - [ ] `response_model` specified
  - [ ] `status_code` specified
  - [ ] `tags` for organization
  - [ ] `summary` and `description`
  - [ ] `responses` dict with error codes
  ```python
  @app.post(
      "/api/v1/users",
      response_model=UserResponse,
      status_code=201,
      tags=["users"],
      summary="Create a new user",
      description="Creates a new user account with email verification",
      responses={
          201: {"description": "User created successfully"},
          400: {"description": "Invalid input"},
          409: {"description": "Email already exists"}
      }
  )
  async def create_user(payload: UserCreate):
      ...
  ```

- [ ] **No Generic Dict Payloads**
  ```bash
  # Find all dict payloads
  rg 'payload.*dict.*Body' services/
  rg 'data.*dict.*Body' services/
  
  # Replace with Pydantic models
  ```

---

## API Security Checklist

### 🔑 Authentication Endpoints

- [ ] **/auth/login**
  - [ ] Rate limited (5-10 requests/minute)
  - [ ] Account lockout after failed attempts
  - [ ] Credentials never logged
  - [ ] Returns generic error (don't reveal if email exists)

- [ ] **/auth/register**
  - [ ] Email verification required
  - [ ] Password complexity enforced
  - [ ] CAPTCHA on registration
  - [ ] Rate limited

- [ ] **/auth/reset-password**
  - [ ] Token expires (15-30 minutes)
  - [ ] One-time use tokens
  - [ ] Rate limited
  - [ ] Email notification on reset

- [ ] **/auth/logout**
  - [ ] Token blacklisted
  - [ ] All sessions terminated

### 🔒 Protected Endpoints

- [ ] **Authorization Check Pattern**
  ```python
  async def require_role(required_role: str):
      def dependency(current_user: str = Depends(get_current_user)):
          user = users_db.get(current_user)
          if not user or required_role not in user.get("roles", []):
              raise HTTPException(403, "Insufficient permissions")
          return current_user
      return dependency
  
  @app.delete("/api/v1/users/{user_id}")
  async def delete_user(
      user_id: str,
      current_user: str = Depends(require_role("admin"))
  ):
      ...
  ```

- [ ] **Input Sanitization**
  - [ ] SQL queries parameterized
  - [ ] HTML/JavaScript escaped
  - [ ] File paths sanitized
  - [ ] Command injection prevented

---

## Code Quality Checklist

### 📊 Complexity Metrics

- [ ] **Function Complexity**
  ```bash
  # Install radon
  pip install radon
  
  # Check cyclomatic complexity
  radon cc services/ -a -nb
  
  # Check maintainability index
  radon mi services/ -nb
  
  # Target: CC < 10, MI > 20
  ```

- [ ] **Code Duplication**
  ```bash
  # Install
  pip install pylint
  
  # Check duplication
  pylint services/ --disable=all --enable=duplicate-code
  ```

### 🧪 Test Coverage

- [ ] **Minimum 80% Coverage**
  ```bash
  # Run with coverage
  pytest --cov=services --cov-report=html --cov-report=term
  
  # Check coverage
  coverage report --fail-under=80
  ```

- [ ] **Security Tests**
  - [ ] Authentication bypass tests
  - [ ] Authorization tests (access control)
  - [ ] Input validation tests (injection, XSS)
  - [ ] Rate limiting tests
  - [ ] Session management tests

### 📝 Documentation

- [ ] **API Documentation**
  - [ ] OpenAPI schema complete
  - [ ] All endpoints documented
  - [ ] Examples provided
  - [ ] Error codes documented

- [ ] **Code Documentation**
  - [ ] Module docstrings
  - [ ] Class docstrings
  - [ ] Function docstrings (Google/Numpy style)
  - [ ] Complex logic commented

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/security-checks.yml
name: Security & Quality Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install bandit safety ruff mypy pytest pytest-cov
      
      - name: Security scan with Bandit
        run: bandit -r services/ -f json -o bandit-report.json
        continue-on-error: true
      
      - name: Dependency vulnerability check
        run: safety check --json
        continue-on-error: true
      
      - name: Linting with Ruff
        run: ruff check services/
      
      - name: Type checking with MyPy
        run: mypy services/ --strict
        continue-on-error: true
      
      - name: Run tests with coverage
        run: pytest --cov=services --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
      
      - name: Semgrep security scan
        run: |
          pip install semgrep
          semgrep --config=auto --json -o semgrep-report.json services/
        continue-on-error: true
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            semgrep-report.json
```

---

## Pre-Commit Hooks

### Setup Pre-Commit

```bash
# Install
pip install pre-commit

# Create .pre-commit-config.yaml
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]

  - repo: https://github.com/returntocorp/semgrep
    rev: v1.52.0
    hooks:
      - id: semgrep
        args: ['--config', 'auto', '--error']
```

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Quick Start Commands

### Daily Security Check
```bash
#!/bin/bash
# scripts/security-check.sh

echo "=== Running Security Checks ==="

echo "1. Scanning for hardcoded secrets..."
trivy fs --scanners secret .

echo "2. Checking dependencies for vulnerabilities..."
safety check

echo "3. Running Bandit security linter..."
bandit -r services/ -ll

echo "4. Running Semgrep security rules..."
semgrep --config=auto services/

echo "5. Type checking with MyPy..."
mypy services/ --strict

echo "6. Linting with Ruff..."
ruff check services/

echo "7. Running tests..."
pytest --cov=services --cov-fail-under=80

echo "=== Security Check Complete ==="
```

### Make it executable
```bash
chmod +x scripts/security-check.sh
./scripts/security-check.sh
```

---

## Priority Actions (Immediate)

### 🔴 Critical (Fix Now)

1. **[ ] Replace Hardcoded Secrets**
   ```bash
   # Find all hardcoded secrets
   bandit -r services/ -f json | jq '.results[] | select(.issue_text | contains("hardcoded"))'
   trivy fs --scanners secret services/
   ```

2. **[ ] Fix Loose Enum Validation** (Already identified)
   - Candidate Service: ✅ Done
   - Security Service: Roles/Permissions
   - User Service: Status fields
   - Notification Service: Notification types

3. **[ ] Add Input Validation**
   - Replace all `dict` payloads with Pydantic models
   - Add field constraints (min/max length, patterns)
   - Use EmailStr for emails, HttpUrl for URLs

4. **[ ] Implement Rate Limiting**
   - On /auth/login endpoint
   - On /auth/register endpoint
   - On expensive operations

### 🟡 High Priority (This Sprint)

5. **[ ] Password Hashing**
   - Replace SHA256 with bcrypt/argon2
   - Add password complexity requirements

6. **[ ] JWT Security**
   - Move secret to environment variable
   - Implement token blacklist
   - Add token expiration

7. **[ ] CORS Configuration**
   - Whitelist specific origins
   - Remove wildcard in production

8. **[ ] Add Security Headers**
   - X-Content-Type-Options
   - X-Frame-Options
   - HSTS
   - CSP

### 🟢 Medium Priority (Next Sprint)

9. **[ ] Comprehensive Tests**
   - Security tests for all endpoints
   - 80%+ code coverage
   - Integration tests

10. **[ ] CI/CD Pipeline**
    - GitHub Actions with security checks
    - Pre-commit hooks
    - Automated testing

11. **[ ] Monitoring & Logging**
    - Structured logging
    - Security event monitoring
    - Error tracking (Sentry)

---

## Configuration Files

### Create `pyproject.toml`
```toml
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv", ".venv-1"]
skips = ["B101"]  # Allow assert in tests

[tool.ruff]
line-length = 100
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "S",   # flake8-bandit (security)
    "T20", # flake8-print
    "SIM", # flake8-simplify
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["services"]
python_files = ["test_*.py"]
addopts = "-v --cov=services --cov-report=term-missing"

[tool.coverage.run]
source = ["services"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

---

## Semgrep Custom Rules

### Create `.semgrep/rules.yaml`
```yaml
rules:
  - id: loose-string-enum-validation
    pattern: |
      status: str = Field($ARGS)
    message: "Use Python Enum instead of loose string validation for status/enum fields"
    severity: WARNING
    languages: [python]
    
  - id: hardcoded-jwt-secret
    pattern: |
      SECRET_KEY = "$VALUE"
    message: "JWT secret key should be in environment variable, not hardcoded"
    severity: ERROR
    languages: [python]
    
  - id: dict-payload
    pattern: |
      async def $FUNC($ARGS, payload: dict = Body(...)):
        ...
    message: "Use Pydantic models instead of dict for payload validation"
    severity: WARNING
    languages: [python]
    
  - id: sha256-password-hashing
    pattern: |
      sha256($PASSWORD.encode())
    message: "SHA256 is not suitable for password hashing. Use bcrypt or argon2"
    severity: ERROR
    languages: [python]
```

---

## Summary Checklist

### Before Each Commit
- [ ] `ruff check --fix services/` - Linting
- [ ] `black services/` - Formatting
- [ ] `mypy services/` - Type checking
- [ ] `pytest` - Tests pass
- [ ] No secrets in code

### Before Each PR
- [ ] `bandit -r services/` - Security scan
- [ ] `safety check` - Dependency check
- [ ] `pytest --cov=services --cov-fail-under=80` - Coverage check
- [ ] All enums properly defined (no loose strings)
- [ ] All payloads use Pydantic models

### Weekly Security Audit
- [ ] `semgrep --config=auto services/` - Pattern scan
- [ ] `trivy fs .` - Full filesystem scan
- [ ] Review authentication/authorization logic
- [ ] Update dependencies
- [ ] Review logs for security events

---

## Tools Installation

```bash
# Create requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
# Linting & Formatting
ruff>=0.1.8
black>=23.12.0
isort>=5.13.0

# Type Checking
mypy>=1.7.1
types-all>=1.0.0

# Security
bandit[toml]>=1.7.5
safety>=3.0.0
semgrep>=1.52.0
pip-audit>=2.6.1

# Testing
pytest>=7.4.3
pytest-cov>=4.1.0
pytest-asyncio>=0.21.1
httpx>=0.25.2

# Pre-commit
pre-commit>=3.6.0

# Complexity
radon>=6.0.1
EOF

# Install all dev tools
pip install -r requirements-dev.txt
```

---

**Last Updated:** 2025-12-14  
**Status:** ✅ Ready for Implementation  
**Priority:** 🔴 Critical - Begin with hardcoded secrets, loose enum validation, and input validation

