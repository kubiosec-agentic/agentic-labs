"""
Agent example: single MCP server over streamable HTTP.

Client side uses the openai-agents SDK (MCPServerStreamableHttp). The server
is the fastmcp-based server_streamable.py running on localhost:8000.

Run (in two terminals):
    terminal 1: python3 server_streamable.py
    terminal 2: python3 mcp_02_streamable.py
"""
import asyncio

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    test_messages = [
        "Add these numbers: 7 and 22.",
        "What's the weather in Tokyo?",
        "What's the secret word?",
    ]

    for idx, message in enumerate(test_messages):
        print(f"\n\nRunning: {message}" if idx > 0 else f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        print(result.final_output)


async def init_server():
    return MCPServerStreamableHttp(
        name="Server A",
        params={"url": "http://localhost:8000/mcp"},
    )


async def main():
    async with await init_server() as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="HTTP Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())
