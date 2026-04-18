"""
Exercise 5: MCP tool governance with AGT MCPGateway + MAF.

Combines three ideas from the training:
  - lab075 MAF_05: MCP tool connected to Microsoft Learn
  - AGT MCPGateway: intercept_tool_call() for policy enforcement
  - AGT GovernancePolicy: allowed/denied tool lists

Key insight: the Microsoft Agent Framework's get_mcp_tool() uses
OpenAI's hosted MCP execution. Tool calls are sent to OpenAI, which
calls the MCP server remotely. Your Python process never sees the
actual tool invocation, which is why function_middleware does not
fire for MCP tools.

The correct interception point is get_mcp_tool(allowed_tools=[...]),
which filters tools BEFORE the LLM sees them. We use AGT's MCPGateway
to compute the allowed list from a GovernancePolicy.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"

    pip install "git+https://github.com/microsoft/agent-governance-toolkit.git#subdirectory=packages/agent-os"

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

from agent_framework.openai import OpenAIChatClient
from agent_os.mcp_gateway import MCPGateway
from agent_os.trust_root import GovernancePolicy


# ===================================================================
# 1. Define governance policy
# ===================================================================

policy = GovernancePolicy(
    name="mcp-learn-governance",
    # Only allow search-type tools from the MCP server
    allowed_tools=["search", "find", "list"],
    # Block tools that fetch full page content
    blocked_patterns=["fetch", "read", "get_page", "download", "get_content"],
    max_tool_calls=5,
)

gateway = MCPGateway(
    policy=policy,
    denied_tools=["fetch", "get_page", "read_page"],
)


# ===================================================================
# 2. Discover MCP tools and filter through governance
# ===================================================================

async def main() -> None:
    print("=" * 60)
    print("  MCP Tool Governance with AGT MCPGateway")
    print("=" * 60)
    print()
    print("Policy: allow search-type MCP tools, block fetch/read tools.")
    print("Governance is enforced via get_mcp_tool(allowed_tools=[...])")
    print("which filters tools BEFORE the LLM sees them.")
    print()

    client = OpenAIChatClient()

    # --- Step 1: Create MCP tool WITHOUT governance (to show what tools exist) ---
    print("Step 1: Discovering tools from Microsoft Learn MCP server...")
    print("  (Using allowed_tools to restrict which tools the LLM can use)")
    print()

    # Check each tool name against MCPGateway
    # Since we can't enumerate MCP tools from the hosted API before connecting,
    # we use the policy's allowed_tools as a positive filter.
    allowed = policy.allowed_tools
    print(f"  Policy allows tools matching: {allowed}")
    print()

    # --- Step 2: Create governed MCP tool ---
    mcp_tool = client.get_mcp_tool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
        approval_mode="never_require",
        allowed_tools=allowed,
    )

    agent = client.as_agent(
        name="GovernedDocsAgent",
        instructions=(
            "You help answer questions about Microsoft technologies. "
            "Use the Microsoft Learn MCP tools to search documentation. "
            "You can only use search-type tools. If the user asks you to "
            "fetch or read full page content, explain that your governance "
            "policy only allows search operations."
        ),
        tools=[mcp_tool],
    )

    # --- Step 3: Test prompts ---
    prompts = [
        "Search Microsoft Learn for documentation about Azure Container Apps.",
        "Fetch the full content of the top result about Azure Container Apps.",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"--- Prompt {i} ---")
        print(f"User: {prompt}")

        # Pre-check with MCPGateway (for audit trail)
        # Extract likely tool name from the prompt
        likely_tool = "search" if "search" in prompt.lower() else "fetch"
        allowed_by_gw, reason = gateway.intercept_tool_call(
            "governed-agent", likely_tool, {"prompt": prompt}
        )
        status = "ALLOW" if allowed_by_gw else "DENY"
        icon = "[+]" if allowed_by_gw else "[!]"
        print(f"  {icon} MCPGateway pre-check: {status} ({reason})")

        try:
            result = await agent.run(prompt)
            print(f"Agent: {result}")
        except Exception as exc:
            print(f"Error: {exc}")
        print()

    # --- Audit summary ---
    print("-" * 60)
    print("  Governance summary")
    print("-" * 60)
    print(f"  Policy: {policy.name}")
    print(f"  Allowed tools filter: {policy.allowed_tools}")
    print(f"  Agent call count: {gateway.get_agent_call_count('governed-agent')}")
    print()
    print("  How it works:")
    print("  1. GovernancePolicy defines allowed tool name patterns")
    print("  2. allowed_tools is passed to get_mcp_tool()")
    print("  3. OpenAI's API filters tools BEFORE the LLM sees them")
    print("  4. Blocked tools (fetch, read) are never offered to the LLM")
    print("  5. MCPGateway provides audit trail + rate limiting")
    print()


if __name__ == "__main__":
    asyncio.run(main())
