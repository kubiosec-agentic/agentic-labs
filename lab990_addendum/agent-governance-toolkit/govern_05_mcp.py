"""
Exercise 5: MCP tool governance with Microsoft Agent Framework.

Combines three ideas from the training:
  - lab075 MAF_03: function_middleware intercepts tool calls
  - lab075 MAF_05: MCP tool connected to Microsoft Learn
  - AGT: deterministic policy evaluation

The agent connects to the Microsoft Learn MCP server, which exposes
documentation search and fetch tools. A function middleware powered by
AGT's PolicyEvaluator checks every tool call (including MCP-discovered
ones) against a policy before execution.

The policy allows search-type operations but blocks fetch/read
operations, demonstrating governance over dynamically discovered MCP
tools.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"

Run:
    python3 govern_05_mcp.py
"""

from __future__ import annotations

import asyncio
import os
import sys

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set.")
if not os.environ.get("OPENAI_CHAT_MODEL"):
    sys.exit("Error: OPENAI_CHAT_MODEL is not set.")

from agent_framework import (
    FunctionInvocationContext,
    function_middleware,
)
from agent_framework.openai import OpenAIChatClient

from agent_os.policies import (
    PolicyEvaluator,
    PolicyDocument,
    PolicyRule,
    PolicyCondition,
    PolicyAction,
    PolicyOperator,
    PolicyDefaults,
)


# --- AGT policy: allow search, block fetch ---

evaluator = PolicyEvaluator(policies=[PolicyDocument(
    name="mcp-tool-governance",
    version="1.0",
    defaults=PolicyDefaults(action=PolicyAction.ALLOW),
    rules=[
        PolicyRule(
            name="block-fetch-tools",
            description="Block MCP tools that retrieve full document content",
            condition=PolicyCondition(
                field="tool_name",
                operator=PolicyOperator.MATCHES,
                value=r"(?i)(fetch|read|get_page|download)",
            ),
            action=PolicyAction.DENY,
            priority=100,
        ),
        PolicyRule(
            name="block-dangerous-patterns",
            description="Block calls with shell injection patterns",
            condition=PolicyCondition(
                field="arguments",
                operator=PolicyOperator.MATCHES,
                value=r"(rm -rf|DROP TABLE|;.*sh\b)",
            ),
            action=PolicyAction.DENY,
            priority=200,
        ),
    ],
)])


# --- Function middleware: governance gate for all tool calls ---

@function_middleware
async def governance_gate(
    context: FunctionInvocationContext,
    call_next,
) -> None:
    """Check every tool call against AGT policy before execution."""
    tool_name = context.function.name if hasattr(context.function, "name") else "unknown"
    args_str = str(getattr(context, "arguments", ""))

    result = evaluator.evaluate({
        "tool_name": tool_name,
        "arguments": args_str,
    })

    if result.action == PolicyAction.DENY:
        rule = result.matched_rule.name if result.matched_rule else "policy"
        print(f"    [!] BLOCKED by AGT: tool='{tool_name}' rule='{rule}'")
        context.result = (
            f"Governance blocked this tool call. "
            f"Tool '{tool_name}' was denied by policy rule '{rule}'. "
            f"Inform the user that this operation is not permitted."
        )
        context.terminate = True
        return

    print(f"    [+] ALLOWED by AGT: tool='{tool_name}'")
    await call_next()


# --- Agent setup ---

async def main() -> None:
    print("=" * 60)
    print("  MCP Tool Governance with AGT")
    print("=" * 60)
    print()
    print("Policy: allow search-type MCP tools, block fetch/read tools.")
    print("The agent connects to Microsoft Learn's MCP server.")
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

    # Prompt 1: should trigger a search tool (allowed)
    prompts = [
        "Search Microsoft Learn for documentation about Azure Container Apps.",
        "Fetch the full content of the top result.",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Prompt {i} ---")
        print(f"User: {prompt}")
        try:
            result = await agent.run(prompt)
            print(f"Agent: {result}")
        except Exception as exc:
            print(f"Error: {exc}")

    print()


if __name__ == "__main__":
    asyncio.run(main())
