"""
Exercise 2: The same agent, but using Azure OpenAI as the backend.

This file is the Azure counterpart of MAF_01_openai_agent.py. The
business logic (tools, instructions, query) is identical. The only
differences are:

  1. Import: same OpenAIChatClient, but with Azure routing inputs.
  2. Auth:   AzureCliCredential (run `az login` first) instead of
             OPENAI_API_KEY.
  3. Env:    AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_CHAT_MODEL
             instead of OPENAI_API_KEY + OPENAI_CHAT_MODEL.
  4. Lifecycle: `async with` for credential cleanup.

Compare the two files side-by-side to see exactly what changes when
moving from OpenAI to Azure.

Prerequisites:
    az login
    export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com"
    export AZURE_OPENAI_CHAT_MODEL="gpt-4o"

Run:
    python3 MAF_02_azure_agent.py
"""

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient
from azure.identity.aio import AzureCliCredential


# Same tool, same logic, same annotation style.
def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return (
        f"The weather in {location} is {conditions[randint(0, 3)]} "
        f"with a high of {randint(10, 30)}C."
    )


async def main() -> None:
    print("=== Azure OpenAI Agent Example ===\n")

    # Same OpenAIChatClient, but with explicit Azure routing inputs.
    # When credential or azure_endpoint is passed, the client switches
    # to Azure mode even if OPENAI_API_KEY is also set.
    async with AzureCliCredential() as credential:
        agent = OpenAIChatClient(
            model=os.environ["AZURE_OPENAI_CHAT_MODEL"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            credential=credential,
        ).as_agent(
            name="WeatherAgent",
            instructions="You are a helpful weather assistant.",
            tools=get_weather,
        )

        # --- non-streaming ---
        query = "What's the weather like in Seattle and Brussels?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        # --- streaming ---
        query2 = "And what about Tokyo?"
        print(f"User: {query2}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run(query2, stream=True):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
