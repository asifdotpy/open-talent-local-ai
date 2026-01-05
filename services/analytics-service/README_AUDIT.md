# Service Audit Results: analytics-service

**Location**: `/home/asif1/open-talent/services/analytics-service`
**Type**: FastAPI

## Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service identification |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/analyze/sentiment` | Sentiment analysis (TextBlob) |
| `POST` | `/api/v1/analyze/quality` | Response quality heuristic (length/keywords) |
| `POST` | `/api/v1/analyze/bias` | Bias detection (keyword matching) |
| `POST` | `/api/v1/analyze/expertise` | Expertise assessment (keyword matching) |
| `POST` | `/api/v1/analyze/performance` | Aggregate performance analysis |
| `POST` | `/api/v1/analyze/report` | Generate intelligence report |
| `GET` | `/api/v1/analytics/interviews` | Get interview stats (Stubbed) |
| `GET` | `/api/v1/analytics/candidates/{candidate_id}` | Get candidate analytics (Stubbed) |
| `GET` | `/api/v1/analytics/interviews/{interview_id}` | Get interview performance (Stubbed) |
| `GET` | `/api/v1/analytics/metrics` | Get overall metrics (Stubbed) |
| `GET` | `/api/v1/analytics/metrics/timeseries` | Get time series metrics (Stubbed) |
| `POST` | `/api/v1/analytics/reports` | Create report (Stubbed) |
| `GET` | `/api/v1/analytics/reports/{report_id}` | Get report (Stubbed) |
| `GET` | `/api/v1/analytics/reports/{report_id}/export` | Export report (Stubbed URL) |

## Mock Data / Simulation Findings

1. **Heuristic Logic**: `analyze_quality`, `analyze_bias`, and `analyze_expertise` rely on simple keyword lists and string matching rather than ML models.
2. **Stubbed Analytics**: Endpoints under `/api/v1/analytics/` return hardcoded zero-values or empty structures (e.g., `metrics` returns 0 for all counts).
3. **Fake Export**: Report export returns `https://example.com/reports/...`.
