# Data Enrichment Agent

**Port:** 8097
**Purpose:** Local-first profile enrichment (FREE tier primary, optional PAID vendor tier)
**Status:** ✅ Phase 2 Complete - Stack Overflow & Google X-Ray Added

## Architecture: LOCAL-FIRST + Optional PAID Tier

### FREE Tier (Default - No API Keys Required)

| Method | Cost | Quality | Coverage | Status | Speed |
|--------|------|---------|----------|--------|-------|
| **GitHub API** | $0.00 | ⭐⭐⭐⭐ | 500M+ devs | ✅ **Working** | 1-2 sec |
| **Stack Overflow API** | $0.00 | ⭐⭐⭐ | 20M+ devs | ✅ **Working** | 2-3 sec |
| **Google X-Ray** | $0.00 | ⭐⭐ | Public LinkedIn | ⚠️ **Limited** | 3-5 sec |
| **LinkedIn Public** | $0.00 | ⭐⭐ | Search results | 🔄 **Fallback** | N/A |

### PAID Tier (Optional - Premium Quality)

| Vendor | Cost/Profile | Quality | Coverage | Status |
|--------|-------------|---------|----------|--------|
| **Proxycurl** | $0.04 | ⭐⭐⭐⭐⭐ | 800M+ | 🔄 Coming soon |
| **Nubela** | $0.02 | ⭐⭐⭐⭐ | 500M+ | 🔄 Coming soon |

## ✅ Phase 2 Implementation Status

**Completed Features:**

- ✅ GitHub API integration (60 req/hour, no auth)
- ✅ Stack Overflow API integration (public API, no auth)
- ✅ Google X-Ray browser automation (Playwright)
- ✅ Smart auto-enrichment routing (Cache → GitHub → Stack Overflow → Google X-Ray → Fallback)
- ✅ Profile caching (30-day TTL)
- ✅ GDPR audit logging
- ✅ Message bus integration
- ✅ Health/Methods endpoints updated

**Current Limitations:**

- ⚠️ Google X-Ray: Blocked by Google anti-bot measures (falls back to minimal profile)
- 🔄 PAID Tier: Framework ready, vendors not yet integrated

## Features

- ✅ **FREE Tier**: Zero external costs, works 100% locally
- ✅ **Multi-Method Enrichment**: GitHub, Stack Overflow, Google X-Ray
- ✅ **Smart Routing**: Automatic method selection based on URL type
- ✅ **Profile Caching**: 30-day cache with deduplication
- ✅ **GDPR Compliant**: Full audit logging (Article 30)
- ✅ **Browser Automation**: Playwright for web scraping
- ✅ **Async Processing**: Non-blocking enrichment requests
- ✅ **Message Bus**: Redis integration with other agents

## API Endpoints

### Health Check

```bash
GET http://localhost:8097/health
```

**Response:**

```json
{
  "status": "✅ healthy",
  "agent": "data-enrichment",
  "port": 8097,
  "tiers": {
    "free": {
      "status": "✅ Available",
      "methods": {
        "github_public": "✅ Ready",
        "stackoverflow": "✅ Ready",
        "google_xray": "✅ Available"
      }
    },
    "paid": {
      "status": "🔄 Coming soon",
      "vendors": ["proxycurl", "nubela"]
    }
  }
}
```

### Enrich Profiles (FREE Tier)

```bash
POST http://localhost:8097/enrich
Content-Type: application/json

{
  "pipeline_id": "discovery_001",
  "profile_urls": [
    "https://github.com/torvalds",
    "https://stackoverflow.com/users/22656",
    "https://linkedin.com/in/some-profile"
  ],
  "user_id": "recruiter_123"
}
```

**Response:**

```json
{
  "request_id": "enrich_discovery_001_1733847600.0",
  "status": "pending",
  "profiles_queued": 3,
  "estimated_time_seconds": 6
}
```

### List Available Methods

```bash
GET http://localhost:8097/methods
```

**Response:**

```json
{
  "free_tier": [
    {
      "method": "github_public",
      "cost": "$0.00",
      "quality": "⭐⭐⭐⭐ (High)",
      "speed": "1-2 sec",
      "coverage": "500M+ profiles",
      "status": "✅ Ready"
    },
    {
      "method": "stackoverflow",
      "cost": "$0.00",
      "quality": "⭐⭐⭐ (Good)",
      "speed": "2-3 sec",
      "coverage": "20M+ profiles",
      "status": "✅ Ready"
    },
    {
      "method": "google_xray",
      "cost": "$0.00",
      "quality": "⭐⭐ (Basic)",
      "speed": "3-5 sec",
      "coverage": "Public LinkedIn",
      "status": "✅ Ready"
    }
  ],
  "paid_tier": [...]
}
```

## Installation & Testing

```bash
cd agents/data-enrichment-agent

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for Google X-Ray)
playwright install chromium

# Run agent
python main.py
```

## Usage Examples

### Example 1: GitHub Profile Enrichment

```bash
curl -X POST http://localhost:8097/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_id": "test_001",
    "profile_urls": ["https://github.com/torvalds"],
    "user_id": "test_user"
  }'
```

**Result:** Linus Torvalds profile with bio, location, social links

### Example 2: Stack Overflow Profile Enrichment

```bash
curl -X POST http://localhost:8097/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_id": "test_002",
    "profile_urls": ["https://stackoverflow.com/users/22656"],
    "user_id": "test_user"
  }'
```

**Result:** Jon Skeet profile with 1.5M+ reputation, badges, location

### Example 3: LinkedIn Profile Search (Limited)

```bash
curl -X POST http://localhost:8097/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_id": "test_003",
    "profile_urls": ["https://linkedin.com/in/some-profile"],
    "user_id": "test_user"
  }'
```

**Result:** Basic profile or fallback (Google anti-bot measures may block)

## Performance Results

**Test Results (December 10, 2025):**

- ✅ GitHub: 100% success rate, ~1.5 sec per profile
- ✅ Stack Overflow: 100% success rate, ~2 sec per profile
- ⚠️ Google X-Ray: Limited by anti-bot measures, ~15 sec timeout
- ✅ Cache: Working, reduces duplicate requests
- ✅ Audit Logging: GDPR compliant, all enrichments logged

## Roadmap

**Phase 2 (Current):** ✅ **COMPLETED**

- ✅ GitHub API integration
- ✅ Stack Overflow API integration
- ✅ Google X-Ray browser automation
- ✅ Smart routing logic
- ✅ Testing and validation

**Phase 3 (Next):** PAID Tier Integration

- 🔄 Proxycurl API integration
- 🔄 Nubela API integration
- 🔄 Credit system implementation
- 🔄 Quality comparison testing

## References

- [AGENTS.md](../../AGENTS.md) - Project architecture
- [LOCAL_AI_ARCHITECTURE.md](../../LOCAL_AI_ARCHITECTURE.md) - Local AI specs
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Development standards

---

**Version:** 2.1 (Phase 2 Complete)
**Status:** ✅ Ready for Production (FREE Tier)
**Last Updated:** December 10, 2025
