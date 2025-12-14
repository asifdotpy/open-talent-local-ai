# Security & Code Quality - Quick Start Guide

**TL;DR:** Run `./scripts/security-check.sh` before every commit/PR.

---

## Installation (5 minutes)

```bash
# Install all security & quality tools
pip install -r requirements-dev.txt

# Or install minimum required tools
pip install bandit safety ruff mypy pytest pytest-cov

# Optional but recommended
pip install semgrep trivy

# Set up pre-commit hooks (runs checks automatically)
pre-commit install
```

---

## Daily Workflow

### Before Every Commit

```bash
# Run full security check
./scripts/security-check.sh

# Or run individual checks
ruff check --fix services/      # Auto-fix linting issues
black services/                 # Format code
pytest --cov=services -q        # Run tests with coverage
```

### Pre-Commit Hooks (Automatic)

```bash
# Installed once
pre-commit install

# Now automatically runs on every commit:
# - Security scan (Bandit)
# - Linting (Ruff)
# - Formatting (Black)
# - Secret detection
# - Type checking (MyPy)
```

---

## Critical Security Fixes (Do First)

### 1. Fix Hardcoded Secrets 🔴 CRITICAL

```bash
# Find hardcoded secrets
bandit -r services/ -f json | grep -i "hardcoded"

# Move to environment variables
# Bad:  SECRET_KEY = "my-secret-key"
# Good: SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
```

### 2. Fix Loose Enum Validation 🟡 HIGH

```bash
# Find loose string validation
rg 'status.*str.*Field\(.*min_length.*max_length' services/

# Replace with Enums (see CODE_QUALITY_AUDIT_ENUM_VALIDATION.md)
```

### 3. Replace Dict Payloads 🟡 HIGH

```bash
# Find dict payloads
rg 'payload.*dict.*Body' services/

# Replace with Pydantic models
```

### 4. Fix Password Hashing 🔴 CRITICAL

```bash
# Find insecure hashing
rg 'sha256.*password|md5.*password' services/ -i

# Replace with bcrypt
pip install passlib[bcrypt]
# Use: pwd_context = CryptContext(schemes=["bcrypt"])
```

---

## Quick Command Reference

### Security Scanning

```bash
# Full security scan
./scripts/security-check.sh

# Individual tools
bandit -r services/ -ll                    # High/Medium security issues
safety check                               # Dependency vulnerabilities
semgrep --config=auto services/            # Pattern-based security
trivy fs --scanners secret .               # Secret detection
```

### Code Quality

```bash
# Linting
ruff check services/                       # Check issues
ruff check --fix services/                 # Auto-fix issues

# Formatting
black services/                            # Format code
black --check services/                    # Check without changing

# Type checking
mypy services/ --strict                    # Strict mode
mypy services/ --ignore-missing-imports    # Lenient mode
```

### Testing

```bash
# Run all tests
pytest services/

# With coverage
pytest --cov=services --cov-report=html

# Specific service
pytest services/candidate-service/tests/ -v

# Parallel execution (faster)
pytest -n auto services/
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Tool configuration (Ruff, Black, MyPy, Coverage) |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `.semgrep/rules.yaml` | Custom security rules (15 patterns) |
| `.github/workflows/security-checks.yml` | CI/CD automation |
| `scripts/security-check.sh` | Local security audit script |

---

## CI/CD Integration

### GitHub Actions (Automatic)

Runs on every push/PR:
1. Security scan (Bandit, Semgrep, Trivy)
2. Dependency check (Safety)
3. Code quality (Ruff, Black, MyPy)
4. Tests with coverage (70% minimum)
5. Secret detection (GitGuardian)

**Weekly Security Audit:** Every Monday at 9 AM

---

## Common Issues & Fixes

### Issue: Tests Failing

```bash
# Run with verbose output
pytest services/candidate-service/tests/ -v --tb=short

# Run specific test
pytest services/candidate-service/tests/test_candidate_service.py::test_create_candidate -v
```

### Issue: Linting Errors

```bash
# Auto-fix most issues
ruff check --fix services/

# Format code
black services/

# Check what will change (dry run)
black --check --diff services/
```

### Issue: Type Errors

```bash
# Run MyPy with details
mypy services/candidate-service/main.py --show-error-codes

# Ignore specific errors (use sparingly)
# Add to pyproject.toml:
# [[tool.mypy.overrides]]
# module = "problematic_module"
# ignore_errors = true
```

### Issue: Coverage Too Low

```bash
# See which files need tests
pytest --cov=services --cov-report=term-missing

# Generate HTML report
pytest --cov=services --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Security Checklist (Before Production)

- [ ] No hardcoded secrets (JWT_SECRET, API_KEY, etc.)
- [ ] All enums use Python Enum (not loose strings)
- [ ] All endpoints use Pydantic models (not dict)
- [ ] Password hashing uses bcrypt/argon2 (not SHA256)
- [ ] Rate limiting on auth endpoints
- [ ] CORS whitelist configured (not wildcard *)
- [ ] Security headers added (X-Frame-Options, CSP, etc.)
- [ ] JWT tokens expire and can be revoked
- [ ] All user input validated (Pydantic)
- [ ] SQL queries parameterized (no string concatenation)
- [ ] File uploads validated (size, type, name)
- [ ] HTTPS enforced in production
- [ ] Debug mode disabled in production
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't capture passwords/tokens
- [ ] Dependencies have no known CVEs
- [ ] Tests cover security scenarios
- [ ] Code coverage ≥ 70%

---

## Tool Installation Verification

```bash
# Check which tools are installed
command -v bandit && echo "✓ Bandit" || echo "✗ Bandit"
command -v safety && echo "✓ Safety" || echo "✗ Safety"
command -v semgrep && echo "✓ Semgrep" || echo "✗ Semgrep"
command -v ruff && echo "✓ Ruff" || echo "✗ Ruff"
command -v mypy && echo "✓ MyPy" || echo "✗ MyPy"
command -v pytest && echo "✓ Pytest" || echo "✗ Pytest"
command -v black && echo "✓ Black" || echo "✗ Black"
command -v trivy && echo "✓ Trivy" || echo "✗ Trivy"
```

---

## Priority Actions

| Priority | Task | Estimated Time | Status |
|----------|------|----------------|--------|
| 🔴 Critical | Fix hardcoded JWT secrets | 30 min | ⬜ |
| 🔴 Critical | Replace SHA256 password hashing with bcrypt | 1 hour | ⬜ |
| 🟡 High | Fix loose enum validation in all services | 2-3 hours | ✅ Candidate (Done) |
| 🟡 High | Replace dict payloads with Pydantic models | 2-3 hours | ⬜ |
| 🟡 High | Add rate limiting to auth endpoints | 1 hour | ⬜ |
| 🟢 Medium | Configure CORS whitelist | 30 min | ⬜ |
| 🟢 Medium | Add security headers | 1 hour | ⬜ |
| 🟢 Medium | Implement token blacklist | 1 hour | ⬜ |

---

## Resources

- **Detailed Guide:** [SECURITY_AND_CODE_QUALITY_CHECKLIST.md](SECURITY_AND_CODE_QUALITY_CHECKLIST.md)
- **Enum Fix Guide:** [CODE_QUALITY_AUDIT_ENUM_VALIDATION.md](CODE_QUALITY_AUDIT_ENUM_VALIDATION.md)
- **Security Script:** `./scripts/security-check.sh`
- **Custom Rules:** `.semgrep/rules.yaml`

---

**Last Updated:** December 14, 2025  
**Quick Help:** Run `./scripts/security-check.sh` for instant security audit
