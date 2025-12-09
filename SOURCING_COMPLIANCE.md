# Proactive Scanning Agent - Compliance & Legal Framework

**Document Version:** 1.0  
**Last Updated:** December 9, 2025  
**Classification:** Legal & Compliance  
**Scope:** Candidate sourcing compliance standards

---

## Executive Summary

The **Proactive Scanning Agent (Port 8091)** has been redesigned to prioritize **legal compliance** in all candidate sourcing activities. This document outlines:

1. ✅ **5-Tier Sourcing Method Hierarchy** (prioritized by legal compliance)
2. ✅ **Consent Tracking & Management** (GDPR, CCPA compliant)
3. ✅ **Data Protection Standards** (retention, deletion, privacy)
4. ✅ **Platform-Specific Compliance** (LinkedIn, GitHub, Stack Overflow)
5. ✅ **Audit & Logging Framework** (full compliance trail)

---

## 🏛️ Sourcing Method Hierarchy (Priority Order)

### **TIER 1: OFFICIAL APIs** ⭐ HIGHEST COMPLIANCE

**Method:** `official_api`  
**Risk Level:** ✅ MINIMAL  
**Legal Status:** ✅ FULLY COMPLIANT  

#### LinkedIn Recruiter API (OAuth2)
```
Authentication: LinkedIn OAuth2 + Recruiter API key
Endpoint: https://api.linkedin.com/v2/search/jobs or /search/people
Authorization: Bearer token (from environment: LINKEDIN_API_TOKEN)
Rate Limit: 5,000 requests/day
Terms of Service: Explicitly allows recruiter use
Compliance: GDPR, CCPA, Platform TOS verified
```

**What you can do:**
- Search for candidates using boolean queries
- Filter by: location, title, skills, experience, industry
- Only contact candidates with "Open to Recruiter Contact" enabled
- Respect recruitment notification settings
- Track engagement with message delivery

**What you CANNOT do:**
- Contact users with private profiles
- Use scraping tools or automation that violates TOS
- Bypass rate limits
- Store candidate data longer than agreed terms

**Compliance Verification:**
- ✅ Explicit API authorization required
- ✅ OAuth2 token management
- ✅ Rate limiting enforced
- ✅ Audit trail: all API calls logged
- ✅ Consent verification: "Open to Contact" flag required

---

#### GitHub REST API v3 (OAuth2)
```
Authentication: GitHub OAuth2 token
Endpoint: https://api.github.com/search/users
Rate Limit: 30 requests/minute (authenticated), 10 requests/minute (unauthenticated)
Scope: public:repo, user:email (optional)
Terms of Service: Allows research and sourcing from public profiles
Compliance: GDPR, CCPA, Terms verified
```

**What you can do:**
- Search public GitHub profiles by: username, language, repositories, followers
- Retrieve public profile data (name, bio, email if public)
- View public repository contributions and activity
- Contact via publicly listed email or social profiles

**What you CANNOT do:**
- Access private repositories or private emails
- Violate GitHub Terms of Service
- Automated scraping beyond API rate limits
- Store private data without explicit consent

**Compliance Verification:**
- ✅ GitHub OAuth2 token authentication
- ✅ Only public profile data accessed
- ✅ Rate limit compliance (30 req/min)
- ✅ Privacy settings respected
- ✅ Contact info must be publicly visible

---

#### Stack Overflow Public API
```
Authentication: No authentication required (public API)
Endpoint: https://api.stackexchange.com/2.3/users
Rate Limit: 10,000 requests/day per IP
Filter: users.filter=...)related_users;withbadges
Terms of Service: Allows research and talent sourcing
Compliance: GDPR, CCPA verified
```

**What you can do:**
- Search users with "Looking for work" flag explicitly set
- Filter by: reputation, expertise tags, location, activity
- Retrieve public profile information
- View Stack Overflow Jobs profile if available

**What you CANNOT do:**
- Contact users without "Looking for work" flag
- Violate Stack Overflow Terms
- Store more data than specified in license
- Exceed API rate limits

**Compliance Verification:**
- ✅ API rate limits enforced (10K/day)
- ✅ "Looking for work" flag required
- ✅ Public data only
- ✅ Compliance audit trail

