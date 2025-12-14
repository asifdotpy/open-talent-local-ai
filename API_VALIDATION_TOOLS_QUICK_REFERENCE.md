# API Validation Tools - Quick Reference

**Created:** December 14, 2025  
**Status:** ✅ Ready for use

---

## 🎯 Quick Start (2 minutes)

### 1. Run All Tests
```bash
cd /home/asif1/open-talent
pytest tests/test_api_inventory_validation.py -v
```

**Output:**
- ✅ PASSED = API working correctly
- ⏭️ SKIPPED = Service not running (OK)
- ❌ FAILED = API issue needs fixing

### 2. Validate OpenAPI Schemas
```bash
python tools/openapi_schema_validator.py --all
```

**Output Shows:**
- ✅ VALID = OpenAPI schema compliant
- ❌ INVALID = Schema has errors
- Specific error messages with suggestions

### 3. Check Specific Service
```bash
# Notification Service (example)
python tools/openapi_schema_validator.py --service notification --verbose
```

---

## 📦 What You Have

### Test Suite: `tests/test_api_inventory_validation.py`

6 test classes covering:

| Test Class | Tests | What It Does |
|-----------|-------|-------------|
| TestServiceConnectivity | 2 | Check if services are running |
| TestOpenAPISchemas | 3 | Validate OpenAPI availability & validity |
| TestCoreEndpoints | 2 | Test documented endpoints |
| TestOpenAPICompliance | 2 | Check OpenAPI metadata |
| TestServiceIntegration | 2 | Integration health checks |
| TestSummaryReport | 1 | Generate validation report |

**Total: 14 test methods**

### Validator Tool: `tools/openapi_schema_validator.py`

Standalone Python script that:
- ✅ Validates OpenAPI 3.0+ compliance
- ✅ Checks required fields
- ✅ Validates path definitions
- ✅ Provides detailed error messages
- ✅ Exports results to JSON
- ✅ Works with all 14 services

### Documentation: `docs/developer-guides/API_VALIDATION_GUIDE.md`

Complete guide covering:
- How to use both tools
- Interpretation of results
- Troubleshooting common issues
- CI/CD integration examples
- Tracking metrics

---

## 🔥 Most Common Commands

```bash
# Start a service for testing
python -m uvicorn services.notification-service.main:app --port 8011

# Validate that service
python tools/openapi_schema_validator.py --service notification

# Run all tests
pytest tests/test_api_inventory_validation.py -v

# Test only Notification Service tests
pytest tests/test_api_inventory_validation.py -v -k notification

# Get detailed validation report
python tools/openapi_schema_validator.py --all --verbose

# Export results to file
python tools/openapi_schema_validator.py --all --output validation_report.json
```

---

## ✅ Test Results Explained

### When Notification Service is Running

**Test Suite Output:**
```
test_api_inventory_validation.py::TestServiceConnectivity::test_service_running[notification] PASSED ✅
test_api_inventory_validation.py::TestOpenAPISchemas::test_openapi_schema_available[notification] PASSED ✅
test_api_inventory_validation.py::TestOpenAPISchemas::test_openapi_schema_valid[notification] PASSED ✅
test_api_inventory_validation.py::TestCoreEndpoints::test_core_endpoints[notification] PASSED ✅
```

**Validator Output:**
```
✅ VALID notification (Port 8011)
  OpenAPI: 3.1.0
  Title: Notification Service
  Version: 1.0.0
  Endpoints: 7
  Components: Yes

  ⚠️  Warnings (1):
    - Missing 'info.description'
```

**Meaning:**
- ✅ Service is running and healthy
- ✅ OpenAPI schema is valid and compliant
- ✅ All endpoints are accessible
- ⚠️ Minor suggestions for improvement

---

## 📊 Understanding Test Results

### ✅ PASSED
Service is working correctly.
```
test_service_running[notification] PASSED
```

### ⏭️ SKIPPED
Service not running on expected port (normal during development).
```
test_service_running[user] SKIPPED (service not running on http://localhost:8007)
```
**Fix:** Start the service, then re-run tests

### ❌ FAILED
API is not working as documented.
```
test_openapi_schema_available[notification] FAILED
AssertionError: notification: OpenAPI schema not available (status 404)
```
**Fix:** Check service logs, ensure FastAPI is generating OpenAPI schema

---

## 🎯 Test Coverage

### Services Tested (14 total)
1. Desktop Integration (8009)
2. Security (8010)
3. Notification (8011) ✅ Running
4. AI Auditing (8012)
5. Explainability (8013)
6. Granite Interview (8005) ✅ Running
7. Interview (8006)
8. User (8007)
9. Candidate (8008)
10. Scout (8010)
11. Conversation (8014)
12. Voice (8015)
13. Avatar (8016)
14. Analytics (8017)

### What's Tested Per Service
- ✅ Service connectivity (responds to /health)
- ✅ OpenAPI schema available (/openapi.json)
- ✅ OpenAPI schema valid (conforms to spec)
- ✅ Core endpoints accessible
- ✅ OpenAPI metadata complete (title, version)
- ✅ OpenAPI has documented paths

---

## 🚀 Running Tests in CI/CD

### GitHub Actions
```yaml
name: API Validation
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/test_api_inventory_validation.py -v
```

### Local Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run tests before commit
python -m pytest tests/test_api_inventory_validation.py::TestOpenAPISchemas -q
if [ $? -ne 0 ]; then
  echo "API validation failed. Please fix before committing."
  exit 1
fi
```

---

## 📈 Metrics Dashboard

Track these numbers over time:

| Metric | Target | Command |
|--------|--------|---------|
| Services Running | 14/14 | `pytest ... -v \| grep PASSED` |
| OpenAPI Valid | 14/14 | `openapi_schema_validator.py --all` |
| Total Errors | 0 | Check validator output |
| Total Warnings | <5 | Check validator output |

---

## 🔧 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Connection refused" | Start service on correct port |
| "OpenAPI schema not available" | FastAPI auto-generates, just run service |
| "OpenAPI schema validation failed" | Run with `--verbose` to see what's missing |
| "Health endpoint returned 500" | Check service logs for errors |
| Test says "SKIPPED" | That's OK if service not running; just run tests again when service starts |

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `tests/test_api_inventory_validation.py` | Main test suite (14 tests per service) |
| `tools/openapi_schema_validator.py` | Standalone validator with detailed output |
| `docs/developer-guides/API_VALIDATION_GUIDE.md` | Complete documentation |
| `MICROSERVICES_API_INVENTORY.md` | Service inventory being validated |
| `OPENAPI_VERIFICATION_COMPLETE.md` | OpenAPI verification status |

---

## ✨ Key Features

✅ **Automated** — No manual testing needed  
✅ **Comprehensive** — Tests all 14 services  
✅ **Detailed** — OpenAPI validation with suggestions  
✅ **Flexible** — Test all or specific services  
✅ **Exportable** — JSON output for CI/CD integration  
✅ **User-friendly** — Clear error messages and suggestions  
✅ **Fast** — Complete validation in seconds  

---

## 📞 Support

For detailed help, see:
- **Usage Guide:** `docs/developer-guides/API_VALIDATION_GUIDE.md`
- **Code Comments:** In test and validator files
- **Example Output:** Run commands above and observe results

---

**Status:** ✅ Ready to use  
**Last Updated:** December 14, 2025  
**Next:** Run tests against your services!

