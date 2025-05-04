import asyncio
import shutil

from agents import Agent, Runner, trace
from agents.mcp import MCPServer, MCPServerStdio


async def run(mcp_server: MCPServer, directory_path: str):
    agent = Agent(
        name="Assistant",
        instructions=f"Answer questions about the git repository at {directory_path}, use that for repo_path",
        mcp_servers=[mcp_server],
    )

    message = "List me the files in the diretory?"
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "What type of files are in the directory?"
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    # Ask the user for the directory path
    directory_path = input("Please enter the path: ")

    async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", directory_path],
    }
    ) as server:
       tools = await server.list_tools()
       await run(server, directory_path)



if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `xxxxxx`.")

    asyncio.run(main())
