#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

BASE_URL="${INTEGRATION_BASE_URL:-http://localhost:8009}"
SCHEMA_PATH="specs/gateway-openapi.json"
CLIENT_OUT="src/api/gateway"
TYPES_OUT="src/types/gateway.ts"

mkdir -p "$(dirname "$SCHEMA_PATH")" "$(dirname "$TYPES_OUT")"

echo "📥 Fetching OpenAPI schema from ${BASE_URL}/openapi.json"
curl -sSf "${BASE_URL}/openapi.json" -o "$SCHEMA_PATH"

echo "🧩 Generating TypeScript client (axios)"
./node_modules/.bin/openapi -i "$SCHEMA_PATH" -o "$CLIENT_OUT" --client axios --useUnionTypes true

echo "🔡 Generating TypeScript types"
./node_modules/.bin/openapi-typescript "$SCHEMA_PATH" -o "$TYPES_OUT"

echo "✅ Gateway client and types generated:"
echo " - $CLIENT_OUT"
echo " - $TYPES_OUT"}
