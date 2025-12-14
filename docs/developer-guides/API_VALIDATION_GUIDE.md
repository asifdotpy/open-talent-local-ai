# API Validation & Testing Guide

**Created:** December 14, 2025  
**Purpose:** Verify all APIs in MICROSERVICES_API_INVENTORY.md are implemented correctly and compliant with OpenAPI standards

---

## 📋 Overview

This guide provides tools and instructions to validate:

1. **API Availability** — Services are running and responding
2. **OpenAPI Compliance** — Schemas follow OpenAPI 3.0+ specification
3. **Endpoint Accessibility** — Core endpoints respond correctly
4. **Schema Validity** — All required fields are present and valid
5. **Integration Health** — Services work together as documented

---

## 🔧 Available Tools

### 1. **API Inventory Validation Test Suite** (pytest)

**Location:** `tests/test_api_inventory_validation.py`

**Purpose:** Comprehensive test suite for all 14 microservices

**Test Classes:**
- `TestServiceConnectivity` — Basic service health checks
- `TestOpenAPISchemas` — OpenAPI schema availability and validity
- `TestCoreEndpoints` — Test documented endpoints
- `TestOpenAPICompliance` — Validate OpenAPI metadata
- `TestServiceIntegration` — Integration and consistency checks
- `TestSummaryReport` — Generate validation report

**Usage:**

```bash
# Run all tests
pytest tests/test_api_inventory_validation.py -v

# Run specific service tests
pytest tests/test_api_inventory_validation.py -v -k "notification"
pytest tests/test_api_inventory_validation.py -v -k "openapi"

# Run with detailed output
pytest tests/test_api_inventory_validation.py -v -s

# Generate HTML report
pytest tests/test_api_inventory_validation.py -v --html=report.html

# Run only health checks
pytest tests/test_api_inventory_validation.py::TestServiceConnectivity -v
```

**Expected Output:**
```
test_api_inventory_validation.py::TestServiceConnectivity::test_service_running[notification] PASSED
test_api_inventory_validation.py::TestOpenAPISchemas::test_openapi_schema_available[notification] PASSED
test_api_inventory_validation.py::TestCoreEndpoints::test_core_endpoints[notification] PASSED
...
```

### 2. **OpenAPI Schema Validator** (standalone tool)

**Location:** `tools/openapi_schema_validator.py`

**Purpose:** Detailed OpenAPI schema validation with suggestions

**Features:**
- ✅ Validates OpenAPI 3.0+ specification compliance
- ✅ Checks required fields (openapi, info, paths, etc.)
- ✅ Validates path definitions and HTTP methods
- ✅ Verifies response definitions
- ✅ Generates detailed error/warning/info messages
- ✅ Exports results to JSON

**Usage:**

```bash
# Validate all running services
python tools/openapi_schema_validator.py --all

# Validate all with details
python tools/openapi_schema_validator.py --all --verbose

# Validate specific service
python tools/openapi_schema_validator.py --service notification
python tools/openapi_schema_validator.py --service notification --verbose

# Export to JSON report
python tools/openapi_schema_validator.py --all --output validation_report.json
```

**Expected Output:**
```
================================================================================
OpenAPI Schema Validator
================================================================================

✅ VALID Notification Service (Port 8011)
  OpenAPI: 3.0.2
  Title: Notification Service
  Version: 1.0.0
  Endpoints: 6
  Components: Yes

  ℹ️  Info (1):
    - Missing 'info.contact'
      💡 Consider adding contact information for support

================================================================================
SUMMARY
================================================================================
Valid Services: 13/14
Invalid Services: 1/14
Total Errors: 0
Total Warnings: 2
```

---

## 📊 Validation Levels

### ❌ Errors (Critical)
Must be fixed before deployment. Examples:
- Missing required OpenAPI fields (openapi, info, paths)
- Invalid OpenAPI version
- No HTTP methods defined for path
- Missing responses definition

### ⚠️ Warnings (Important)
Should be addressed. Examples:
- Missing description
- Path with no HTTP methods
- Missing operationId
- Endpoints without summary/description

### ℹ️ Info (Nice to Have)
Recommendations for better documentation. Examples:
- Missing contact information
- Missing license information
- Missing operationId (optional but helpful)

---

## 🚀 Quick Start

### Step 1: Ensure Services are Running

```bash
# Start Notification Service (example)
cd /home/asif1/open-talent
python -m uvicorn services.notification-service.main:app --port 8011

# In another terminal, verify it's running
curl http://localhost:8011/health
```

### Step 2: Run Validation Tests

```bash
# Run all tests
cd /home/asif1/open-talent
pytest tests/test_api_inventory_validation.py -v

# Watch for any failures
# Services not running will be skipped (OK)
# Failed tests indicate schema or endpoint issues
```

### Step 3: Detailed Schema Validation

```bash
# Check specific service in detail
python tools/openapi_schema_validator.py --service notification --verbose

# Or check all services
python tools/openapi_schema_validator.py --all --verbose
```

### Step 4: Export Report

```bash
# Generate comprehensive JSON report
python tools/openapi_schema_validator.py --all --output api_validation_report.json

# Review report
cat api_validation_report.json | jq '.'  # if jq is installed
# Or open in text editor
```

---

## 📋 API Inventory Checklist

Use this checklist to ensure your API is properly documented:

