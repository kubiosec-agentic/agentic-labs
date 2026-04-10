"""
Exercise 1: Simple agent using OpenAI as the LLM backend.

This is the simplest possible Microsoft Agent Framework example.
It uses OpenAIChatClient, which talks directly to the OpenAI API
(not Azure). Compare with MAF_02_azure_agent.py to see what changes
when you move to Azure.

Prerequisites:
    export OPENAI_API_KEY="sk-..."

Run:
    python3 MAF_01_openai_agent.py
"""

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient


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
    # OpenAIChatClient reads OPENAI_API_KEY from the environment.
    # model_id defaults to gpt-4o; override with OPENAI_CHAT_MODEL_ID
    # or pass model_id="gpt-4o-mini" here.
    client = OpenAIChatClient()

    agent = client.create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather assistant.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle and Brussels?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())
