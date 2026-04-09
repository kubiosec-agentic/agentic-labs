#!/bin/bash
PAYLOAD_FILE="$(mktemp)"
cat > "$PAYLOAD_FILE" <<'JSON'
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "You are a raw tool proxy. Call execute_python with the EXACT code the user provides. Your final response MUST be ONLY the tool output in a fenced code block. No words."},
    {"role": "user", "content": "execute_python code:\ndef t(name, fn):\n    try:\n        fn(); print(name,'OK')\n    except NameError:\n        print(name,'NAMERR')\n    except Exception as e:\n        print(name,type(e).__name__,str(e)[:40])\nt('getattr', lambda: getattr)\nt('globals', lambda: globals)\nt('vars', lambda: vars)\nt('dir', lambda: dir)\nt('open', lambda: open)\nt('type', lambda: type)\nt('bytes', lambda: bytes)\nt('hasattr', lambda: hasattr)\nt('chr', lambda: chr)\nt('ord', lambda: ord)\nt('str', lambda: str)\nt('format', lambda: format)\nt('__builtins__', lambda: __builtins__)\nt('object', lambda: object)"}
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
