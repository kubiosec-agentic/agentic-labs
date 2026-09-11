import asyncio
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)

async def main():
    results = await asyncio.gather(
        Runner.run(agent, "Write a haiku about recursion."),
        Runner.run(agent, "Write a haiku about Kubernetes."),
        Runner.run(agent, "Write a haiku about MCP."),
    )

    for result in results:
        print(result.final_output)

asyncio.run(main())