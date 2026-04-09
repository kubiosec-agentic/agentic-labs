"""
Sampling demo: fastmcp Client over streamable HTTP with an OpenAI-backed
sampling handler.

The client connects to server_sampling_http.py, lists tools, then calls
`analyze_sentiment`. The server's implementation of that tool issues a
`sampling/createMessage` request back through the session. fastmcp routes
that request to the `sampling_handler` registered on this Client, which
forwards the messages to the OpenAI API and returns the completion. The
server sees only the final text, not the provider, model, or key.

Environment:
    OPENAI_API_KEY must be set (openai>=1.0).

Run:
    python3 client_sampling_http.py
"""
import asyncio
from fastmcp import Client
from fastmcp.client.sampling import (
    SamplingMessage,
    SamplingParams,
    RequestContext,
)
import openai


async def basic_sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    context: RequestContext,
) -> str:
    print("[client:sampling_handler] Received sampling request:")
    for message in messages:
        print(f"  {message.role}: {message.content.text}")

    chat_messages = [
        {"role": m.role, "content": m.content.text} for m in messages
    ]
    oa = openai.OpenAI()
    response = oa.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_messages,
        max_tokens=256,
        temperature=0.2,
    )
    return response.choices[0].message.content


def basic_log_handler(level: str, message: str):
    print(f"[client:log:{level}] {message}")


client = Client(
    "http://127.0.0.1:8000/mcp/",
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
            {"text": "I really hate this world !!!!!!!1"},
        )
        # fastmcp 3.x: call_tool returns a CallToolResult, not a list.
        # .data is the parsed structured return; .content holds raw blocks.
        print(f"Tool result (structured) -> {result.data}")
        if result.content:
            print(f"Tool result (text block) -> {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
