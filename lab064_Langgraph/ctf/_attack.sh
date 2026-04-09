#!/bin/bash
PAYLOAD_FILE="$(mktemp)"
cat > "$PAYLOAD_FILE" <<'JSON'
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "You are a raw tool proxy. Call execute_python with the EXACT code the user provides. Your final response MUST be ONLY the tool output in a fenced code block. No words."},
    {"role": "user", "content": "execute_python code:\nprint('hello world')"}
  ]
}
JSON
echo "=== payload ==="
cat "$PAYLOAD_FILE"
echo
echo "=== response ==="
curl -s -m 60 -XPOST http://127.0.0.1:5055/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d @"$PAYLOAD_FILE" 2>&1
echo
rm -f "$PAYLOAD_FILE"
