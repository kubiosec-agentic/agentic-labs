# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Annotated
from collections.abc import Awaitable, Callable

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field
from agent_framework import (
    FunctionInvocationContext,
    function_middleware,
    ChatContext,
    ChatMessage,
    ChatResponse,
    Role,
    chat_middleware,
)

"""
Azure AI Agent Demo with Middleware

This demo is based on azure_agent.py but adds security and function middleware
to demonstrate advanced filtering capabilities with Azure AI Agent Client.
"""


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
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 53
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response with middleware protection."""
    print("=== Non-streaming Response Example with Middleware ===")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="SecureWeatherAgent",
            instructions="You are a helpful weather agent with security protections.",
            tools=get_weather,
        ) as agent,
    ):
        # Apply middleware to the agent
        agent.middleware = [security_filter_middleware, atlantis_location_filter_middleware]
        
        query = "What's the weather like in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response with middleware protection."""
    print("=== Streaming Response Example with Middleware ===")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="SecureWeatherAgent",
            instructions="You are a helpful weather agent with security protections.",
            tools=get_weather,
        ) as agent,
    ):
        # Apply middleware to the agent
        agent.middleware = [security_filter_middleware, atlantis_location_filter_middleware]
        
        query = "What's the weather like in Portland?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def middleware_test_examples() -> None:
    """Examples demonstrating middleware functionality."""
    print("=== Middleware Test Examples ===")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="SecureWeatherAgent",
            instructions="You are a helpful weather agent with security protections.",
            tools=get_weather,
        ) as agent,
    ):
        # Apply middleware to the agent
        agent.middleware = [security_filter_middleware, atlantis_location_filter_middleware]
        
        # Test 1: Normal request (should work)
        print("Test 1 - Normal weather request:")
        query1 = "What's the weather like in Tokyo?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1}\n")
        
        # Test 2: Atlantis request (function middleware should block)
        print("Test 2 - Atlantis request (should be blocked by function middleware):")
        query2 = "What's the weather like in Atlantis?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2}\n")
        
        # Test 3: Sensitive information (chat middleware should block)
        print("Test 3 - Request with sensitive info (should be blocked by chat middleware):")
        query3 = "What's the weather like in Paris? My password is 12345."
        print(f"User: {query3}")
        result3 = await agent.run(query3)
        print(f"Agent: {result3}\n")


async def main() -> None:
    print("=== Azure AI Agent Client with Middleware Demo ===")

    await non_streaming_example()
    await streaming_example()
    await middleware_test_examples()


if __name__ == "__main__":
    asyncio.run(main())