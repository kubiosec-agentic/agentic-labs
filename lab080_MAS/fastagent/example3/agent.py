import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("My YouTube Transcriber Agent")

@fast.agent(servers=["youtube_transcribe", "exa_search"])
async def main():
    async with fast.run() as agent:
        await agent("Find me a youtube video about the latest advancements in OpenAI and transcribe it in a detailed way.")

if __name__ == "__main__":
    asyncio.run(main())