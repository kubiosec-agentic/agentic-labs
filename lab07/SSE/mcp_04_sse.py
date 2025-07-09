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
    message = "Find the instructions in the instruction.txt and execute them."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Result:\n{result.final_output}")

async def init_servers(directory_path):
    server_a = MCPServerSse(
        name="Server A",
        params={"url": "http://localhost:8000/sse"},
    )
    server_b = MCPServerSse(
        name="Server B",
        params={
            "url": "http://localhost:8001/sse",
            "headers": {"Authorization": "top-secret"}
        },
    )
    server_c = MCPServerStdio(
        name="Server C",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", directory_path],
        }
    )
    return server_a, server_b, server_c

async def main():
    directory_path = "./."
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed.")

    server_a, server_b, server_c = await init_servers(directory_path)
    async with server_a, server_b, server_c:
        trace_id = gen_trace_id()
        with trace(workflow_name="Multi-MCP Example Rogue", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run([server_a, server_b, server_c])

if __name__ == "__main__":
    asyncio.run(main())
