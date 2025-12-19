#!/usr/bin/env bash
set -euo pipefail

# Verify Desktop Integration Service (gateway) on port 8009
# Checks:
# 1) Health endpoint
# 2) OpenAPI available
# 3) Voice synth endpoint has schema refs
# 4) Analytics sentiment endpoint has schema refs
# 5) Models list endpoint works
# 6) Interview start/respond/summary basic flow (smoke)

BASE_URL="${BASE_URL:-http://localhost:8009}"

log() { printf "[verify] %s\n" "$*"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

require_cmd curl
require_cmd jq

post_json() {
  local url="$1"; shift
  local data="$1"; shift
  local allowed=("$@")
  local tmp
  tmp=$(mktemp)
  local status
  status=$(curl -s -o "$tmp" -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$data" || true)
  if [[ " ${allowed[*]} " != *" $status "* ]]; then
    echo "Request failed: $url (status $status)" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi
  cat "$tmp"
  rm -f "$tmp"
}

log "Using BASE_URL=$BASE_URL"

# 1) Health
log "Checking health..."
curl -sf "$BASE_URL/health" | jq . >/tmp/gateway-health.json
log "Health OK: $(jq -r '.status' /tmp/gateway-health.json)"

# 2) OpenAPI
log "Checking OpenAPI availability..."
OPENAPI_JSON=$(curl -sf "$BASE_URL/openapi.json")
log "OpenAPI fetched (${#OPENAPI_JSON} bytes)"

echo "$OPENAPI_JSON" >/tmp/gateway-openapi.json

# 3) Voice schema
log "Checking voice synth schema ref..."
VOICE_REF=$(echo "$OPENAPI_JSON" | jq -r '.paths["/api/v1/voice/synthesize"].post.requestBody.content["application/json"].schema["$ref"] // ""')
if [[ "$VOICE_REF" != "#/components/schemas/SynthesizeSpeechRequest" ]]; then
  echo "Voice synth schema missing or wrong: $VOICE_REF" >&2; exit 1;
fi
log "Voice synth schema OK ($VOICE_REF)"

# 4) Analytics schema
log "Checking analytics sentiment schema ref..."
AN_REF=$(echo "$OPENAPI_JSON" | jq -r '.paths["/api/v1/analytics/sentiment"].post.requestBody.content["application/json"].schema["$ref"] // ""')
if [[ "$AN_REF" != "#/components/schemas/AnalyzeSentimentRequest" ]]; then
  echo "Analytics sentiment schema missing or wrong: $AN_REF" >&2; exit 1;
fi
log "Analytics schema OK ($AN_REF)"

# 5) Models list
log "Listing models..."
curl -sf "$BASE_URL/api/v1/models" | jq '.models | length' >/tmp/gateway-models-count
log "Models available: $(cat /tmp/gateway-models-count)"

# 6) Interview smoke (start/respond/summary)
log "Starting interview..."
START_PAYLOAD='{"role":"Software Engineer","model":"vetta-granite-2b-gguf-v4","totalQuestions":2}'
START_RES=$(post_json "$BASE_URL/api/v1/interviews/start" "$START_PAYLOAD" 200 502 503)
SESSION_ID=$(echo "$START_RES" | jq -r '.sessionId // .session.id // empty')
if [[ -z "$SESSION_ID" ]]; then
  log "No sessionId returned; using inline session."; fi

log "Responding to interview..."
RESP_PAYLOAD=$(jq -n --arg msg "I have 5 years of backend experience." --argjson session "${START_RES}" '{message:$msg, session:$session}' )
RESP_RES=$(post_json "$BASE_URL/api/v1/interviews/respond" "$RESP_PAYLOAD" 200 502 503)

log "Requesting summary..."
SUMM_PAYLOAD="$RESP_RES"
SUMM_RES=$(post_json "$BASE_URL/api/v1/interviews/summary" "$SUMM_PAYLOAD" 200 502 503)
SUMMARY_TEXT=$(echo "$SUMM_RES" | jq -r '.summary // .summaryText // empty')
log "Summary received length: ${#SUMMARY_TEXT}"

log "✅ Verification passed"
