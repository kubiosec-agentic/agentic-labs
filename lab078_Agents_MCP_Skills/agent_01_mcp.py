"""
Exercise 1: an OpenAI Agents SDK agent that talks to an MCP server (stdio).

No skills yet. Just the baseline: how the Agents SDK spawns a stdio MCP server
and exposes its tools to the model.

  MCPServerStdio(params={"command": python, "args": ["mcp_server.py"]})

spawns `python mcp_server.py` as a subprocess and speaks MCP JSON-RPC to it
over stdio. Passed to Agent(mcp_servers=[server]), the server's tools (add,
http_get) become callable by the model, alongside any function tools.

Run (needs OPENAI_API_KEY):
    python3 agent_01_mcp.py
"""

import asyncio
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

from common import MODEL, disable_tracing, require_key

HERE = Path(__file__).parent


async def main() -> None:
    disable_tracing()
    require_key()

    async with MCPServerStdio(
        name="lab078",
        params={
            "command": sys.executable,          # this venv's python
            "args": [str(HERE / "mcp_server.py")],
            "cwd": str(HERE),
        },
        cache_tools_list=True,                  # tools do not change mid-run
        client_session_timeout_seconds=15,
    ) as server:
        # Prove the wiring before we even build the agent: this needs no key.
        tools = await server.list_tools()
        print("MCP tools discovered:", [t.name for t in tools])

        agent = Agent(
            name="Recon assistant",
            model=MODEL,
            instructions=(
                "You are a security recon assistant. Use the MCP tools when they help. "
                "add(a,b) does arithmetic; http_get(url) fetches a URL and returns its "
                "status, headers and a body snippet."
            ),
            mcp_servers=[server],
        )

        result = await Runner.run(
            agent,
            "First add 21 and 21. Then fetch https://example.com and tell me its HTTP "
            "status code and its Content-Type header. Keep it short.",
        )
        print("\n--- final output ---")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
