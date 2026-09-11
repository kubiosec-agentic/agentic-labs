import asyncio
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)

async def main():
    result = await Runner.run(agent, "Write a haiku about recursion.")
    print(result.final_output)

asyncio.run(main())
