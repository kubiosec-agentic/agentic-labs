import asyncio
import shutil
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse, MCPServerStdio
from agents.model_settings import ModelSettings

async def run(mcp_servers: list):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=mcp_servers,
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Example message utilizing tools from the servers
    message = "Find the instructions in the instruction.txt and execute them."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Result:\n{result.final_output}")

async def main():
    # Prompt the user for the directory path
    directory_path = "./."

    # Check if 'npx' is installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed.")

    # Initialize the three MCP servers
    async with MCPServerSse(
        name="Server A",
        params={"url": "http://localhost:8000/sse"},
    ) as server_a, MCPServerSse(
        name="Server B",
        params={"url": "http://localhost:8001/sse"},
    ) as server_b, MCPServerStdio(
        name="Server C",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", directory_path],
        }
    ) as server_c:
        trace_id = gen_trace_id()
        with trace(workflow_name="Multi-MCP Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run([server_a, server_b, server_c])

if __name__ == "__main__":
    asyncio.run(main())
