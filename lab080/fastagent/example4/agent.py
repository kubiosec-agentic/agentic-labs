import asyncio

from mcp_agent.core.fastagent import FastAgent

# Create the application
MyFastAgent = FastAgent("Agent Chaining")


@MyFastAgent.agent(
    "url_fetcher",
    instruction="Given a URL, provide a complete and comprehensive summary",
    servers=["fetch"],
)
@MyFastAgent.agent(
    "social_media",
    instruction="""
    Write a 280 character social media post for any given text. 
    Respond only with the post, never use hashtags.
    """,
)

@MyFastAgent.chain(
    name="post_writer",
    sequence=["url_fetcher", "social_media"],
)

async def main() -> None:
    async with MyFastAgent.run() as agent:
        result = await agent.post_writer.send("https://www.radarhack.com")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())