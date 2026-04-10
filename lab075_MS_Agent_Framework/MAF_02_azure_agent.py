"""
Exercise 2: The same agent, but using Azure OpenAI as the backend.

This file is the Azure counterpart of MAF_01_openai_agent.py. The
business logic (tools, instructions, query) is identical. The only
differences are:

  1. Import: AzureAIAgentClient instead of OpenAIChatClient.
  2. Auth:   AzureCliCredential (run `az login` first) instead of
             OPENAI_API_KEY.
  3. Env:    AZURE_AI_PROJECT_ENDPOINT + AZURE_AI_MODEL_DEPLOYMENT_NAME
             instead of OPENAI_API_KEY.
  4. Lifecycle: Azure agents are created server-side and automatically
             cleaned up with `async with ... as agent`.

Compare the two files side-by-side to see exactly what changes when
moving from OpenAI to Azure.

Prerequisites:
    az login
    export AZURE_AI_PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
    export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

Run:
    python3 MAF_02_azure_agent.py
"""

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field


# Same tool, same logic. The only difference: Azure uses
# pydantic Field() for parameter descriptions instead of plain
# Annotated strings. Both work, but Field() is the Azure convention.
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return (
        f"The weather in {location} is {conditions[randint(0, 3)]} "
        f"with a high of {randint(10, 30)}C."
    )


async def main() -> None:
    print("=== Azure AI Agent Example ===\n")

    # AzureAIAgentClient reads AZURE_AI_PROJECT_ENDPOINT and
    # AZURE_AI_MODEL_DEPLOYMENT_NAME from the environment.
    # The agent is created server-side and auto-deleted on exit.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="WeatherAgent",
            instructions="You are a helpful weather assistant.",
            tools=get_weather,
        ) as agent,
    ):
        # --- non-streaming ---
        query = "What's the weather like in Seattle and Brussels?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        # --- streaming ---
        query2 = "And what about Tokyo?"
        print(f"User: {query2}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(query2):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
