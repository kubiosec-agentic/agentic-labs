"""
Exercise 5: Agent with a hosted MCP tool (OpenAI Responses API).

This exercise connects the agent to the Microsoft Learn MCP server
using the framework's hosted MCP support. The agent can then query
Microsoft documentation to answer questions.

Hosted MCP means the MCP connection is managed server-side by
OpenAI's Responses API, not locally. The framework exposes this
through client.get_mcp_tool().

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"

Run:
    python3 MAF_05_mcp_agent.py
"""

import asyncio
import os
import sys

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")
if not os.environ.get("OPENAI_CHAT_MODEL"):
    sys.exit("Error: OPENAI_CHAT_MODEL is not set. Run: export OPENAI_CHAT_MODEL=\"gpt-4o-mini\"")

from agent_framework.openai import OpenAIChatClient


async def main() -> None:
    print("=== MCP Agent Example (Microsoft Learn) ===\n")

    # OpenAIChatClient uses the Responses API which supports hosted
    # MCP tools. The MCP connection runs server-side at OpenAI; the
    # agent discovers available tools from the MCP server automatically.
    client = OpenAIChatClient()

    mcp_tool = client.get_mcp_tool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
        approval_mode="never_require",
    )

    agent = client.as_agent(
        name="DocsAgent",
        instructions=(
            "You help answer questions about Microsoft technologies. "
            "Use the Microsoft Learn MCP tool to search documentation "
            "before answering."
        ),
        tools=[mcp_tool],
    )

    query = "How do I create a middleware in the Microsoft Agent Framework for Python?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}\n")

    # Streaming follow-up
    query2 = "Show me an example of function middleware that blocks specific tool calls."
    print(f"User: {query2}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run(query2, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