---

### **TIER 2: AUTHORIZED PARTNERS** ⭐⭐ HIGH COMPLIANCE

**Method:** `authorized_partner`  
**Risk Level:** ✅ LOW  
**Legal Status:** ✅ COMPLIANT  

Examples:
- LinkedIn Premium API partners (HubSpot, Workable, Greenhouse)
- GitHub integration partners (recommended by GitHub)
- Approved ATS integrations

**Requirements:**
- Partner has signed Data Processing Agreement (DPA)
- GDPR-compliant data handling verified
- Regular security audits
- Compliance certification (SOC2, ISO 27001)

---

### **TIER 3: OPT-IN DIRECTORIES** ⭐⭐ HIGH COMPLIANCE

**Method:** `opt_in_directory`  
**Risk Level:** ✅ LOW  
**Legal Status:** ✅ FULLY COMPLIANT  

**Platforms:**
- Stack Overflow Jobs (candidates explicitly looking for work)
- Angel List (founder network with opt-in job search)
- Dev.to (public developer profiles)
- Kaggle (public data science profiles)
- Product Hunt (startup founders)

**Why Compliant:**
- ✅ Users explicitly chose to be listed
- ✅ Consent is unambiguous
- ✅ Users actively seeking opportunities
- ✅ Platforms enforce TOS compliance
- ✅ Data retention policies clear

**Example: Stack Overflow "Looking for Work"**
```
User explicitly sets flag: "Open to Work"
This means: "Yes, recruiters may contact me"
Consent type: EXPLICIT_OPT_IN
Contact method: Direct message or email (if public)
Data retention: 2 years (aligned with GDPR)
```

---

### **TIER 4: PUBLIC PROFILES** ⭐⭐ MEDIUM COMPLIANCE

**Method:** `public_profile`  
**Risk Level:** ⚠️ MEDIUM  
**Legal Status:** ✅ COMPLIANT (WITH CONSENT TRACKING)  

**Platforms:**
- GitHub public profiles
- Public portfolio websites
- LinkedIn public profiles (basic info only)
- Twitter/X professional accounts

**Compliance Requirements:**
- ✅ Profile must be public (not private)
- ✅ Consent tracking required (document how accessed)
- ✅ Contact info must be publicly visible
- ✅ Must honor "do not contact" indicators
- ✅ Reasonable contact frequency (no spam)

**Example: GitHub Public Profile**
```
Access: GitHub public API → public profile data
Profile visibility: PUBLIC
Contact info available: Email/website in bio
Consent basis: Public profile = implicit consent to discovery
Data retention: 1 year
Retention policy: Delete after 1 year if not contacted
```

---

### **TIER 5: INTERNAL REFERRALS** ⭐⭐ HIGH COMPLIANCE

**Method:** `internal_referral`  
**Risk Level:** ✅ LOW  
**Legal Status:** ✅ FULLY COMPLIANT  

**Sources:**
- Employee referral programs
- Alumni networks
- Internal talent pools
- Company Slack/Teams channels (with permission)

**Compliance:**
- ✅ Consent already implied (internal network)
- ✅ Data governance clear
- ✅ Privacy policies apply
- ✅ Easy opt-out mechanism

---

## 📋 Consent Types & Management

### Four Consent Models

#### 1. EXPLICIT_OPT_IN ✅ HIGHEST COMPLIANCE
```python
ConsentType.EXPLICIT_OPT_IN
```

**Definition:** User actively chose to allow sourcing/contact  
**Examples:**
- LinkedIn: "Open to recruiter contact" flag enabled
- Stack Overflow: "Looking for work" explicitly set
- Email signup: "Yes, contact me about opportunities"
- Website form: Submitted "Get hired" form

**GDPR Compliance:** ✅ FULLY COMPLIANT  
**Data Retention:** 730 days (2 years)  
**Contact Methods:** All channels allowed (email, LinkedIn, phone)  

**Required Documentation:**
```python
ComplianceRecord(
    candidate_id="candidate_123",
    platform="linkedin",
    sourcing_method=SourcingMethod.OFFICIAL_API,
    consent_type=ConsentType.EXPLICIT_OPT_IN,
    consent_date=datetime(2025, 12, 9),
    opt_in_url="https://linkedin.com/in/candidate",
    terms_accepted=True,
    data_retention_days=730
)
```

