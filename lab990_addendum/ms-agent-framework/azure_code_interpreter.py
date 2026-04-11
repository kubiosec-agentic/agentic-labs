# Copyright (c) Microsoft. All rights reserved.
# Updated to Microsoft Agent Framework 1.0 GA API
#
# Key changes from pre-1.0:
#   - AzureAIAgentClient removed; use FoundryChatClient from agent_framework.foundry
#   - HostedCodeInterpreterTool removed; use client.get_code_interpreter_tool()
#   - create_agent() removed; use Agent(client=...) directly
#   - AgentRunResponse.from_agent_response_generator() -> AgentResponse.from_updates()
#   - Package: pip install agent-framework-foundry azure-identity

"""
Azure AI Foundry Agent with Code Interpreter Example

This sample demonstrates using the code interpreter tool with a Foundry
agent for Python code execution and mathematical problem solving.

Prerequisites:
    az login
    export FOUNDRY_PROJECT_ENDPOINT="https://<project>.services.ai.azure.com"
    export FOUNDRY_MODEL="gpt-4o"

Run:
    python3 azure_code_interpreter.py
"""

import asyncio
import os
import sys

if not os.environ.get("FOUNDRY_PROJECT_ENDPOINT"):
    sys.exit(
        "Error: FOUNDRY_PROJECT_ENDPOINT is not set.\n"
        "Run: export FOUNDRY_PROJECT_ENDPOINT=\"https://<project>.services.ai.azure.com\""
    )

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main() -> None:
    """Example showing how to use the code interpreter tool with Foundry."""
    print("=== Azure AI Foundry Agent with Code Interpreter Example ===")

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
        credential=AzureCliCredential(),
    )

    # In 1.0 GA, hosted tools are obtained from the client instead of
    # standalone classes (HostedCodeInterpreterTool was removed).
    code_interpreter = client.get_code_interpreter_tool()

    agent = Agent(
        client=client,
        name="CodingAgent",
        instructions=(
            "You are a helpful assistant that can write and execute "
            "Python code to solve problems."
        ),
        tools=[code_interpreter],
    )

    query = "Generate the factorial of 100 using python code, show the code and execute it."
    print(f"User: {query}")

    # Non-streaming: get the complete response at once
    result = await agent.run(query)
    print(f"Agent: {result}")

    # To inspect code interpreter outputs, iterate over messages and
    # look for content with type "code_interpreter_tool_call" or
    # "code_interpreter_tool_result":
    for message in result.messages:
        for content in message.contents:
            if content.type == "code_interpreter_tool_call":
                print(f"\nCode Input:\n{content.text}")
            elif content.type == "code_interpreter_tool_result":
                print(f"\nCode Output:\n{content.text}")


if __name__ == "__main__":
    asyncio.run(main())
