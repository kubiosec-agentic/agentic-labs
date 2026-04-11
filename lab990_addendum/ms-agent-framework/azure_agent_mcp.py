# Copyright (c) Microsoft. All rights reserved.
# Updated to Microsoft Agent Framework 1.0 GA API
#
# Key changes from pre-1.0:
#   - ChatAgent removed; use Agent from agent_framework
#   - chat_client= parameter renamed to client=
#   - AzureAIAgentClient removed; use FoundryChatClient from agent_framework.foundry
#   - HostedWebSearchTool removed; use client.get_web_search_tool() instead
#   - Package: pip install agent-framework-foundry azure-identity

"""
Azure Foundry Agent with MCP Example

This sample shows how to connect an Agent Framework agent to an
HTTP-based MCP (Model Context Protocol) server. The agent can
dynamically discover and invoke tools exposed by the MCP server.

Prerequisites:
    az login
    export FOUNDRY_PROJECT_ENDPOINT="https://<project>.services.ai.azure.com"
    export FOUNDRY_MODEL="gpt-4o"

Run:
    python3 azure_agent_mcp.py
"""

import asyncio
import os
import sys

if not os.environ.get("FOUNDRY_PROJECT_ENDPOINT"):
    sys.exit(
        "Error: FOUNDRY_PROJECT_ENDPOINT is not set.\n"
        "Run: export FOUNDRY_PROJECT_ENDPOINT=\"https://<project>.services.ai.azure.com\""
    )

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def http_mcp_example():
    """Example using an HTTP-based MCP server."""
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
        credential=AzureCliCredential(),
    )

    async with MCPStreamableHTTPTool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
    ) as mcp_server:
        agent = Agent(
            client=client,
            name="DocsAgent",
            instructions="You help with Microsoft documentation questions.",
            tools=[mcp_server],
            # To add hosted web search alongside MCP tools:
            # tools=[mcp_server, client.get_web_search_tool()],
        )

        result = await agent.run(
            "How to run the dev ui in the microsoft agent framework for a python app?"
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(http_mcp_example())
