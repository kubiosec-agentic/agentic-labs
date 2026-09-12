"""
OpenAI Agents SDK + one stateless MCP server, end to end (README section 6).

Unlike client_demo.py (a bare fastmcp client that only speaks MCP), this is a
real openai-agents Agent. It connects to stateless_server.py over streamable
HTTP and answers a question by calling that server's MCP tools. That gives you
the FULL flow to watch in mitmproxy, both legs of an agentic call:

    agent  ->  OpenAI API   (the model deciding which tool to call, then
                             composing the answer from the tool results)
    agent  ->  MCP server   (initialize, tools/list, tools/call add,
                             tools/call celsius_to_fahrenheit)

Both legs are pointed through mitmproxy with environment variables, so nothing
in the code is proxy-specific:

    OPENAI_API_KEY    required (a real key; the model call is real)
    OPENAI_BASE_URL   OpenAI traffic target. Set to the mitm reverse proxy
                      (e.g. http://127.0.0.1:8080/v1/) to capture the LLM leg.
                      Default: the real api.openai.com.
    MCP_URL           MCP server URL. Set to the mitm reverse proxy
                      (e.g. http://127.0.0.1:8089/mcp) to capture the MCP leg.
                      Default: http://127.0.0.1:8100/mcp (direct).
    AGENT_MODEL       Override the model (default gpt-4o-mini).

Run directly (no proxy):
    export OPENAI_API_KEY=...
    python3 stateless_server.py            # in another terminal
    python3 agent_demo.py

Run through mitmproxy: see README section 6.
"""
import os
import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def main() -> None:
    mcp_url = os.getenv("MCP_URL", "http://127.0.0.1:8100/mcp")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1 (default)")
    print(f"MCP server   : {mcp_url}")
    print(f"OpenAI target: {base_url}")

    async with MCPServerStreamableHttp(
        name="stateless-math",
        params={"url": mcp_url},
        client_session_timeout_seconds=30,
    ) as server:
        agent = Agent(
            name="MathAgent",
            instructions=(
                "You answer using ONLY the MCP tools provided (add, multiply, "
                "celsius_to_fahrenheit). Call the tools; do not compute in your "
                "head. Report each tool's result plainly."
            ),
            model=os.getenv("AGENT_MODEL", "gpt-4o-mini"),
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="auto"),
        )

        task = "Add 7 and 5, then convert 21 degrees Celsius to Fahrenheit."
        print(f"\nTask: {task}\n")
        result = await Runner.run(starting_agent=agent, input=task)
        print(f"Agent answer:\n{result.final_output}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY first (the model call is real).")
    asyncio.run(main())
