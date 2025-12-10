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

#### LinkedIn Recruiter API - Important Note

⚠️ **Critical Reality Check:**
The official LinkedIn Recruiter API (with scopes like `r_recruiter_search` and `r_prospect_finder`) is **only available to formal LinkedIn partners** (Workday, Greenhouse, Lever, etc.) through enterprise contracts. Individual developers and startups cannot access these scopes through the standard developer program.

**Why the standard flow fails:**
1. Requesting "Talent Solutions" in the developer program requires becoming a formal LinkedIn partner
2. Partner approval is not given to individual developers or small startups
3. Without partner status, your app never receives the necessary sourcing scopes
4. Result: You can only access basic profile info (your own profile), not candidate search

**What Actually Works for Sourcing:**

---

#### **Option 1: Google Custom Search (X-Ray Search) ✅ FREE**

Uses Google Search API to find LinkedIn public profiles matching your criteria.

**Setup:**
```
1. Go to: https://programmablesearchengine.google.com/
2. Create a new search engine
3. Select "Search the entire web"
4. Get your Search Engine ID and API Key
5. Use Google Custom Search JSON API
```

**Example Query:**
```bash
# Find Java developers open to work on LinkedIn
curl "https://www.googleapis.com/customsearch/v1?q=site:linkedin.com/in+java+developer+open+to+work&cx=YOUR_SEARCH_ENGINE_ID&key=YOUR_API_KEY"
```

**Environment Variables:**
```bash
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
GOOGLE_API_KEY=your-api-key
```

**Python Example:**
```python
from googleapiclient.discovery import build
import os

def search_linkedin_profiles(query):
    service = build("customsearch", "v1", 
                   developerKey=os.getenv("GOOGLE_API_KEY"))
    
    results = service.cse().list(
        q=query,
        cx=os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        num=10
    ).execute()
    
    return results['items']

# Usage
profiles = search_linkedin_profiles("java developer london open to work site:linkedin.com/in")
for profile in profiles:
    print(profile['title'], profile['link'])
```

