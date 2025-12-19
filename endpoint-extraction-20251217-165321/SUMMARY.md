# OpenTalent Endpoint Extraction Report

**Generated:** Wed Dec 17 16:53:21 +06 2025  
**Location:** /home/asif1/open-talent/endpoint-extraction-20251217-165321

---

## Summary

### avatar-service (Port 8001)
- **Status:** ✅ Running
- **Endpoints:** 46
- **Swagger UI:** http://localhost:8001/docs
- **OpenAPI JSON:** http://localhost:8001/openapi.json
- **Files Generated:**
  - `avatar-service-endpoints.txt` (endpoint paths)
  - `avatar-service-detailed.txt` (methods + descriptions)
  - `avatar-service-full.json` (complete OpenAPI paths)
  - `avatar-service-info.json` (service metadata)

### conversation-service (Port 8003)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/conversation-service && python main.py`

### interview-service (Port 8004)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/interview-service && python main.py`

### security-service (Port 8005)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/security-service && python main.py`

### candidate-service (Port 8008)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/candidate-service && python main.py`

### notification-service (Port 8011)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/notification-service && python main.py`

### ai-auditing-service (Port 8012)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/ai-auditing-service && python main.py`

### analytics-service (Port 8017)
- **Status:** ✅ Running
- **Endpoints:** 16
- **Swagger UI:** http://localhost:8017/docs
- **OpenAPI JSON:** http://localhost:8017/openapi.json
- **Files Generated:**
  - `analytics-service-endpoints.txt` (endpoint paths)
  - `analytics-service-detailed.txt` (methods + descriptions)
  - `analytics-service-full.json` (complete OpenAPI paths)
  - `analytics-service-info.json` (service metadata)

### explainability-service (Port 8014)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/explainability-service && python main.py`

### voice-service (Port 8015)
- **Status:** ❌ Not Running
- **Note:** Start service with: `cd services/voice-service && python main.py`

### scout-service (Port 8010)
- **Status:** ✅ Running
- **Endpoints:** 15
- **Swagger UI:** http://localhost:8010/docs
- **OpenAPI JSON:** http://localhost:8010/openapi.json
- **Files Generated:**
  - `scout-service-endpoints.txt` (endpoint paths)
  - `scout-service-detailed.txt` (methods + descriptions)
  - `scout-service-full.json` (complete OpenAPI paths)
  - `scout-service-info.json` (service metadata)


---

## Statistics

- **Total Services Checked:** 11
- **Running Services:** 3
- **Failed/Unavailable:** 8
- **Total Endpoints Found:** 77
- **Average Endpoints per Service:** 25

---

## Next Steps

1. Review individual service endpoint files
2. Compare with specification documents in project root
3. Update `FINAL_API_VALIDATION_DOCUMENT.md`
4. Cross-reference with service README files
5. Test critical endpoints manually

---

## Files in This Directory

- `SUMMARY.md` - This file
- `*-endpoints.txt` - Simple list of endpoint paths
- `*-detailed.txt` - Endpoints with HTTP methods and descriptions
- `*-full.json` - Complete OpenAPI path objects
- `*-info.json` - Service metadata (title, version, description)

