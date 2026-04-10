"""
Example 3: Agent with Microsoft Learn MCP (streamable HTTP).

Connects to the Microsoft Learn documentation MCP server and uses it
to answer questions about Microsoft technologies. Demonstrates how
FastAgent integrates with remote MCP servers over streamable HTTP.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("MS Learn Docs Agent")


@fast.agent(
    instruction=(
        "You help answer questions about Microsoft technologies. "
        "Use the Microsoft Learn MCP tool to search documentation "
        "before answering."
    ),
    servers=["mslearn"],
)
async def main():
    async with fast.run() as agent:
        await agent(
            "How do I create a middleware in the Microsoft Agent Framework for Python?"
        )


if __name__ == "__main__":
    asyncio.run(main())