**Advantages:**
- ✅ Free (within Google's quota)
- ✅ No scraping, uses official Google API
- ✅ Only returns public data
- ✅ Compliant with LinkedIn TOS (you're not scraping LinkedIn directly)
- ✅ Legal and sustainable

**Limitations:**
- Results are limited (Google index freshness)
- No structured data (need to parse HTML)

---

#### **Option 2: Commercial Proxy APIs ✅ RECOMMENDED FOR PRODUCTION**

Use vendors that provide aggregated professional data through APIs.

**Important Context:** These vendors don't get data from LinkedIn's official API either. Instead, they:
1. Scrape publicly available data (LinkedIn public profiles, GitHub, Stack Overflow, etc.)
2. Buy data from data brokers (People Data Labs, Coresignal, etc.)
3. Use AI/ML for "identity resolution" (matching same person across platforms)
4. Infer contact data (email pattern matching, third-party databases)
5. Operate in the legal gray area of scraping public data

**The Legal Basis:** The Ninth Circuit ruling in *hiQ Labs v. LinkedIn* (2019) established that scraping publicly available data (not behind login) is legal under US law. However, GDPR restrictions in Europe are much stricter.

**Popular Providers:**
1. **Proxycurl** (https://proxycurl.com/)
   - Aggregated professional data from public sources
   - Search by skills, location, title
   - Contact info (email, phone) from various sources
   - Pricing: $0.01-0.05 per profile lookup
   - Coverage: 800M+ profiles

2. **Nubela Recruitment APIs** (https://www.nubela.co/)
   - Base data from public web + data brokers
   - Candidate search with AI matching
   - Email finding (pattern-based + verified)
   - Pricing: $0.005-0.02 per record
   - Coverage: 500M+ profiles

3. **People Data Labs (PDL)** (https://www.peopledatalabs.com/)
   - The "data broker" layer (wholesale supplier)
   - Sells raw data firehose to other companies
   - 400M+ verified professional records
   - Pricing: Enterprise/bulk contracts

4. **RapidAPI Marketplace** (https://rapidapi.com/)
   - Multiple aggregated data providers
   - Compare sourcing methods and coverage
   - Test before committing

**Setup Example (Proxycurl):**

```bash
# Get API key from https://proxycurl.com/
# Store in environment
PROXYCURL_API_KEY=your-api-key
```

```python
import requests
import os

def search_candidates(skills, location, title):
    """Search candidates using Proxycurl API"""
    
    headers = {
        "Authorization": f"Bearer {os.getenv('PROXYCURL_API_KEY')}"
    }
    
    params = {
        "linkedin_profile_url": None,  # Or use URL if searching specific person
        "extra": "include",
        "github_profile_id": "include",
        "skills": skills,
        "location": location
    }
    
    response = requests.get(
        "https://npi.proxycurl.com/api/v2/linkedin/profile/search",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        candidates = response.json()['results']
        return candidates
    else:
        raise Exception(f"API Error: {response.text}")

# Usage
candidates = search_candidates(
    skills=["Python", "AWS", "Kubernetes"],
    location="San Francisco, CA",
    title="Senior Engineer"
)

for candidate in candidates:
    print(f"{candidate['name']} - {candidate['linkedin_url']}")
```

**Advantages:**
- ✅ Fully compliant (vendor handles compliance)
- ✅ Structured data returned immediately
- ✅ Candidate contact info included
- ✅ Email verification included
- ✅ Scale to thousands of searches
- ✅ No scraping risk
- ✅ Legal and sustainable

**Recommended:** Use Option 2 for production sourcing at scale.

---

**What you CAN do (with proxy API vendors):**
- Search for candidates using filters: skills, location, title, experience
- Get structured candidate data (name, title, location, skills, contact)
- Filter results by: experience level, industry, company, resume keywords
- Retrieve email addresses (verified by vendor)
- Contact candidates with appropriate consent messaging
- Track all sourcing actions in audit log

**What you CANNOT do:**
- Scrape LinkedIn directly (violates TOS)
- Access private/restricted data
- Contact users who haven't opted in
- Store data longer than retention policy allows (1-2 years)
- Use credentials to access LinkedIn on behalf of users

**Compliance Verification:**
- ✅ Using official vendor APIs (Proxycurl, Nubela)
- ✅ Only public LinkedIn data accessed
- ✅ Data minimization (only necessary fields)
- ✅ Audit trail: all searches logged with filters, results, dates
- ✅ Consent tracking: data retention limits enforced
- ✅ Vendor responsible for LinkedIn TOS compliance

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

## � How Data Aggregators Actually Work (Reality Check)

**Understanding the "AI Recruiting" Vendors:**

Companies like Juicebox, SeekOut, HireEZ, and ZoomInfo claim access to 800+ million professional profiles. This is NOT because they have special LinkedIn API access (they don't). Here's how they actually build these databases:

### **Layer 1: The Raw Material (Public Web Scraping)**

**What gets scraped:**
- **LinkedIn public profiles** (profiles set to "public" that appear in Google search)
- **GitHub profiles** (all public - code repos, user profiles, activity)
- **Stack Overflow profiles** (public by default unless disabled)
- **Twitter/X professional accounts** (public tweets, bios)
- **Conference attendee lists** (PDFs and websites)
- **Personal portfolio websites** (public)
- **Professional networks** (Dribbble, Behance, etc.)

**Legal basis (US):** The *hiQ Labs v. LinkedIn* ruling established that scraping publicly available data (not password-protected) doesn't violate the CFAA.

**GDPR issue (EU):** Much stricter. Scraping personal data of EU residents without consent violates GDPR Article 4. This is why many US tools geofence and exclude EU data.

### **Layer 2: Data Broker Supply Chain**

Rather than maintaining scrapers for 800M profiles themselves, companies like Juicebox buy from data brokers:

| Broker | Focus | Scale | Customers |
|--------|-------|-------|-----------|
| **People Data Labs (PDL)** | Professional profiles | 400M+ | Juicebox, SeekOut, others |
| **Coresignal** | Multi-source profiles | 500M+ | Various SaaS platforms |
| **Nubela/Proxycurl** | Public data aggregation | 800M+ | B2B API customers |
| **Apollo/Hunter** | Email finding focus | 100M+ | Sales/recruiting tools |

**The Model:**
```
Data Brokers (scrape & aggregate)
        ↓
Sell bulk data access to...
        ↓
Customer-facing platforms (Juicebox, SeekOut)
        ↓
End users (recruiters, salespeople)
```

### **Layer 3: Identity Resolution (The AI Magic)**

**The Problem:** You have 5 different profiles for "John Smith":
- GitHub: `python developer`, San Francisco
- LinkedIn: `Software Engineer at Google`, San Francisco  
- Twitter: `@john_smith`, SF Bay Area
- Stack Overflow: `Python expert`, California
- Portfolio: `Full-stack engineer`, San Francisco

**The Solution:** Machine learning matches profiles by:
- Location similarity (all say "San Francisco")
- Skill similarity ("Python" appears in all)
- Job title patterns (engineer roles)
- Named entity recognition
- Cross-platform behavior patterns

**Result:** One unified "John Smith" profile with merged attributes from all sources.

### **Layer 4: Contact Data (The Inference)**

LinkedIn doesn't publish personal emails/phones for most users. Vendors infer them:

**Method 1: Email Pattern Matching**
```
Known: "John Smith works at Google"
Known: Google's email format is firstname.lastname@google.com
Inferred: john.smith@google.com
```

**Method 2: Marketing Database Cross-Reference**
```
Professional profile: "John Smith, Google, SF"
Marketing DB: "john.smith@gmail.com, Google employee, SF"
Match: High confidence, add to profile
```

**Method 3: Freemium Extension Crowdsourcing**
```
Browser Extension: "Free Email Finder" 
User installs it to find emails
Plugin reads user's: address book, email signatures, messages
Uploads to central database
Result: Millions of emails collected from users' trusted sources
```

### **Layer 5: The Gray Legal Zone**

| Jurisdiction | Status | Why |
|--------------|--------|-----|
| **US (Federal)** | ✅ Legal (mostly) | *hiQ Labs* ruling: public data scraping allowed |
| **US (California CCPA)** | ⚠️ Conditional | Must provide opt-out; can't discriminate |
| **EU (GDPR)** | ❌ Restricted | Requires explicit consent for personal data |
| **LinkedIn ToS** | ❌ Violation | Explicitly prohibits scraping |

**The Paradox:** 
- Scraping LinkedIn public profiles is technically legal (hiQ ruling)
- But LinkedIn's ToS prohibits it (violation of contract, not law)
- LinkedIn can sue for breach of contract, but not under CFAA

---

### **What This Means for OpenTalent:**

**Option 1: Use Legal Vendor APIs (Recommended)**
```python
# This is what Juicebox does:
# - Buy access to aggregated data from vendors
# - Use vendor's API to search
# - Vendor handles all scraping/legal risks
# - You get compliant data without TOS violation

response = requests.get(
    "https://npi.proxycurl.com/api/v2/linkedin/profile/search",
    headers={"Authorization": f"Bearer {API_KEY}"},
    params={"skills": "Python", "location": "San Francisco"}
)
```

**Advantages:**
- ✅ Vendor liable for data sourcing (not you)
- ✅ Legal indemnification in contract
- ✅ Structured, verified data
- ✅ Compliant contact info
- ✅ Scale-ready infrastructure

**Option 2: Build Your Own Scraper (Not Recommended for Startups)**
```python
# This is what data brokers do:
# - Scrape public profiles 24/7
# - Run identity resolution ML models
# - Maintain infrastructure at scale
# - Handle legal/TOS violations themselves

from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://linkedin.com/in/...")  # ❌ LinkedIn TOS violation
# Extract profile data
# Store in database
# Sell access to other platforms
```

**Disadvantages:**
- ❌ You're liable for TOS violations (not vendor)
- ❌ LinkedIn's anti-bot systems block you
- ❌ Requires massive engineering effort
- ❌ GDPR compliance complex and expensive
- ❌ Legal risk from LinkedIn lawsuits

**Option 3: Minimal/Legal Sourcing (Public APIs Only)**
```python
# GitHub public API - zero TOS risk
# Stack Overflow API - explicitly allows research
# Google Custom Search - search engine, not scraping

# These are slower but completely legal
```

---

### **Compliance Guidelines for Using Vendor Data:**

If you use a vendor like Proxycurl or Nubela:

✅ **DO:**
- Verify vendor's legal basis for data sourcing
- Check vendor's GDPR compliance (ask for DPA)
- Review vendor's terms - who is liable for TOS violations?
- Store API credentials securely (environment variables)
- Document that data comes from vendor (not LinkedIn direct)
- Respect data retention limits (1-2 years max)
- Provide opt-out mechanism for candidates
- Include vendor disclosure in privacy policy

❌ **DON'T:**
- Assume vendor has official LinkedIn partnership
- Use vendor data without understanding their sourcing method
- Contact candidates without valid consent
- Store data longer than vendor's license allows
- Scrape LinkedIn yourself "to supplement" vendor data
- Claim you have LinkedIn API access

---

### **The Real Question for Your Legal Team:**

When evaluating a data vendor, ask:

1. **Data Source:** Where does your data come from?
   - Answer: Public web scraping, data brokers, etc.
   
2. **Legal Basis:** What legal authority allows this?
   - Answer: *hiQ ruling* (US), GDPR exemptions for legitimate interest (EU), etc.
   
3. **Liability:** Who is liable if LinkedIn sues?
   - Answer: Vendor should indemnify you
   
4. **GDPR Compliance:** How do you handle EU residents?
   - Answer: Should have DPA, possibly geofencing, contact info limitations

5. **Refreshed Data:** How often is data updated?
   - Answer: Daily/weekly crawler runs

6. **Verification:** How is contact data verified?
   - Answer: Pattern matching, third-party verification, user crowdsourcing

If vendor can't answer these, it's not enterprise-ready.

---

## � Cost Analysis & Pricing Strategy

### Vendor API Cost Comparison (Per Profile)

| Vendor | Search Cost | Enrichment Cost | Total Per Profile | Coverage | Quality |
|--------|-------------|-----------------|-------------------|----------|---------|
| **Proxycurl** | $0.01 | $0.03 | **$0.04** | 800M+ | ⭐⭐⭐⭐⭐ |
| **Nubela/PDL** | $0.005 | $0.015 | **$0.02** | 500M+ | ⭐⭐⭐⭐ |
| **Apollo.io** | $0.01 | $0.02 | **$0.03** | 270M+ | ⭐⭐⭐ |
| **PeopleGPT** | Subscription-based | N/A | **$99-499/mo** | 800M+ | ⭐⭐⭐⭐ |
| **Google CSE** | **Free** | Manual | **$0** | Public web | ⭐⭐ |

**Real-World Cost Scenarios:**

| Use Case | Method | Profiles/Month | Monthly Cost | Notes |
|----------|--------|----------------|--------------|-------|
| **Startup (Light)** | Google CSE + Manual | 50 | **$0** | Free tier, manual enrichment |
| **Startup (Automated)** | Nubela API | 200 | **$4** | Pay-as-you-go |
| **SMB Recruiter** | Proxycurl API | 500 | **$20** | Standard usage |
| **Agency (Medium)** | Proxycurl/Nubela Mix | 2,000 | **$60** | Blended rate |
| **Enterprise** | PDL Bulk + Proxycurl | 10,000 | **$200** | Volume discount |
| **PeopleGPT Competitor** | Subscription Model | Unlimited* | **$99-499/mo** | *Fair use limits apply |

### OpenTalent Pricing Tiers (Recommended Model)

#### **Tier 1: Free (Agentic Browser Search)** 🆓
- **Price:** $0/month
- **What's Included:**
  - Manual Google X-Ray search (unlimited)
  - Agentic browser automation for search
  - Light profile cards (title, snippet, URL)
  - Export to CSV (up to 50 profiles/month)
  - BYOK: Users bring their own API keys (optional)
- **Target:** Individual recruiters, students, trial users
- **Positioning:** "Search 800M+ profiles for free using Google"

#### **Tier 2: Starter (Pay-Per-Reveal)** 💳
- **Price:** $0.02/profile (pay-as-you-go)
- **What's Included:**
  - Everything in Free tier
  - API integration (Nubela/Proxycurl BYOK)
  - Unlimited light searches
  - Pay only when revealing full profile
  - Contact data (email, phone) when available
  - Audit logging & compliance tracking
  - GDPR/CCPA compliance tools
  - 1-year data retention
- **Target:** Freelance recruiters, small agencies
- **Positioning:** "Access 800M+ profiles via data partners, pay per use"
- **Monthly Cost Examples:**
  - 50 reveals: $1
  - 200 reveals: $4
  - 500 reveals: $10

#### **Tier 3: Professional (Subscription + Credits)** 🚀
- **Price:** $49/month + $0.015/profile (bulk rate)
- **What's Included:**
  - Everything in Starter tier
  - 500 free reveals/month (worth $10)
  - Bulk discount on additional reveals
  - Priority API rate limits
  - Advanced search filters
  - CRM/ATS integrations
  - Team collaboration (up to 5 users)
  - 2-year data retention
  - Email support
- **Target:** Growing agencies, in-house recruiting teams
- **Positioning:** "Multi-source talent discovery across 800M+ global profiles"
- **Monthly Cost Examples:**
  - Base: $49 (includes 500 reveals)
  - +500 reveals: $49 + $7.50 = $56.50
  - +2,000 reveals: $49 + $30 = $79

#### **Tier 4: Enterprise (Custom Volume)** 🏢
- **Price:** Custom (bulk contract)
- **What's Included:**
  - Everything in Professional tier
  - Unlimited users
  - Custom API integration
  - White-label option
  - Dedicated data vendor contracts
  - Custom retention policies
  - Legal indemnification
  - SLA guarantees (99.9% uptime)
  - Dedicated account manager
  - Custom compliance workflows
- **Target:** Large agencies, Fortune 500 HR departments
- **Positioning:** "Powered by [Proxycurl/PDL] with 800M+ profile coverage"
- **Pricing Structure:**
  - 10K profiles/month: $200/mo ($0.02/profile)
  - 50K profiles/month: $750/mo ($0.015/profile)
  - 100K+ profiles/month: Custom rate

### Cost Comparison: OpenTalent vs. Competitors

| Feature | OpenTalent Free | OpenTalent Pro | PeopleGPT | Juicebox | SeekOut |
|---------|-----------------|----------------|-----------|----------|---------|
| **Base Price** | $0 | $49/mo | $99/mo | $199/mo | $299/mo |
| **Profiles Access** | 800M+ (search) | 800M+ (reveal) | 800M+ | 800M+ | 900M+ |
| **Search Limit** | Unlimited | Unlimited | 500/mo | 1,000/mo | 2,000/mo |
| **Reveal Limit** | 50/mo (export) | 500 + extras | Unlimited* | Unlimited* | Unlimited* |
| **Contact Data** | Manual lookup | ✅ Included | ✅ Included | ✅ Included | ✅ Included |
| **BYOK** | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Agentic Search** | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Privacy Focus** | ✅ Local-first | ✅ Local-first | ⚠️ Cloud | ⚠️ Cloud | ⚠️ Cloud |
| **Cost at 2K reveals** | $0 (manual) | $79 | $99 | $199 | $299 |

*Fair use limits typically 5K-10K reveals/month

### Marketing Claims (Permissible Language)

✅ **ALLOWED (with attribution):**
- "Search 800M+ professional profiles via integrated data partners"
- "Multi-source talent discovery across 800M+ global profiles"
- "Powered by [Proxycurl/PDL/Nubela] with 800M+ profile coverage"
- "Access to 800M+ profiles through leading data providers"
- "Desktop app with 800M+ profile search capability"

❌ **NOT ALLOWED:**
- "Our database contains 800M profiles" (false ownership)
- "800M profiles" without vendor attribution (misleading)
- Exact competitor language ("Talent discovery across 800M+ global profiles" without differentiation)

### Required Disclosures (FTC/GDPR Transparency)

**In Marketing Materials:**
```
OpenTalent provides access to professional data through third-party 
data providers including Proxycurl, People Data Labs, and Nubela. 
Profile data is sourced from publicly available information aggregated 
by our partners. Users must bring their own API keys (BYOK model) for 
paid features. OpenTalent does not store or own candidate data; all 
data is cached locally on your device per your retention settings.
```

**In Privacy Policy:**
```
Data Sources: OpenTalent integrates with third-party data providers 
(Proxycurl, Nubela, People Data Labs) to enable candidate search. 
These providers aggregate publicly available professional data from 
LinkedIn, GitHub, Stack Overflow, and other public sources.

Data Storage: All candidate data is stored locally on your device 
using encrypted SQLite (SQLCipher). We do not transmit or store 
candidate data on our servers.

User Responsibility: By using BYOK (Bring Your Own Key), you agree 
to comply with vendor terms of service and applicable data protection 
laws (GDPR, CCPA). You are responsible for obtaining and maintaining 
valid consent for candidate outreach.

Vendor Liability: Our data partners (not OpenTalent) are responsible 
for data sourcing compliance. We recommend reviewing vendor DPAs and 
legal indemnification terms.
```

### Revenue Projection Model

**Scenario: 1,000 Active Users (Year 1)**

| Tier | Users | Monthly Rev/User | Total Monthly | Annual |
|------|-------|------------------|---------------|--------|
| Free | 600 | $0 | $0 | $0 |
| Starter (PAYG) | 250 | $10 | $2,500 | $30,000 |
| Professional | 140 | $49-79 | $8,960 | $107,520 |
| Enterprise | 10 | $500 | $5,000 | $60,000 |
| **Total** | **1,000** | - | **$16,460** | **$197,520** |

**Growth Assumptions:**
- 60% free tier (acquisition funnel)
- 25% convert to Starter after 50 free reveals
- 14% upgrade to Professional (agencies)
- 1% Enterprise (large orgs)

**Breakeven Analysis:**
- Development cost: $120K/year (2 devs)
- Infrastructure: $12K/year (AWS, APIs)
- Marketing: $24K/year (content, SEO)
- **Total Cost:** $156K/year
- **Breakeven:** ~800 paid users
- **Target:** 1,000 users = 25% profit margin

---

## �🖥️ Production Desktop Architecture (Compliant, Cost-Controlled)

**Goals:** BYOK liability shield, avoid TOS scraping risk, control vendor spend, satisfy GDPR (Article 14) and CCPA.

### Core Principles
- **BYOK:** Users bring their own vendor keys (Proxycurl/Nubela/PDL). No bundled keys.
- **Local-first:** All data, policies, and audit logs stay on the user’s machine; encrypted at rest (SQLite + SQLCipher) and via OS keychain for secrets (Keytar).
- **Pay-to-Reveal:** Discovery is cheap; enrichment only on user action.
- **Geofence + Consent:** Block EU profiles unless consent/notification is satisfied; honor retention limits.
- **Deterministic Identity:** Match by canonical URL and vendor ID; avoid fuzzy matches locally.

### Data Flow (Two-Stage, Pay-to-Reveal)
1) **Discovery (cheap):** SERP provider (SerpApi/DataForSEO) → light results (title/snippet/URL) stored locally. Google CSE as fallback.
2) **Reveal (paid):** User clicks "Reveal" (or selects top N) → vendor enrichment API → full profile stored locally.
3) **Cache + TTL:** Store enriched records with region-based retention (e.g., 365–730 days); auto-purge on expiry.
4) **UI:** Show light cards first; reveal button; per-source rate-limit badges; geofence/consent status chips; Article 14 countdown badge.

### Policy Engine (per request)
- **Geo/Consent:** If region == EU and no consent/notification, block or start Article 14 timer.
- **Rate Limits:** Token bucket per vendor + per SERP; exponential backoff + circuit breaker on 429s/5xx.
- **Data Minimization:** Only store fields required for sourcing; redact PII from logs.
- **Article 14 Countdown (EU):**
  - On enrich: set `enriched_at` and `notification_due = enriched_at + 30d`.
  - If no outreach/notification logged by due date → tombstone (hide/lock) profile locally.
  - Outreach action logs `notification_sent: true` in audit trail.

### Identity Resolution (Local, Deterministic)
- **Primary key:** Canonical LinkedIn URL (normalize trailing slash, lowercase host).
- **Secondary:** Vendor `profile_id` when present.
- **Avoid:** Fuzzy name/title matching locally (high false positives).

### Storage & Security
- **DB:** SQLite + SQLCipher; schema: profiles, searches, audit_logs, retention_timers.
- **Secrets:** OS keychain via Keytar; never store API keys in localStorage/files.
- **Audit Logs:** Append-only, redacted (query, filters, counts, source, consent status, geo decision, reveal actions, notification_sent, deletion events). No raw PII in logs.

### UI/UX Hooks
- Reveal buttons (single/top N) with credit estimate before call.
- Badges: geo status (EU blocked/allowed), rate-limit state, Article 14 countdown (days left), data source (SERP vs vendor).
- Controls: retention TTL per region, consent toggles, dry-run mode (log decisions, no outbound calls).

### Vendor/Key Handling (Liability Shield)
- Users paste their own keys (BYOK); your app is a client tool, not a data vendor.
- Document vendor sourcing method and liability terms; prompt user to accept vendor TOS.

### Testing Checklist
- Policy engine unit tests: EU block, consent path, notification countdown, tombstone at Day 30.
- Rate-limit tests: bucket depletion, backoff, circuit breaker.
- Audit integrity: append-only, redaction verified.
- Dry-run mode: decisions logged, zero external calls.

### Policy Engine (Pseudo-code)
```python
def authorize_request(request, ctx):
    # ctx: region, consent_flag, notification_sent, enriched_at, rate_buckets
    if ctx.region == "EU":
        # Article 14: must notify within 30 days of enrichment
        if not ctx.consent_flag and not ctx.notification_sent:
            if ctx.enriched_at and days_since(ctx.enriched_at) >= 30:
                return Deny(reason="Article 14 deadline passed; tombstoned")
            # allow discovery; enrichment starts countdown
    # Rate limit (token bucket per vendor/source)
    if not has_tokens(ctx.rate_buckets[request.source]):
        return RetryAfter(reason="Rate limit", retry_in=ctx.rate_buckets[request.source].next_window())
    # Minimal fields only; redact before logging
    return Allow()
```

### Sample Local DB Schema (SQLite + SQLCipher)
```sql
-- profiles
CREATE TABLE profiles (
  id INTEGER PRIMARY KEY,
  canonical_url TEXT UNIQUE,          -- normalized LinkedIn URL
  vendor_id TEXT,                     -- vendor profile_id
  source TEXT,                        -- vendor or serp
  region TEXT,                        -- inferred region (e.g., EU/US)
  enriched_at DATETIME,               -- when full data fetched
  notification_sent BOOLEAN DEFAULT 0,
  notification_due DATETIME,          -- enriched_at + 30d (EU)
  retention_expiry DATETIME,          -- per-region TTL
  payload_json TEXT,                  -- encrypted payload
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profiles_url ON profiles(canonical_url);
CREATE INDEX idx_profiles_vendor ON profiles(vendor_id);
CREATE INDEX idx_profiles_retention ON profiles(retention_expiry);

-- searches (light results cache)
CREATE TABLE searches (
  id INTEGER PRIMARY KEY,
  query TEXT,
  region TEXT,
  source TEXT,           -- serp provider
  results_json TEXT,      -- light cards (title/snippet/url)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- audit_logs (redacted, append-only)
CREATE TABLE audit_logs (
  id INTEGER PRIMARY KEY,
  event_type TEXT,        -- search, reveal, outreach, delete, tombstone
  source TEXT,            -- vendor or serp
  query TEXT,
  counts INT,
  geo TEXT,
  consent_status TEXT,    -- none/consent/notification_sent
  details TEXT,           -- small metadata; no PII
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
``` 

---

## �🔗 Platform-Specific Guidelines

### LinkedIn (Official APIs via Third-Party Vendors)

⚠️ **Important:** Direct access to LinkedIn's Recruiter API requires becoming a formal LinkedIn Partner (which requires enterprise contracts for vendors like Workday, Greenhouse, Lever). This is not available to individual developers or small startups.

**✅ DO (Use Vendor APIs):**
- Use official vendor APIs (Proxycurl, Nubela, RapidAPI providers)
- Access only public profile data through vendor
- Respect vendor rate limits
- Contact candidates with explicit consent or opt-in flags
- Honor "do not contact" preferences
- Document all sourcing in audit trail
- Store API keys in environment variables (never in code)

**❌ DON'T:**
- Scrape LinkedIn directly with selenium/BeautifulSoup
- Use fake accounts to access LinkedIn
- Contact users without valid consent
- Bypass vendor rate limits
- Store data longer than retention policy (1-2 years)
- Use credential-stuffing or TOS-violating automation

**Compliance Check:**
```bash
# ✅ Verify using official vendor API (Proxycurl/Nubela)
# ✅ Rate limits respected (vendor enforced)
# ✅ Only public profile data accessed
# ✅ Audit trail shows sourcing method (vendor API + filters used)
```

**Real Example:**
```python
# COMPLIANT: Using vendor API
response = requests.get(
    "https://npi.proxycurl.com/api/v2/linkedin/profile/search",
    headers={"Authorization": f"Bearer {PROXYCURL_API_KEY}"},
    params={"skills": "Python,AWS", "location": "San Francisco"}
)

# NON-COMPLIANT: Direct scraping
from selenium import webdriver
driver.get("https://linkedin.com")  # ❌ Violates LinkedIn TOS
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
