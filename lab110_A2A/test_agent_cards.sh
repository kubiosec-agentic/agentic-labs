#!/usr/bin/env bash
set -e

echo "=== A2A Agent Card Verification ==="
echo ""

ADK_BASE="http://localhost:8001/a2a/check_prime_agent"
CARD_PATH="/.well-known/agent-card.json"

# ── Test 1: Check if the ADK server is running ────────────────────
echo "--- Test 1: ADK server health check ---"
if curl -sf "${ADK_BASE}" -o /dev/null 2>&1; then
    echo "  PASS: ADK server is reachable at ${ADK_BASE}"
else
    echo "  FAIL: Cannot reach ADK server at ${ADK_BASE}"
    echo "  Start it with: cd adk_server && source .venv/bin/activate && adk api_server --a2a --port 8001 remote_a2a"
    exit 1
fi

# ── Test 2: Fetch the agent card ──────────────────────────────────
echo ""
echo "--- Test 2: Fetch agent card ---"
CARD_URL="${ADK_BASE}${CARD_PATH}"
echo "  GET ${CARD_URL}"
echo ""

CARD=$(curl -sf "${CARD_URL}")
if [ -z "$CARD" ]; then
    echo "  FAIL: Empty response from agent card endpoint"
    exit 1
fi

echo "$CARD" | python3 -m json.tool 2>/dev/null || echo "$CARD"
echo ""
echo "  PASS: Agent card retrieved successfully"

# ── Test 3: Validate required agent card fields ───────────────────
echo ""
echo "--- Test 3: Validate agent card fields ---"

for field in name description version url skills; do
    if echo "$CARD" | python3 -c "import sys,json; d=json.load(sys.stdin); assert '$field' in d" 2>/dev/null; then
        VALUE=$(echo "$CARD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$field',''))" 2>/dev/null)
        echo "  PASS: '$field' present -> ${VALUE:0:60}"
    else
        echo "  FAIL: Missing required field '$field'"
    fi
done

# ── Test 4: Check skills array ────────────────────────────────────
echo ""
echo "--- Test 4: Validate skills ---"
SKILL_COUNT=$(echo "$CARD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('skills',[])))" 2>/dev/null)
echo "  Skills count: $SKILL_COUNT"

echo "$CARD" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for s in d.get('skills', []):
    print(f\"  - {s['name']} ({s['id']}): {s['description']}\")
" 2>/dev/null

# ── Test 5: Send a test task via A2A protocol ─────────────────────
echo ""
echo "--- Test 5: Send a test task (A2A JSON-RPC) ---"

TASK_PAYLOAD=$(cat <<'JSONEOF'
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": "test-001",
  "params": {
    "id": "test-task-001",
    "message": {
      "role": "user",
      "parts": [
        {"type": "text", "text": "Is 42 prime?"}
      ]
    }
  }
}
JSONEOF
)

echo "  POST ${ADK_BASE}"
echo "  Payload: Is 42 prime?"
echo ""

RESPONSE=$(curl -sf -X POST "${ADK_BASE}" \
    -H "Content-Type: application/json" \
    -d "$TASK_PAYLOAD" 2>&1) || true

if [ -n "$RESPONSE" ]; then
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "  PASS: A2A task endpoint responded"
else
    echo "  WARN: No response from task endpoint (may need different path)"
fi

echo ""
echo "=== All tests complete ==="
