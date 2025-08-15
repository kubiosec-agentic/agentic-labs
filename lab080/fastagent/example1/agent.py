import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("My Interactive Agent")

@fast.agent(instruction="You are a helpful assistant")
async def main():
    async with fast.run() as agent:
        # Start interactive prompt
        await agent()

if __name__ == "__main__":
    asyncio.run(main())