---

#### 2. IMPLIED_CONSENT ⚠️ MEDIUM COMPLIANCE
```python
ConsentType.IMPLIED_CONSENT
```

**Definition:** User hasn't explicitly opted out, but no explicit opt-in  
**Examples:**
- Public GitHub profile (profile visibility indicates interest)
- Public LinkedIn profile (participation indicates openness)
- Published portfolio website

**GDPR Compliance:** ⚠️ CONDITIONAL (requires clear privacy notice)  
**Data Retention:** 365 days (1 year)  
**Contact Methods:** Primary channels only (email from profile, LinkedIn)  

**Requirements:**
- Must include clear opt-out option
- Must honor "do not contact" requests
- Must provide privacy notice upfront
- Must be reasonable in contact frequency

---

#### 3. THIRD_PARTY_REFERRAL ✅ HIGH COMPLIANCE
```python
ConsentType.THIRD_PARTY_REFERRAL
```

**Definition:** Candidate referred by another person/entity  
**Examples:**
- Employee referral
- Recruiter referral
- LinkedIn mutual connection referral
- Alumni network referral

**GDPR Compliance:** ✅ COMPLIANT (with proper disclosure)  
**Data Retention:** 730 days (2 years)  
**Contact Methods:** Email referrer first, then candidate  

**Requirements:**
- Must disclose referral source
- Must mention referrer's connection
- Can lead with: "John (your connection) referred you..."

---

#### 4. PUBLIC_POSTING 🔓 VALID BUT CAUTION
```python
ConsentType.PUBLIC_POSTING
```

**Definition:** Candidate publicly posted availability (blog, tweet, etc.)  
**Examples:**
- "Hiring" tweet
- Published resume/CV
- Blog post about job search
- "Looking for opportunities" Instagram story

**GDPR Compliance:** ⚠️ REQUIRES VERIFICATION  
**Data Retention:** 365 days (1 year)  
**Contact Methods:** Public contact method listed in posting  

**Caution:**
- Verify posting date (not old)
- Ensure still actively looking
- Use contact method from posting
- Don't assume ongoing consent

---

## 🔐 Data Protection & Privacy

### Data Retention Policies

| Consent Type | Retention Period | Deletion Method | Auto-Delete |
|--------------|-----------------|----------------|------------|
| EXPLICIT_OPT_IN | 730 days (2 years) | GDPR compliant deletion | ✅ Yes |
| IMPLIED_CONSENT | 365 days (1 year) | Secure purge | ✅ Yes |
| THIRD_PARTY_REFERRAL | 730 days (2 years) | GDPR deletion | ✅ Yes |
| PUBLIC_POSTING | 365 days (1 year) | Secure purge | ✅ Yes |

### Right to Be Forgotten (GDPR Article 17)

**Implementation:**
```python
DELETE /api/candidates/{candidate_id}
```

**Process:**
1. Search for all candidate records
2. Delete from all systems (database, cache, backups)
3. Notify downstream services (scouts, ATS, CRM)
4. Log deletion for audit trail
5. Confirm deletion within 30 days

### Data Access Minimization

**Collect Only:**
- Name
- Current role/title
- Email address (if public)
- Primary skills
- Social profile URL (link only, not full profile)
- Sourcing method/consent type
- Consent date

**Do NOT Collect:**
- Phone numbers (unless publicly provided)
- Home address
- Birthdate/age information
- Family information
- Ethnic background
- Religious beliefs
- Health information
- Salary expectations (unless disclosed)

---

## 📊 Compliance Audit Trail

Every candidate sourced is logged with:

