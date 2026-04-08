"""
Agent with a function tool.

Defines a weather tool via the @function_tool decorator, attaches it
to an agent, and runs an async query. The agent decides to call the
tool, receives the result, and produces a final answer.
"""

from agents import Agent, Runner, function_tool
import asyncio


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)


async def main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
