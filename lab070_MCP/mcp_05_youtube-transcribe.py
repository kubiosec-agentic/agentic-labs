"""
Lab 070 - MCP over Streamable HTTP against a hosted YouTube transcriber.

This example talks to a remote MCP server on mcp-cloud.ai that exposes a
`get_transcript` tool for YouTube videos. It uses Streamable HTTP transport
(not stdio, not SSE) and passes a bearer token via the Authorization header.

Environment variables:
    MCP_HTTP_URL        Full URL of the remote MCP endpoint, e.g.
                        https://youtube-transcribe-2-XXXX.server.mcp-cloud.ai/mcp
    MCPCLOUD_API_TOKEN  JWT bearer token issued by mcp-cloud.ai

Run:
    export MCP_HTTP_URL="https://youtube-transcribe-2-1764776944236.server.mcp-cloud.ai/mcp"
    export MCPCLOUD_API_TOKEN="eyJhbGciOi..."
    python3 mcp_05_youtube-transcribe.py
"""

import asyncio
import os

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions=(
            "You are a video assistant. Use the available MCP tools to fetch "
            "the transcript of the requested YouTube video, then produce a "
            "concise summary with the main points and any notable quotes."
        ),
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    test_messages = [
        "Transcribe and summarize the following video: https://www.youtube.com/watch?v=ZXiruGOCn9s&t=197s",
    ]

    for idx, message in enumerate(test_messages):
        print(f"\n\nRunning: {message}" if idx > 0 else f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        print(result.final_output)


async def init_server():
    url = os.getenv("MCP_HTTP_URL")
    token = os.getenv("MCPCLOUD_API_TOKEN")
    if not url or not token:
        raise RuntimeError(
            "Set MCP_HTTP_URL and MCPCLOUD_API_TOKEN before running this script."
        )

    # Streamable HTTP transport. Note: mcp-cloud.ai serves the endpoint at
    # /mcp (no trailing slash here, unlike local fastmcp 3.x which uses /mcp/).
    server = MCPServerStreamableHttp(
        name="youtube-transcribe",
        params={
            "url": url,
            "headers": {"Authorization": f"Bearer {token}"},
            "timeout": 120,
        },
        client_session_timeout_seconds=300,
        max_retry_attempts=3,
    )
    return server


async def main():
    async with await init_server() as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="YouTube Transcribe (Streamable HTTP)", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())
