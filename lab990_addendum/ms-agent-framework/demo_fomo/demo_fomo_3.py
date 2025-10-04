from typing import Annotated
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
import os
import asyncio
from agent_framework import (
    FunctionInvocationContext,
    function_middleware,
    ChatContext,
    ChatMessage,
    ChatResponse,
    Role,
    chat_middleware,
)
from collections.abc import Awaitable, Callable


@chat_middleware
async def security_filter_middleware(
    context: ChatContext,
    next: Callable[[ChatContext], Awaitable[None]],
) -> None:
    """Chat middleware that blocks requests containing sensitive information."""
    blocked_terms = ["password", "secret", "api_key", "token"]

    for message in context.messages:
        if message.text:
            message_lower = message.text.lower()
            for term in blocked_terms:
                if term in message_lower:
                    # Override the response without calling the LLM
                    context.result = ChatResponse(
                        messages=[
                            ChatMessage(
                                role=Role.ASSISTANT,
                                text=(
                                    "I cannot process requests containing sensitive information. "
                                    "Please rephrase your question without including passwords, secrets, "
                                    "or other sensitive data."
                                ),
                            )
                        ]
                    )
                    return

    await next(context) 


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


# Create the agent with both security and function middleware
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
    middleware=[security_filter_middleware, atlantis_location_filter_middleware],  # Both middleware
) 

if __name__ == "__main__":
    print("Testing normal weather request:")
    print(asyncio.run(agent.run("What's the weather like in Seattle?")))
    
    print("\nTesting Atlantis request (function middleware):")
    print(asyncio.run(agent.run("What's the weather like in Atlantis?")))
    
    print("\nTesting security filter (chat middleware):")
    print(asyncio.run(agent.run("What's the weather like in Paris? My password is 12345.")))