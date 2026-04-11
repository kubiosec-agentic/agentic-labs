# Copyright (c) Microsoft. All rights reserved.
# Updated to Microsoft Agent Framework 1.0 GA API

import asyncio
import os
import sys
from random import randint
from typing import Annotated

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")

from agent_framework.openai import OpenAIChatClient


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}C."


async def main() -> None:
    # OpenAIChatClient reads OPENAI_API_KEY and OPENAI_CHAT_MODEL from env.
    # .as_agent() is the 1.0 GA way to create a runnable agent from a client.
    agent = OpenAIChatClient().as_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )
    result = await agent.run("What's the weather like in Seattle?")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
