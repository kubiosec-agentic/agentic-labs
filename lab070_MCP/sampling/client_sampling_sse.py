"""Sampling demo client over SSE with a stub sampling handler.

The handler here is deliberately trivial (it returns a fixed string) to
make the protocol flow easy to read in the logs. Swap in the OpenAI or
Anthropic handler from the HTTP example for real inference.
"""
import asyncio
from fastmcp import Client
from fastmcp.client.sampling import (
    SamplingMessage,
    SamplingParams,
    RequestContext,
)
from fastmcp.client.transports import SSETransport


async def basic_sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    context: RequestContext,
) -> str:
    print("[client:sampling_handler] received:")
    for message in messages:
        print(f"  {message.role}: {message.content.text}")
    return "I really do not care"  # stubbed completion


def basic_log_handler(level: str, message: str):
    print(f"[client:log:{level}] {message}")


transport = SSETransport(url="http://127.0.0.1:8000/sse/")

client = Client(
    transport=transport,
    sampling_handler=basic_sampling_handler,
    log_handler=basic_log_handler,
)


async def main():
    async with client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"  description: {tool.description}")

        result = await client.call_tool(
            "analyze_sentiment",
            {"text": "What a great day!"},
        )
        # fastmcp 3.x: CallToolResult, not a list. Use .data / .content.
        print(f"Tool result (structured) -> {result.data}")
        if result.content:
            print(f"Tool result (text block) -> {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