### Service Configuration
- [ ] Service name matches MICROSERVICES_API_INVENTORY.md
- [ ] Service port matches documentation
- [ ] Service responds to health check (GET /health → 200)
- [ ] Service root endpoint works (GET / → 200 or 404)

### OpenAPI Schema
- [ ] OpenAPI schema available at /openapi.json
- [ ] OpenAPI version is 3.x (3.0.0, 3.0.2, 3.1.0, etc.)
- [ ] All required fields present: openapi, info, paths
- [ ] info.title field is present and meaningful
- [ ] info.version field is present (semantic versioning)

### Endpoints
- [ ] All documented endpoints are defined in paths
- [ ] Each path has at least one HTTP method (GET, POST, etc.)
- [ ] Each method has a responses definition
- [ ] Common response codes documented (200, 400, 404, 500, etc.)
- [ ] operationId defined for each method (recommended)
- [ ] summary or description provided for each method

### Schema Completeness
- [ ] Components section defined (if using reusable schemas)
- [ ] Request/response schemas defined where appropriate
- [ ] Error responses documented with proper status codes
- [ ] Authentication/security schemes documented (if applicable)

---

## 🔍 Interpreting Test Results

### ✅ All Tests Pass
Your service is compliant and properly documented. Great!

### ⏭️ Skipped Tests
Service is not running on expected port. This is OK during development:
```
tests/test_api_inventory_validation.py::...::<service> SKIPPED (service not running)
```

**Fix:** Start the service on the correct port

### ❌ Failed Tests
Schema or endpoint is not working as documented. Must be fixed:
```
tests/test_api_inventory_validation.py::TestOpenAPISchemas::test_openapi_schema_valid[notification] FAILED
```

**Fix:** Review the error message and use detailed validator for suggestions

### Common Failures

**"OpenAPI schema not available"**
- **Cause:** Service doesn't expose /openapi.json
- **Fix:** Ensure FastAPI auto-generates OpenAPI (it does by default)

**"OpenAPI schema validation failed"**
- **Cause:** Schema missing required fields or invalid structure
- **Fix:** Run `openapi_schema_validator.py` with `--verbose` for specific suggestions

**"Health endpoint returned 500"**
- **Cause:** Service has runtime error
- **Fix:** Check service logs for errors

**"Expected 200/204, got 404"**
- **Cause:** Health endpoint not implemented
- **Fix:** Add `@app.get("/health")` endpoint to service

---

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: API Validation

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services (example)
        run: |
          docker-compose up -d
          sleep 10  # Wait for services to start
      
      - name: Run API validation tests
        run: |
          pytest tests/test_api_inventory_validation.py -v --tb=short
      
      - name: Generate validation report
        run: |
          python tools/openapi_schema_validator.py --all --output report.json
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: report.json
```

---

## 📈 Metrics to Track

Monitor these metrics over time:

| Metric | Target | Current |
|--------|--------|---------|
| Services Running | 14/14 | ? |
| OpenAPI Schemas Valid | 14/14 | ? |
| Health Checks Passing | 14/14 | ? |
| Core Endpoints Responding | 14/14 | ? |
| Total Errors | 0 | ? |
| Total Warnings | <5 | ? |

---

## 🛠️ Troubleshooting

### Issue: "Connection refused" error
**Cause:** Service not running on expected port  
**Solution:**
```bash
# Check if service is running
curl http://localhost:8011/health

# Start service
cd /home/asif1/open-talent
python -m uvicorn services.notification-service.main:app --port 8011
```

### Issue: "OpenAPI schema not available"
**Cause:** FastAPI not generating OpenAPI schema  
**Solution:**
```python
# In main.py, ensure FastAPI app is created without disabling OpenAPI:
app = FastAPI()  # ✅ Correct (OpenAPI enabled)
# app = FastAPI(openapi_url=None)  # ❌ Wrong (OpenAPI disabled)

# Also check /docs endpoint
curl http://localhost:8011/docs  # Should return HTML
curl http://localhost:8011/openapi.json  # Should return JSON
```

### Issue: "Schema validation failed: Missing required field"
**Cause:** OpenAPI schema missing required fields  
**Solution:**
```python
# Run detailed validator for suggestions
python tools/openapi_schema_validator.py --service notification --verbose

# Add missing fields to your FastAPI app:
app = FastAPI(
    title="Service Name",
    version="1.0.0",
    description="Service description",
)
```

### Issue: "No paths defined"
**Cause:** Service has no documented endpoints  
**Solution:**
```python
# Add at least one endpoint:
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {"message": "OK"}
```

---

## 📚 References

### FastAPI Documentation
- [FastAPI OpenAPI Documentation](https://fastapi.tiangolo.com/advanced/extending-openapi-schema/)
- [FastAPI Tags and Metadata](https://fastapi.tiangolo.com/tutorial/metadata/#tags)

### OpenAPI Specification
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.3)
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [httpx Documentation](https://www.python-httpx.org/)

---

## 📝 Summary

This validation framework ensures:

✅ All services are discoverable and running  
✅ All APIs follow OpenAPI 3.0+ standard  
✅ All endpoints are documented and respond  
✅ All schemas are valid and complete  
✅ All validations are automated and repeatable  

---

**Last Updated:** December 14, 2025  
**Status:** Ready for use  
**Next Steps:** Run tests against all services to establish baseline

