"""
Exercise 2: OpenAI Agents SDK with governance guardrails.

Wraps async tool functions with a governance guard that enforces an
allowlist, a blocklist, and content pattern matching. Three scenarios
demonstrate the enforcement:

  1. A tool NOT in the allowlist is blocked.
  2. An allowed tool called with dangerous content is blocked.
  3. An allowed tool called with safe content succeeds.

No actual LLM call is made; this focuses on the governance layer.

Run:
    python3 govern_02.py
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from agent_os.integrations.openai_agents_sdk import (
    GovernancePolicy,
    OpenAIAgentsKernel,
    PolicyViolationError,
)

# --- 1. Define a governance policy ---
policy = GovernancePolicy(
    allowed_tools=["file_search", "code_interpreter"],   # explicit allowlist
    blocked_tools=["shell_exec", "network_request"],     # explicit blocklist
    blocked_patterns=["DROP TABLE", "rm -rf"],           # ban dangerous strings
    max_tool_calls=10,
)

kernel = OpenAIAgentsKernel(policy=policy, on_violation=lambda _e: None)
guard = kernel.create_tool_guard()
audit: list[dict] = []

print("=" * 60)
print("  OpenAI Agents SDK: governance guardrails")
print("=" * 60)


async def main() -> None:

    # --- 2. Blocked: tool not in allowlist ---
    print("\n[1] Calling 'web_search' (not in allowlist) ...")

    @guard
    async def web_search(query: str) -> str:
        return f"results for {query}"

    try:
        await web_search("AI governance news")
    except PolicyViolationError as exc:
        print(f"    BLOCKED: {exc}")
        audit.append({"ts": datetime.now().isoformat(),
                       "tool": "web_search", "status": "BLOCKED"})

    # --- 3. Blocked: dangerous content in argument ---
    print("\n[2] Calling 'code_interpreter' with dangerous argument ...")

    @guard
    async def code_interpreter(code: str) -> str:
        return "executed"

    try:
        await code_interpreter("import os; os.system('rm -rf /')")
    except PolicyViolationError as exc:
        print(f"    BLOCKED: {exc}")
        audit.append({"ts": datetime.now().isoformat(),
                       "tool": "code_interpreter", "status": "BLOCKED"})

    # --- 4. Allowed: compliant tool call ---
    print("\n[3] Calling 'file_search' with safe content ...")

    @guard
    async def file_search(query: str) -> list[str]:
        return ["Q4_report.pdf", "annual_summary.pdf"]

    result = await file_search("Find Q4 financial reports")
    print(f"    ALLOWED: guardrails passed, found: {result}")
    audit.append({"ts": datetime.now().isoformat(),
                   "tool": "file_search", "status": "ALLOWED"})

    # --- 5. Audit trail ---
    print("\n-- Audit Trail " + "-" * 44)
    for i, entry in enumerate(audit, 1):
        print(f"  [{i}] {entry['ts']}  tool={entry['tool']!r}  "
              f"status={entry['status']}")
    print()


asyncio.run(main())
