# OpenTalent Security Policy

**Last Updated:** December 5, 2025
**Version:** 1.0

## Security Scanning Requirements

All code commits to OpenTalent must pass the following security standards:

### 1. Secret Detection (ggshield)

**Status:** ✅ Mandatory (Pre-commit hook)

No API keys, passwords, tokens, or sensitive credentials can be committed.

**Blocked patterns:**

- API keys (OpenAI, AWS, Azure, etc.)
- Database credentials
- Private encryption keys
- Authentication tokens
- OAuth secrets
- Database connection strings

**If a secret is detected:**

1. Pre-commit hook will reject the commit
2. Remove the secret from code
3. Use environment variables instead
4. Recommit

### 2. Security Issues (bandit)

**Status:** ✅ Mandatory (Pre-commit hook)

All medium-severity and above security issues must be fixed before commit.

**Common issues detected:**

- Hardcoded secrets
- Use of insecure functions (pickle, exec, eval)
- SQL injection risks
- Insecure randomness
- Insecure file permissions
- Missing input validation

**Fix issues:**

```bash
bandit -r . -ll  # Show issues
# Fix code, then rerun
bandit -r . -ll  # Verify fixed
```

### 3. Dependency Vulnerabilities (safety)

**Status:** ✅ Mandatory (Regular scans)

All dependencies must be checked for known vulnerabilities.

```bash
# Run before deployment
safety check -r requirements.txt
safety check -r requirements-dev.txt
```

**Response time:**

- Critical (CVSS 9+): Fix within 24 hours
- High (CVSS 7-8.9): Fix within 1 week
- Medium (CVSS 4-6.9): Fix within 2 weeks
- Low (CVSS <4): Fix in next release

### 4. Code Quality (ruff, black, mypy)

**Status:** ✅ Mandatory (Pre-commit hook)

Code must follow consistent formatting and quality standards.

**Checks:**

- PEP 8 style compliance (ruff)
- Code formatting consistency (black)
- Type safety (mypy)
- Import organization (isort)

## Environment Variables

### Required .env Variables

Never commit `.env` files. Use `.env.example` template instead.

```bash
# .env.example (OK to commit)
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@host/db
SENTRY_DSN=your_sentry_dsn

# .env (NEVER commit)
OPENAI_API_KEY=sk-1234567890abcdef
DATABASE_URL=postgresql://admin:SuperSecret123@prod.db.example.com/OpenTalent
SENTRY_DSN=https://key@sentry.io/project
```

### Variable Categories

**Never commit:**

- API keys and tokens
- Database credentials
- Private keys and certificates
- OAuth secrets
- AWS/GCP/Azure credentials
- JWT signing keys
- Payment processor keys (Stripe, etc.)

**Safe to commit:**

- Application configuration
- Feature flags
- Logging levels
- Feature defaults
- Documentation examples

## Git Practices

### Branch Protection

- All branches require passing security checks before merge
- No direct commits to `main` branch
- Pull requests require approval
- Branches must be up-to-date with main

### Commit Messages

Use conventional commit format:

```
type: subject

body

Closes #123
```

**Types:**

- `fix:` - Bug fix
- `feat:` - New feature
- `security:` - Security fix
- `chore:` - Maintenance
- `docs:` - Documentation

### Example

```
security: rotate API keys and update environment configuration

- Remove hardcoded keys from avatar-service
- Update .env.example with placeholder values
- Document required environment variables in README

Closes #156
```

## Deployment Security

### Before Deployment

```bash
# 1. Run full security scan
ggshield secret scan repo .

# 2. Check dependencies
safety check -r requirements.txt

# 3. Run bandit
bandit -r . -ll

# 4. Type check
mypy .

# 5. Run tests
pytest tests/ --cov=src

# 6. Verify environment
# - Confirm .env is NOT included in build
# - Verify environment variables are set
# - Check deployment credentials
```

### Secrets Rotation Schedule

| Type | Frequency | Last Rotated |
|------|-----------|--------------|
| API Keys | Every 3 months | Ongoing |
| Database Passwords | Every 6 months | - |
| JWT Signing Keys | Every 6 months | - |
| OAuth Tokens | Every 3 months | - |
| SSH Keys | Every 12 months | - |

## Third-Party Integrations

All third-party services must be vetted for security:

✅ **Approved:**

- OpenAI (GPT models)
- Hugging Face (model hub)
- AWS (infrastructure)
- Google Cloud (infrastructure)
- Sentry (error tracking)
- GitHub (version control)

### Adding New Integration

Submit security review:

1. Service documentation
2. Security practices
3. Data handling procedures
4. Compliance certifications
5. Review approval required

## Incident Response

### If a Secret is Exposed

1. **Immediately revoke** the compromised credential
2. **Create new** credential with different value
3. **Update environment** variables across all systems
4. **Audit logs** for unauthorized access
5. **Notify team** in security channel
6. **Document incident** with timeline and resolution

### If Vulnerability is Found

1. **Assess severity** (Critical/High/Medium/Low)
2. **Create security issue** (private GitHub issue)
3. **Develop fix** on security branch
4. **Test thoroughly** including regression tests
5. **Deploy patch** to production
6. **Document resolution** in release notes

## Compliance

OpenTalent follows:

- ✅ **OWASP Top 10** - Web application security
- ✅ **SANS Top 25** - Most dangerous software weaknesses
- ✅ **PEP 8** - Python style guide
- ✅ **CWE Standards** - Common weakness enumeration
- ✅ **GDPR** - Data protection (for EU users)

## Code Review Security Checklist

When reviewing pull requests, check:

- [ ] No hardcoded secrets or credentials
- [ ] No SQL injection risks
- [ ] Input validation present
- [ ] Type hints are used
- [ ] Error handling is appropriate
- [ ] Logging doesn't expose sensitive data
- [ ] Dependencies are reviewed
- [ ] Tests have adequate coverage

## Tools & Monitoring

### Automated Security Scanning

| Tool | Purpose | Frequency |
|------|---------|-----------|
| ggshield | Secret detection | Every commit |
| bandit | Security issues | Every commit |
| safety | Dependency vulnerabilities | Daily |
| Ruff | Code quality | Every commit |
| mypy | Type safety | Every commit |

### Continuous Monitoring

- GitHub security alerts for dependencies
- Sentry for runtime error tracking
- GitGuardian for secret detection
- Regular penetration testing (quarterly)

## Support & Reporting

### Security Questions?

Email: <security@opentalent.ai>
Or create a private security issue on GitHub

### Report a Vulnerability?

Do NOT create public GitHub issues for security vulnerabilities.

**Submit to:**

1. <security@opentalent.ai> with details
2. Or create private GitHub security advisory
3. Include reproduction steps and potential impact

### Expected Response Time

- **Acknowledgment:** 24 hours
- **Initial Assessment:** 48 hours
- **Fix Released:** Based on severity (24h-30 days)

## Acknowledgments

Security policy inspired by:

- OWASP Application Security Verification Standard (ASVS)
- GitGuardian best practices
- Industry security standards

---

**Questions?** See [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) for detailed setup instructions.
