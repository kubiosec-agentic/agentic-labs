import asyncio
import shutil

from agents import Agent, Runner
from agents.run_context import RunContextWrapper
from agents.mcp import MCPServerStdio

async def run(mcp_server: MCPServerStdio, directory_path: str, ctx, agent):
    for message in [
        "List me the files in the directory?",
        "What type of files are in the directory?"
    ]:
        print("\n" + "-" * 40)
        print(f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=message, context=ctx)
        print(result.final_output)

async def main():
    directory_path = input("Please enter the path: ")

    async with MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", directory_path],
        }
    ) as server:
        run_context = RunContextWrapper(context=None)
        agent = Agent(
            name="Assistant",
            instructions=f"Answer questions about the git repository at {directory_path}, use that for repo_path",
            mcp_servers=[server],
        )

        tools = await server.list_tools(run_context, agent)
        print("Available tools:", [tool.name for tool in tools])

        await run(server, directory_path, run_context, agent)

if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed.")
    asyncio.run(main())
