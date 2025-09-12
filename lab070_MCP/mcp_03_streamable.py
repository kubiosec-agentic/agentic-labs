import asyncio
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp 
from agents.model_settings import ModelSettings


async def run(mcp_servers: list[MCPServerStreamableHttp]):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=mcp_servers,
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
        print(f"Result:\n{result.final_output}")


async def init_servers():
    server_a = MCPServerStreamableHttp(
        name="Server A",
        params={"url": "http://localhost:8000/mcp/"},
    )
    server_b = MCPServerStreamableHttp(
        name="Server B",
        params={"url": "http://localhost:8001/mcp/"},
    )
    return server_a, server_b


async def main():
    server_a, server_b = await init_servers()
    async with server_a, server_b:
        trace_id = gen_trace_id()
        with trace(workflow_name="Multi-MCP Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run([server_a, server_b])


if __name__ == "__main__":
    asyncio.run(main())
