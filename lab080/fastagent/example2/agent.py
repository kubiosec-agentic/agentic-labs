import asyncio
from mcp_agent.core.fastagent import FastAgent
from pydantic import AnyUrl

fast = FastAgent("My XSS Learning Agent")

@fast.agent(name="my-agent-2",instruction=AnyUrl("https://gist.githubusercontent.com/evalstate/d432921aaaee2c305cf46ae320840360/raw/eb9c7ff93adc780171bfb0ae2560be2178304f16/gistfile1.txt"))

async def main():
    async with fast.run() as agent:
        await agent("write me instrcution for testing XSS in a test web application using svg tags")

if __name__ == "__main__":
    asyncio.run(main())