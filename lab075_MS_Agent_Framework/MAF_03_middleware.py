"""
Exercise 3: Chat middleware and function middleware.

Microsoft Agent Framework has two middleware hooks that sit between
your agent and the LLM (chat middleware) or between the LLM and your
tools (function middleware). This is the framework's answer to
"how do I add security guardrails without touching every tool?"

This example uses OpenAIChatClient so it runs without Azure. The
middleware API is identical on both backends.

What to observe:
  - security_filter_middleware fires BEFORE the LLM sees the message.
    If a blocked term is found, the LLM is never called.
  - atlantis_filter_middleware fires AFTER the LLM decides to call
    get_weather but BEFORE the function executes. It can inspect
    arguments and short-circuit the call.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"

Run:
    python3 MAF_03_middleware.py
"""

import asyncio
import os
import sys
from typing import Annotated

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")
if not os.environ.get("OPENAI_CHAT_MODEL"):
    sys.exit("Error: OPENAI_CHAT_MODEL is not set. Run: export OPENAI_CHAT_MODEL=\"gpt-4o-mini\"")

from agent_framework import (
    ChatContext,
    ChatResponse,
    FunctionInvocationContext,
    Message,
    chat_middleware,
    function_middleware,
)
from agent_framework.openai import OpenAIChatClient


# ---------------------------------------------------------------------------
# Chat middleware: runs before the LLM sees the user message.
# ---------------------------------------------------------------------------
@chat_middleware
async def security_filter_middleware(
    context: ChatContext,
    call_next,
) -> None:
    """Block requests that contain sensitive keywords."""
    blocked_terms = ["password", "secret", "api_key", "token"]

    for message in context.messages:
        if message.text:
            lower = message.text.lower()
            for term in blocked_terms:
                if term in lower:
                    context.result = ChatResponse(
                        messages=[
                            Message(
                                role="assistant",
                                contents=[
                                    "I cannot process requests containing "
                                    "sensitive information. Please rephrase "
                                    "without passwords, secrets, or tokens."
                                ],
                            )
                        ]
                    )
                    return  # short-circuit: LLM is never called

    await call_next()


# ---------------------------------------------------------------------------
# Function middleware: runs when the LLM calls a tool, before execution.
# ---------------------------------------------------------------------------
@function_middleware
async def atlantis_filter_middleware(
    context: FunctionInvocationContext,
    call_next,
) -> None:
    """Block weather requests for Atlantis (demo guardrail)."""
    location = getattr(context.arguments, "location", None)
    if location and location.lower() == "atlantis":
        context.result = (
            "Blocked! Atlantis is off-limits. Tell the user we cannot "
            "provide weather information for fictional locations."
        )
        context.terminate = True
        return

    await call_next()


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------
def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny with a high of 22C."


# ---------------------------------------------------------------------------
# Agent wiring
# ---------------------------------------------------------------------------
async def main() -> None:
    agent = OpenAIChatClient().as_agent(
        name="SecureWeatherAgent",
        description="Weather agent with security middleware",
        instructions="You are a helpful weather assistant.",
        tools=[get_weather],
        middleware=[security_filter_middleware, atlantis_filter_middleware],
    )

    tests = [
        ("Normal request", "What's the weather in Tokyo?"),
        ("Atlantis (function middleware)", "What's the weather in Atlantis?"),
        ("Sensitive info (chat middleware)", "Weather in Paris? My password is 12345."),
    ]

    for label, query in tests:
        print(f"--- {label} ---")
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