```python
{
    "audit_log": {
        "candidate_id": "linkedin_pipeline_123_0",
        "timestamp": "2025-12-09T10:30:37Z",
        "pipeline_id": "pipeline_project_123_1733740234",
        "platform": "linkedin",
        "sourcing_method": "official_api",
        "consent_type": "explicit_opt_in",
        "data_collected": {
            "name": "John Doe",
            "current_role": "Senior Software Engineer",
            "email": "john.doe@linkedin.com",
            "skills": ["Python", "AWS", "Kubernetes"],
            "profile_url": "https://linkedin.com/in/johndoe"
        },
        "consent_verification": {
            "recruitment_enabled": True,
            "open_to_opportunities": True,
            "source_url": "https://linkedin.com/in/johndoe"
        },
        "compliance_level": "GDPR_COMPLIANT",
        "data_retention_days": 730,
        "retention_expiry": "2027-12-09T10:30:37Z",
        "contact_channels_allowed": ["email", "linkedin_message"],
        "agent": "proactive-scanning",
        "action": "candidate_discovered"
    }
}
```

---

## 🔗 Platform-Specific Guidelines

### LinkedIn (Official API)

**✅ DO:**
- Use LinkedIn Recruiter API with OAuth2
- Search candidates with "Open to Recruiter Contact" enabled
- Send InMail (doesn't bypass user settings)
- Respect messaging limits
- Honor profile privacy settings

**❌ DON'T:**
- Scrape LinkedIn with automation tools
- Use fake accounts
- Contact users with private profiles
- Bypass message request limits
- Store credentials in code
- Cache candidate data longer than 30 days

**Compliance Check:**
```bash
# Verify LinkedIn API key is from official channel
# Check: linkedin.com/developers/apps
# Verify: OAuth2 scopes are minimal
# Rate limit: 5,000 requests/day (enforced by API)
```

---

### GitHub (REST API v3)

**✅ DO:**
- Use GitHub REST API v3 (not GraphQL for scraping)
- Request public profile data only
- Respect `public_repositories` count (activity indicator)
- Check bio/profile for email/contact info
- Honor GitHub TOS (Section 5: Abuse)

**❌ DON'T:**
- Access private repositories
- Use personal access tokens for public data
- Scrape beyond API rate limits
- Store token in code/logs
- Impersonate other users
- Violate GitHub's scraping TOS

**Compliance Check:**
```bash
# Verify OAuth scope: minimal (public_repo only)
# Rate limit: 30 requests/minute
# Check: api.github.com rate limit headers
# Validate: only public profiles accessed
```

---

### Stack Overflow (Public API)

**✅ DO:**
- Use Stack Overflow API (public, no auth needed)
- Filter for "Looking for work" users only
- Respect reputation score threshold (quality filter)
- Check public expertise tags
- Use official contact methods

**❌ DON'T:**
- Scrape beyond API rate limits (10K/day)
- Contact users without "Looking for work" flag
- Use automation to bypass rate limits
- Store more data than license allows
- Violate API attribution requirements

**Compliance Check:**
```bash
# Filter: users.filter contains "looking for work" flag
# Rate limit: 10,000 requests/day per IP
# Check: X-RateLimit headers in response
# Verify: reputation > 1000 (quality tier)
```

---

## 📋 Compliance Endpoints (REST API)

### 1. List Compliance Methods
```bash
GET /compliance/methods
```

**Response:**
```json
{
  "sourcing_methods": [
    {
      "tier": 1,
      "method": "official_api",
      "description": "Official platform APIs (OAuth2, API keys)",
      "compliance_level": "HIGHEST",
      "gdpr_compliant": true,
      "ccpa_compliant": true
    },
    ...
  ]
}
```

---

### 2. Get Compliance Levels
```bash
GET /compliance/levels
```

**Response:**
```json
{
  "compliance_levels": [
    {
      "level": "GDPR_COMPLIANT",
      "region": "European Union",
      "requirements": [
        "Explicit consent required",
        "Right to be forgotten honored",
        ...
      ]
    },
    ...
  ]
}
```

---

### 3. Validate Scanning Request
```bash
POST /compliance/validate
Content-Type: application/json

{
  "pipeline_id": "pipeline_123",
  "job_description": "Senior Python Engineer",
  "sourcing_methods": ["official_api", "opt_in_directory"],
  "require_explicit_consent": true,
  "compliance_level": "GDPR_COMPLIANT"
}
```

**Response:**
```json
{
  "valid": true,
  "sourcing_methods_validated": ["official_api", "opt_in_directory"],
  "compliance_level": "GDPR_COMPLIANT",
  "warnings": [],
  "recommendations": [
    "✅ Using official APIs (tier 1) - HIGHEST compliance",
    "✅ Explicit consent requirement enabled"
  ]
}
```

---

### 4. Start Compliant Scan
```bash
POST /pipelines/start
Content-Type: application/json

{
  "project_id": "project_123",
  "job_description": "Senior Backend Engineer with Python",
  "job_title": "Senior Backend Engineer",
  "target_platforms": ["linkedin", "github"],
  "num_candidates_target": 50,
  "sourcing_methods": ["official_api", "opt_in_directory"],
  "require_explicit_consent": true,
  "compliance_level": "GDPR_COMPLIANT"
}
```

---

## ✅ Compliance Checklist

### Before Starting Any Sourcing:

- [ ] **Legal Review**: Get legal team approval for sourcing strategy
- [ ] **Platform TOS**: Reviewed latest TOS for each platform
- [ ] **API Authorization**: Have OAuth2 credentials/API keys for official APIs
- [ ] **Privacy Policy**: Published privacy policy explaining data collection
- [ ] **Consent Mechanism**: Clear opt-in/opt-out mechanism in place
- [ ] **Data Retention**: Policy established (default: 1-2 years)
- [ ] **Right to Delete**: Process for GDPR "right to be forgotten" requests
- [ ] **Audit Logging**: All sourcing actions logged with compliance metadata
- [ ] **Security**: Credentials stored securely (environment variables, not code)
- [ ] **Training**: Team trained on compliance requirements

### Per Sourcing Campaign:

- [ ] **Method Validated**: Sourcing methods are Tier 1-2 compliant
- [ ] **Consent Verified**: All candidates have explicit or valid consent
- [ ] **Limits Set**: Daily/weekly sourcing limits to avoid spam
- [ ] **Review**: QA review of first 10 candidates before bulk operation
- [ ] **Documentation**: Email/SMS templates reviewed for compliance
- [ ] **Frequency**: Reasonable contact frequency (no more than weekly)
- [ ] **Opt-Out**: Easy unsubscribe/opt-out mechanism provided
- [ ] **Monitoring**: Bounce rates, unsubscribes, spam complaints monitored

### Per Contact Sent:

- [ ] **Consent Verified**: Candidate has valid consent to contact
- [ ] **Contact Info**: Using publicly provided contact method
- [ ] **Personalization**: Message personalized (not mass template)
- [ ] **Opt-Out**: Clear way to unsubscribe
- [ ] **Privacy Notice**: Link to privacy policy included
- [ ] **Identification**: Clear who is sending message (company, recruiter name)

---

## 🚨 Non-Compliance Risks

| Risk | Penalty | Mitigation |
|------|---------|-----------|
| GDPR violation | €20M or 4% revenue | Use Tier 1-2 methods, explicit consent |
| CCPA violation | $2,500-$7,500 per violation | Implement privacy policy, opt-out |
| LinkedIn TOS violation | Account ban | Use official API only |
| GitHub TOS violation | IP ban | Respect rate limits, public data only |
| Spam complaints | Email deliverability issues | Limit frequency, clean list |
| Candidate legal action | Damages, legal fees | Document consent, respect preferences |

---

## 📚 Further Reading

- **GDPR Text**: https://gdpr-info.eu/
- **CCPA Text**: https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201720180AB375
- **LinkedIn TOS**: https://www.linkedin.com/legal/user-agreement
- **GitHub TOS**: https://docs.github.com/site-policy/github-terms
- **Stack Overflow TOS**: https://stackoverflow.com/legal/terms-of-service
- **OWASP Privacy**: https://owasp.org/www-community/Privacy

---

## 📞 Questions or Concerns?

For compliance questions:
1. **Legal Team**: [company-legal@example.com]
2. **Privacy Officer**: [privacy@example.com]
3. **Security Team**: [security@example.com]

This framework ensures OpenTalent operates with **integrity, transparency, and full legal compliance**.

---

**Document Owner:** Legal & Compliance Team  
**Last Review:** December 9, 2025  
**Next Review:** March 9, 2026  
**Version:** 1.0 (Released)
