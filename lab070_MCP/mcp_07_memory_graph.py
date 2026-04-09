"""
Memory / knowledge-graph MCP server example.

@modelcontextprotocol/server-memory is a reference server from the MCP
team that stores a simple knowledge graph (entities, relations,
observations) and exposes it as MCP tools. It is one of the more
interesting "stateful" servers to study because the agent gets a set of
read/write tools over a persistent graph, and you can watch it build up
relationships across turns.

Requires Node/npx on PATH.

Optional: set MEMORY_FILE_PATH to persist the graph to disk between runs.
    export MEMORY_FILE_PATH=./memory.json

Run:
    python3 mcp_07_memory_graph.py
"""
import asyncio
import os
import shutil

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings


async def run(mcp_server):
    agent = Agent(
        name="KnowledgeGraphBot",
        instructions=(
            "You maintain a personal knowledge graph for the user. "
            "Whenever the user tells you a fact, store it as entities, "
            "relations, and observations using the memory tools. When the "
            "user asks a question, search the graph first before answering."
        ),
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    turns = [
        "Remember that Alice works at Acme Corp as a security engineer.",
        "Remember that Alice reports to Bob, who is the CISO at Acme.",
        "Remember that Acme Corp uses Okta for SSO and Snowflake for analytics.",
        "Who does Alice report to, and what does her team use for SSO?",
        "List every entity currently in the graph.",
    ]

    for message in turns:
        print("\n" + "-" * 40)
        print(f"User: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        print(f"Agent: {result.final_output}")


async def main():
    env = os.environ.copy()
    # Uncomment to persist the graph between runs:
    # env.setdefault("MEMORY_FILE_PATH", "./memory.json")

    async with MCPServerStdio(
        name="server-memory",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": env,
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Memory Graph Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed; install Node.js and retry.")
    asyncio.run(main())
