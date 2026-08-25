#!/usr/bin/env bash
set -e

echo "=== A2A Agent Card Verification ==="
echo ""

ADK_BASE="http://localhost:8001/a2a/check_prime_agent"
CARD_PATH="/.well-known/agent-card.json"

# ── Test 1: Fetch the agent card (also serves as health check) ────
echo "--- Test 1: Fetch agent card ---"
CARD_URL="${ADK_BASE}${CARD_PATH}"
echo "  GET ${CARD_URL}"
echo ""

CARD=$(curl -sf "${CARD_URL}" 2>&1)
if [ -z "$CARD" ]; then
    echo "  FAIL: Cannot reach agent card endpoint"
    echo "  Start it with: cd adk_server && source .venv/bin/activate && adk api_server --a2a --port 8001 remote_a2a"
    exit 1
fi

echo "$CARD" | python3 -m json.tool 2>/dev/null || echo "$CARD"
echo ""
echo "  PASS: Agent card retrieved successfully"

# ── Test 2: Validate required agent card fields ───────────────────
echo ""
echo "--- Test 2: Validate agent card fields ---"

for field in name description version url skills; do
    if echo "$CARD" | python3 -c "import sys,json; d=json.load(sys.stdin); assert '$field' in d" 2>/dev/null; then
        VALUE=$(echo "$CARD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$field',''))" 2>/dev/null)
        echo "  PASS: '$field' present -> ${VALUE:0:60}"
    else
        echo "  FAIL: Missing required field '$field'"
    fi
done

# ── Test 3: Check skills array ────────────────────────────────────
echo ""
echo "--- Test 3: Validate skills ---"
SKILL_COUNT=$(echo "$CARD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('skills',[])))" 2>/dev/null)
echo "  Skills count: $SKILL_COUNT"

echo "$CARD" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for s in d.get('skills', []):
    print(f\"  - {s['name']} ({s['id']}): {s['description']}\")
" 2>/dev/null

# ── Test 4: Send a test task (A2A JSON-RPC) ───────────────────────
echo ""
echo "--- Test 4: Send a test message (A2A JSON-RPC) ---"

# NOTE: "tasks/send" was the A2A 0.1 method name and no longer exists.
# A2A 0.3 / 1.0 uses "message/send", requires a "messageId", and parts
# are discriminated by "kind" (not "type").
TASK_PAYLOAD=$(cat <<'JSONEOF'
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": "test-001",
  "params": {
    "message": {
      "role": "user",
      "messageId": "test-msg-001",
      "parts": [
        {"kind": "text", "text": "Is 42 prime?"}
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

if [ -z "$RESPONSE" ]; then
    echo "  FAIL: No response from task endpoint"
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    # A JSON-RPC error still comes back as HTTP 200, so check the body.
    if echo "$RESPONSE" | python3 -c "import sys,json; sys.exit(0 if 'error' in json.load(sys.stdin) else 1)" 2>/dev/null; then
        echo "  FAIL: server returned a JSON-RPC error (see above)"
    else
        echo "  PASS: A2A message endpoint responded"
    fi
fi

echo ""
echo "=== All tests complete ==="
