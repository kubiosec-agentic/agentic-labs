# Copyright (c) Microsoft. All rights reserved.
# Updated to Microsoft Agent Framework 1.0 GA API
#
# Key changes from pre-1.0:
#   - AzureAIAgentClient removed; use FoundryChatClient from agent_framework.foundry
#   - create_agent() context manager removed; use Agent(client=...) directly
#   - run_stream() replaced by run(stream=True)
#   - Package: pip install agent-framework-foundry azure-identity

"""
Azure AI Foundry Agent Example

This sample demonstrates using FoundryChatClient for direct model inference
through a Microsoft Foundry project endpoint. Shows both streaming and
non-streaming responses with function tools.

Prerequisites:
    az login
    export FOUNDRY_PROJECT_ENDPOINT="https://<project>.services.ai.azure.com"
    export FOUNDRY_MODEL="gpt-4o"

Run:
    python3 azure_agent.py
"""

import asyncio
import os
import sys
from random import randint
from typing import Annotated

if not os.environ.get("FOUNDRY_PROJECT_ENDPOINT"):
    sys.exit(
        "Error: FOUNDRY_PROJECT_ENDPOINT is not set.\n"
        "Run: export FOUNDRY_PROJECT_ENDPOINT=\"https://<project>.services.ai.azure.com\""
    )

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from pydantic import Field


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
        credential=AzureCliCredential(),
    )

    agent = Agent(
        client=client,
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=[get_weather],
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
        credential=AzureCliCredential(),
    )

    agent = Agent(
        client=client,
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=[get_weather],
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run(query, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Azure AI Foundry Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())
