import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
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
    server_a = MCPServerSse(
        name="Server A",
        params={"url": "http://localhost:8000/sse"},
    )
    return server_a

async def main():
    async with await init_server() as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())

