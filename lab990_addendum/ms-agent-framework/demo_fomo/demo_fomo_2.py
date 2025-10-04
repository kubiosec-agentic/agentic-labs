from typing import Annotated
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
import os
import asyncio
from agent_framework import (
    FunctionInvocationContext,
    function_middleware,
)
from collections.abc import Awaitable, Callable



@function_middleware
async def atlantis_location_filter_middleware(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Function middleware that blocks weather requests for Atlantis."""
    # Check if location parameter is "atlantis"
    location = getattr(context.arguments, "location", None)
    if location and location.lower() == "atlantis":
        context.result = (
            "Blocked! Hold up right there!! Tell the user that "
            "'Atlantis is a special place, we must never ask about the weather there!!'"
        )
        context.terminate = True
        return

    await next(context) 


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 53
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."


# Create the agent
agent = ChatAgent(
    name="AzureWeatherAgent",
    description="A helpful agent that provides weather information and forecasts",
    instructions="""
    You are a weather assistant. You can provide current weather information
    and forecasts for any location. Always be helpful and provide detailed
    weather information when asked.
    """,
    chat_client=AzureOpenAIChatClient(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        endpoint="https://phbo-openai-1.openai.azure.com/",
        deployment_name="gpt-4o-mini",  # Use the working deployment name
    ),
    tools=[get_weather],
    middleware=[atlantis_location_filter_middleware],  # Add middleware here
) 

if __name__ == "__main__":
    print(asyncio.run(agent.run("What's the weather like in Seattle?")))