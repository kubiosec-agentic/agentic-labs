"""
Shared helpers for lab066. Nothing here is Deep Agents specific; it is just
the model factory and a printer so the exercise scripts stay short.
"""

import os
import sys

from langchain.chat_models import init_chat_model

# Model-agnostic on purpose: any "provider:model" string init_chat_model()
# understands works here. Override with DA_MODEL, e.g.
#   DA_MODEL="openai:gpt-4o" python3 da_01_harness.py
DEFAULT_MODEL = os.environ.get("DA_MODEL", "openai:gpt-4o-mini")

# FilesystemPermission patterns are matched with wcmatch WITHOUT the DOTGLOB
# flag, so "/**" does not match dotfiles: a rule on "/**" leaves /.env,
# /.git/config and friends untouched (deepagents 0.7.14, verified in
# Exercise 4). To really mean "everything", use all three.
EVERYTHING = ["/**", "/**/.*", "/**/.*/**"]


def get_model(model: str | None = None):
    """Return a chat model. With an openai: prefix deepagents uses the
    Responses API by default; use_responses_api=False forces Chat Completions
    so the wire traffic matches what you saw in lab010/lab032."""
    name = model or DEFAULT_MODEL
    if name.startswith("openai:"):
        return init_chat_model(name, use_responses_api=False)
    return init_chat_model(name)


def require_key():
    if not os.environ.get("OPENAI_API_KEY") and DEFAULT_MODEL.startswith("openai:"):
        sys.exit("export OPENAI_API_KEY=... first (or set DA_MODEL to another provider)")


def print_stream(stream):
    """Print every tool call and every AI message as the agent runs.

    stream is the iterator returned by agent.stream(..., stream_mode="updates").
    Each update is {node_name: {"messages": [...]}}; we only care about the
    messages. Sub-agent runs are nested and show up as one 'task' tool call
    from the parent's point of view."""
    for update in stream:
        for node, payload in update.items():
            if not isinstance(payload, dict):
                continue
            for msg in payload.get("messages", []) or []:
                mtype = getattr(msg, "type", "")
                if mtype == "ai":
                    for tc in getattr(msg, "tool_calls", []) or []:
                        args = str(tc.get("args"))
                        print(f"  [{node}] tool call -> {tc['name']}({args[:160]}{'...' if len(args) > 160 else ''})")
                    if msg.content:
                        text = msg.content if isinstance(msg.content, str) else str(msg.content)
                        print(f"  [{node}] AI: {text[:800]}")
                elif mtype == "tool":
                    text = msg.content if isinstance(msg.content, str) else str(msg.content)
                    first = text.strip().splitlines()[0] if text.strip() else ""
                    print(f"  [{node}] tool result ({getattr(msg, 'name', '?')}): {first[:160]}")


def final_answer(result) -> str:
    msgs = result.get("messages", [])
    for m in reversed(msgs):
        if getattr(m, "type", "") == "ai" and m.content:
            return m.content if isinstance(m.content, str) else str(m.content)
    return "(no AI message)"


def trace_prompt(label: str = "model request"):
    """Middleware that prints the assembled system prompt of the FIRST model
    call, so you can see what the harness injected (skills index, memory,
    tool instructions). Enabled with DA_TRACE=1. For the full wire view use
    mitmproxy like in lab050/lab070."""
    from langchain.agents.middleware import wrap_model_call

    seen = {"done": False}

    @wrap_model_call(name="TracePrompt")
    def _trace(request, handler):
        if os.environ.get("DA_TRACE") and not seen["done"]:
            seen["done"] = True
            sm = request.system_message
            content = sm.content if sm is not None else ""
            if isinstance(content, list):
                content = "\n".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
            print(f"\n----- system prompt ({label}, {len(content)} chars) -----")
            print(content)
            print("----- end system prompt -----\n")
        return handler(request)

    return _trace
