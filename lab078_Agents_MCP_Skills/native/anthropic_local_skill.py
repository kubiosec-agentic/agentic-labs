"""
Exercise 4c: a LOCAL skill with Anthropic (nothing uploaded).

4b uploads the skill and runs it in Anthropic's sandbox. But the Anthropic
Messages API has no built-in "use a skill folder on my disk" option, the same
gap the OpenAI Agents SDK has. So the way to run a local skill with Claude is
the same move as Exercises 1 to 3: hand-roll the loader on the plain Messages
API. The SKILL.md folder stays on your machine, the scripts run on your
machine (subprocess), and Claude just drives the loop through tool calls.

Contrast:
  4b  anthropic_skill_example.py   uploaded, runs in Anthropic's sandbox (code exec)
  4c  this file                    local folder, runs on your machine, hand-rolled loop

This reuses the exact same loader logic as the OpenAI agents (skills_runtime),
just wired to Anthropic's tool-use loop instead of the Agents SDK.

Requirements:
  pip install anthropic
  export ANTHROPIC_API_KEY=...
  export ANTHROPIC_MODEL=<a current Claude model>   # docs model literals move; do not hardcode
"""

import json
import os
import sys
from pathlib import Path

# Reuse the local skill loader from the lab's runtime. These are plain helpers;
# only the OpenAI-specific @function_tool wrappers live in skills_runtime, and
# we re-implement the three handlers here against the same _safe/paths.
sys.path.insert(0, str(Path(__file__).parent.parent))
import skills_runtime as sr  # noqa: E402


# --- plain handlers (same logic as skills_runtime, without the OpenAI wrapper) ---
def _read_skill(skill: str) -> str:
    md = sr._safe(skill, "SKILL.md")
    return md.read_text(encoding="utf-8") if md.is_file() else f"error: no SKILL.md for {skill}"


def _read_reference(skill: str, path: str) -> str:
    try:
        ref = sr._safe(skill, "references", path)
    except ValueError as e:
        return f"error: {e}"
    return ref.read_text(encoding="utf-8") if ref.is_file() else f"error: reference not found: {path}"


def _run_skill_script(skill: str, script: str, stdin_text: str = "") -> str:
    import subprocess
    try:
        p = sr._safe(skill, script)
    except ValueError as e:
        return f"error: {e}"
    if not p.is_file():
        return f"error: script not found: {script}"
    r = subprocess.run([sys.executable, str(p)], input=stdin_text, capture_output=True, text=True, timeout=30)
    out = r.stdout + (f"\n[exit {r.returncode}]\n{r.stderr}" if r.returncode else "")
    return out.strip() or "(no output)"


HANDLERS = {"read_skill": _read_skill, "read_reference": _read_reference, "run_skill_script": _run_skill_script}

# Anthropic tool schemas (the same three tools, described for Claude).
TOOLS = [
    {
        "name": "read_skill",
        "description": "Read the full SKILL.md instructions for a skill directory (e.g. 'http-header-audit').",
        "input_schema": {"type": "object", "properties": {"skill": {"type": "string"}}, "required": ["skill"]},
    },
    {
        "name": "read_reference",
        "description": "Read a reference file under skills/<skill>/references/, e.g. read_reference('http-header-audit','grading.md').",
        "input_schema": {
            "type": "object",
            "properties": {"skill": {"type": "string"}, "path": {"type": "string"}},
            "required": ["skill", "path"],
        },
    },
    {
        "name": "run_skill_script",
        "description": "Run a script under skills/<skill>/scripts/ with stdin_text on stdin, e.g. run_skill_script('http-header-audit','scripts/audit_headers.py', stdin_text=<headers JSON>).",
        "input_schema": {
            "type": "object",
            "properties": {"skill": {"type": "string"}, "script": {"type": "string"}, "stdin_text": {"type": "string"}},
            "required": ["skill", "script"],
        },
    },
]


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("export ANTHROPIC_API_KEY=... first")
    model = os.environ.get("ANTHROPIC_MODEL")
    if not model:
        sys.exit("set ANTHROPIC_MODEL to a current Claude model")

    import anthropic

    client = anthropic.Anthropic()
    system = sr.build_instructions(
        "You are an application-security assistant. When a task matches a skill, read it "
        "and follow its steps exactly, preferring the skill's script over your own judgement."
    )
    print("Skills on the menu:", [s["dir"] for s in sr.discover_skills()])

    messages = [{
        "role": "user",
        "content": (
            "Audit the HTTP security headers below with the http-header-audit skill, then give the "
            "letter grade and the two weakest headers. "
            'Headers: {"Strict-Transport-Security":"max-age=0",'
            '"Content-Security-Policy":"default-src \'self\'; script-src \'unsafe-inline\'",'
            '"Server":"nginx/1.18.0"}'
        ),
    }]

    # Manual tool-use loop: call the model, run any tool_use blocks locally,
    # feed tool_result back, repeat until the model stops asking for tools.
    for _ in range(10):
        resp = client.messages.create(model=model, max_tokens=2048, system=system, tools=TOOLS, messages=messages)
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        for b in resp.content:
            if getattr(b, "type", None) == "text" and b.text.strip():
                print(f"  [claude] {b.text.strip()[:500]}")
        if resp.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            out = HANDLERS[tu.name](**tu.input)
            first = out.splitlines()[0] if out else ""
            print(f"  [tool] {tu.name}({json.dumps(tu.input)[:120]}) -> {first[:120]}")
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out})
        messages.append({"role": "user", "content": results})

    print(
        "\nThe skill folder never left your machine and the grader ran here via subprocess. "
        "Same local loader as Exercises 1-3, driven by Claude's tool loop instead of the "
        "OpenAI Agents SDK. Compare 4b, where the same folder was uploaded and run in "
        "Anthropic's sandbox."
    )


if __name__ == "__main__":
    main()
