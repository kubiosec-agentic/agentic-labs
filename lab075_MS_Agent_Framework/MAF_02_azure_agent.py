"""
Exercise 2: The same agent, but using Azure OpenAI as the backend.

This file is the Azure counterpart of MAF_01_openai_agent.py. The
business logic (tools, instructions, query) is identical. The only
differences are:

  1. Auth:   API key via AZURE_OPENAI_API_KEY instead of OPENAI_API_KEY.
  2. Env:    AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_CHAT_MODEL
             instead of OPENAI_API_KEY + OPENAI_CHAT_MODEL.

Compare the two files side-by-side to see exactly what changes when
moving from OpenAI to Azure.

Prerequisites:
    export AZURE_OPENAI_API_KEY="<your-azure-api-key>"
    export AZURE_OPENAI_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"
    export AZURE_OPENAI_CHAT_MODEL="gpt-5-nano"

Run:
    python3 MAF_02_azure_agent.py
"""

import asyncio
import os
import sys
from random import randint
from typing import Annotated

if not os.environ.get("AZURE_OPENAI_API_KEY"):
    sys.exit("Error: AZURE_OPENAI_API_KEY is not set. Run: export AZURE_OPENAI_API_KEY=\"<key>\"")
if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
    sys.exit("Error: AZURE_OPENAI_ENDPOINT is not set. Run: export AZURE_OPENAI_ENDPOINT=\"https://...\"")
if not os.environ.get("AZURE_OPENAI_CHAT_MODEL"):
    sys.exit("Error: AZURE_OPENAI_CHAT_MODEL is not set. Run: export AZURE_OPENAI_CHAT_MODEL=\"gpt-5-nano\"")

from agent_framework.openai import OpenAIChatClient


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
    # When api_key + azure_endpoint are passed, the client switches
    # to Azure mode even if OPENAI_API_KEY is also set.
    agent = OpenAIChatClient(
        model=os.environ["AZURE_OPENAI_CHAT_MODEL"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
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
