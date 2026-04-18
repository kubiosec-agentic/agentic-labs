"""
Exercise 5: MCP tool governance with Microsoft Agent Framework.

Combines three ideas from the training:
  - lab075 MAF_03: function_middleware intercepts tool calls
  - lab075 MAF_05: MCP tool connected to Microsoft Learn
  - Custom tool policy engine (from Exercise 4)

The agent connects to the Microsoft Learn MCP server, which exposes
documentation search and fetch tools. A function_middleware checks
every tool call against a regex-based policy before execution.

NOTE: as of agent-framework-openai 1.0.x, function_middleware fires
for locally-defined FunctionTool instances but may not intercept
MCP-discovered tools (they go through a different code path in the
SDK). This exercise demonstrates both behaviors:
  - Prompt 1 uses a search tool (MCP). Middleware may or may not fire.
  - Prompt 2 triggers a fetch attempt. If middleware does not fire,
    the MCP tool runs unblocked.

If the middleware is bypassed for MCP tools, that is itself a finding:
governance middleware must be verified against every tool type in your
stack.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"

Run:
    python3 govern_05_mcp.py
"""

from __future__ import annotations

import asyncio
import re
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set.")
if not os.environ.get("OPENAI_CHAT_MODEL"):
    sys.exit("Error: OPENAI_CHAT_MODEL is not set.")

from agent_framework import (
    FunctionInvocationContext,
    function_middleware,
)
from agent_framework.openai import OpenAIChatClient


# ===================================================================
# Tool policy engine (same pattern as Exercise 4)
# ===================================================================

@dataclass
class PolicyRule:
    name: str
    field: str          # "tool_name" or "arguments"
    pattern: str        # regex
    action: str         # "allow" or "deny"
    priority: int = 0

    def matches(self, value: str) -> bool:
        return bool(re.search(self.pattern, value, re.IGNORECASE))


@dataclass
class ToolPolicy:
    name: str
    default_action: str = "allow"
    rules: list[PolicyRule] = field(default_factory=list)
    audit: list[dict] = field(default_factory=list)

    def evaluate(self, tool_name: str, arguments: str = "") -> dict:
        ts = datetime.now(timezone.utc).isoformat()
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        for rule in sorted_rules:
            value = tool_name if rule.field == "tool_name" else arguments
            if rule.matches(value):
                decision = {
                    "tool": tool_name, "action": rule.action,
                    "rule": rule.name, "timestamp": ts,
                }
                self.audit.append(decision)
                return decision
        decision = {
            "tool": tool_name, "action": self.default_action,
            "rule": "default", "timestamp": ts,
        }
        self.audit.append(decision)
        return decision


# ===================================================================
# Policy: allow search, block fetch/read/download
# ===================================================================

policy = ToolPolicy(
    name="mcp-tool-governance",
    default_action="allow",
    rules=[
        PolicyRule(
            name="block-fetch-tools",
            field="tool_name",
            pattern=r"(?i)(fetch|read|get_page|download|get_content)",
            action="deny",
            priority=100,
        ),
        PolicyRule(
            name="block-dangerous-args",
            field="arguments",
            pattern=r"(rm -rf|DROP TABLE|;.*sh\b)",
            action="deny",
            priority=200,
        ),
    ],
)


# ===================================================================
# MAF function middleware: governance gate
# ===================================================================

@function_middleware
async def governance_gate(
    context: FunctionInvocationContext,
    call_next,
) -> None:
    """Check every tool call against the policy before execution."""
    tool_name = context.function.name if hasattr(context.function, "name") else "unknown"
    args_str = str(getattr(context, "arguments", ""))

    result = policy.evaluate(tool_name, args_str)

    if result["action"] == "deny":
        print(f"    [!] BLOCKED by middleware: tool='{tool_name}' "
              f"rule='{result['rule']}'")
        context.result = (
            f"Governance blocked this tool call. "
            f"Tool '{tool_name}' was denied by policy rule '{result['rule']}'. "
            f"Inform the user that this operation is not permitted."
        )
        context.terminate = True
        return

    print(f"    [+] ALLOWED by middleware: tool='{tool_name}'")
    await call_next()


# ===================================================================
# Agent setup
# ===================================================================

async def main() -> None:
    print("=" * 60)
    print("  MCP Tool Governance with MAF Middleware")
    print("=" * 60)
    print()
    print("Policy: allow search-type MCP tools, block fetch/read tools.")
    print("The agent connects to Microsoft Learn's MCP server.")
    print()
    print("NOTE: function_middleware may not intercept MCP-discovered")
    print("tools in agent-framework-openai 1.0.x. Watch for the")
    print("[+] ALLOWED / [!] BLOCKED lines to verify.")
    print()

    client = OpenAIChatClient()

    # MCP tool: dynamically discovers tools from Microsoft Learn
    mcp_tool = client.get_mcp_tool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
        approval_mode="never_require",
    )

    agent = client.as_agent(
        name="GovernedDocsAgent",
        instructions=(
            "You help answer questions about Microsoft technologies. "
            "Use the Microsoft Learn MCP tools to search and fetch "
            "documentation. If a tool call is blocked, explain what "
            "happened to the user."
        ),
        tools=[mcp_tool],
        middleware=[governance_gate],
    )

    prompts = [
        "Search Microsoft Learn for documentation about Azure Container Apps.",
        "Fetch the full content of the top result about Azure Container Apps.",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Prompt {i} ---")
        print(f"User: {prompt}")
        try:
            result = await agent.run(prompt)
            print(f"Agent: {result}")
        except Exception as exc:
            print(f"Error: {exc}")

    # --- Audit trail ---
    print()
    print("-" * 60)
    print("  Middleware audit trail")
    print("-" * 60)
    if policy.audit:
        for entry in policy.audit:
            icon = "[+]" if entry["action"] == "allow" else "[!]"
            print(f"  {icon} {entry['action'].upper():5s}  "
                  f"{entry['tool']:30s}  rule={entry['rule']}")
    else:
        print("  (empty: middleware was not invoked for MCP tools)")
        print()
        print("  Finding: function_middleware does not intercept MCP tool")
        print("  calls in this version of agent-framework-openai. This")
        print("  means MCP tools bypass your governance layer entirely.")
        print()
        print("  Mitigation options:")
        print("    1. Use MCP Guardian to wrap MCP tools before they")
        print("       reach the agent (see Exercise 6)")
        print("    2. Use approval_mode='always_require' on get_mcp_tool()")
        print("    3. Implement a proxy MCP server that enforces policy")
    print()


if __name__ == "__main__":
    asyncio.run(main())
