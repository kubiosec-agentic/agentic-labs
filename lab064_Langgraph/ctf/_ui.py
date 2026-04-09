"""Shared browser UI for the CTF stages.

Each stage imports `render_ui` and mounts it at GET `/`. The UI is a single
self-contained HTML page (no build step, no static files) that talks to the
same `/v1/chat/completions` endpoint the CLI/curl examples use. It supports
both session modes:

- Stateful: sends `X-Session-Id` header, server keeps history via MemorySaver.
- Stateless: sends the full message history on every request (classic OpenAI).

The UI is intentionally plain. This is a security lab, not a product.
"""

from __future__ import annotations


_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CTF Stage {stage} - {title}</title>
<style>
  :root {{
    --bg: #0f1115;
    --panel: #1a1d24;
    --border: #2a2f3a;
    --text: #e6e8ee;
    --muted: #8a92a6;
    --user: #2d5fb0;
    --assistant: #2a2f3a;
    --error: #7a1f1f;
    --accent: #f0a020;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    flex-direction: column;
    height: 100vh;
  }}
  header {{
    background: var(--panel);
    border-bottom: 2px solid var(--accent);
    padding: 12px 20px;
  }}
  header h1 {{
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }}
  header .meta {{
    font-size: 12px;
    color: var(--muted);
    margin-top: 4px;
  }}
  header .meta code {{
    color: var(--accent);
  }}
  .controls {{
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 10px 20px;
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
    font-size: 12px;
  }}
  .controls label {{
    color: var(--muted);
  }}
  .controls input[type=text] {{
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 4px 8px;
    font-family: monospace;
    font-size: 12px;
    width: 220px;
  }}
  .controls button {{
    background: var(--border);
    color: var(--text);
    border: none;
    border-radius: 4px;
    padding: 4px 10px;
    cursor: pointer;
    font-size: 12px;
  }}
  .controls button:hover {{ background: #3a3f4a; }}
  #chat {{
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .msg {{
    max-width: 80%;
    padding: 10px 14px;
    border-radius: 10px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 14px;
    line-height: 1.4;
  }}
  .msg.user {{
    background: var(--user);
    align-self: flex-end;
  }}
  .msg.assistant {{
    background: var(--assistant);
    align-self: flex-start;
    border: 1px solid var(--border);
  }}
  .msg.error {{
    background: var(--error);
    align-self: flex-start;
  }}
  .msg .role {{
    font-size: 10px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
    letter-spacing: 0.5px;
  }}
  footer {{
    background: var(--panel);
    border-top: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    gap: 10px;
  }}
  footer textarea {{
    flex: 1;
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    font-family: inherit;
    font-size: 14px;
    resize: none;
    height: 60px;
  }}
  footer button {{
    background: var(--accent);
    color: #111;
    border: none;
    border-radius: 6px;
    padding: 0 20px;
    font-weight: 600;
    cursor: pointer;
  }}
  footer button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
</style>
</head>
<body>
<header>
  <h1>CTF Stage {stage}: {title}</h1>
  <div class="meta">Guardrails: <code>{guardrails}</code> &middot; Endpoint: <code>/v1/chat/completions</code></div>
</header>
<div class="controls">
  <label>Session ID: <input type="text" id="sessionId" value=""></label>
  <label><input type="checkbox" id="stateful" checked> Stateful (server-side memory)</label>
  <button id="newSession">New session</button>
  <button id="clear">Clear view</button>
</div>
<div id="chat"></div>
<footer>
  <textarea id="input" placeholder="Ask the agent... (Enter to send, Shift+Enter for newline)"></textarea>
  <button id="send">Send</button>
</footer>
<script>
  const chatEl = document.getElementById('chat');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('send');
  const sessionEl = document.getElementById('sessionId');
  const statefulEl = document.getElementById('stateful');
  const clearBtn = document.getElementById('clear');
  const newSessionBtn = document.getElementById('newSession');

  // Client-side history for stateless mode
  let history = [];

  function randomId() {{
    return 'ui-' + Math.random().toString(36).slice(2, 10);
  }}
  sessionEl.value = randomId();

  function addMsg(role, content) {{
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    const roleDiv = document.createElement('div');
    roleDiv.className = 'role';
    roleDiv.textContent = role;
    const body = document.createElement('div');
    body.textContent = content;
    div.appendChild(roleDiv);
    div.appendChild(body);
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
  }}

  async function send() {{
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = '';
    addMsg('user', text);
    sendBtn.disabled = true;

    const stateful = statefulEl.checked;
    const headers = {{ 'Content-Type': 'application/json' }};
    let messages;
    if (stateful) {{
      headers['X-Session-Id'] = sessionEl.value || 'default';
      messages = [{{ role: 'user', content: text }}];
    }} else {{
      history.push({{ role: 'user', content: text }});
      messages = history.slice();
    }}

    try {{
      const res = await fetch('/v1/chat/completions', {{
        method: 'POST',
        headers: headers,
        body: JSON.stringify({{ model: 'ctf-agent', messages: messages }}),
      }});
      const data = await res.json();
      if (data.error) {{
        addMsg('error', data.error.message || JSON.stringify(data.error));
      }} else {{
        const content = data.choices[0].message.content;
        addMsg('assistant', content);
        if (!stateful) {{
          history.push({{ role: 'assistant', content: content }});
        }}
      }}
    }} catch (e) {{
      addMsg('error', 'Request failed: ' + e.message);
    }} finally {{
      sendBtn.disabled = false;
      inputEl.focus();
    }}
  }}

  sendBtn.addEventListener('click', send);
  inputEl.addEventListener('keydown', (e) => {{
    if (e.key === 'Enter' && !e.shiftKey) {{
      e.preventDefault();
      send();
    }}
  }});
  clearBtn.addEventListener('click', () => {{
    chatEl.innerHTML = '';
    history = [];
  }});
  newSessionBtn.addEventListener('click', () => {{
    sessionEl.value = randomId();
    chatEl.innerHTML = '';
    history = [];
  }});
  inputEl.focus();
</script>
</body>
</html>
"""


def render_ui(stage: int, title: str, guardrails: str) -> str:
    """Return the full HTML page for the given CTF stage."""
    return _HTML_TEMPLATE.format(stage=stage, title=title, guardrails=guardrails)
