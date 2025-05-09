import asyncio
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings


async def run(mcp_servers: list[MCPServerSse]):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=mcp_servers,
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Test tool 1 (e.g., from server A)
    message = "Add these numbers: 7 and 22."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Result:\n{result.final_output}")

    # Test tool 2 (e.g., from server B)
    message = "What's the weather in Tokyo?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Result:\n{result.final_output}")

    # Test tool 3 (also from server B or A)
    message = "What's the secret word?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Result:\n{result.final_output}")


async def main():
    # You can replace the second URL with a different one if you have two actual MCP servers
    async with MCPServerSse(
        name="Server A",
        params={"url": "http://localhost:8000/sse"},
    ) as server_a, MCPServerSse(
        name="Server B",
        params={"url": "http://localhost:8001/sse"},  # Use same server for test, or change port
    ) as server_b:
        trace_id = gen_trace_id()
        with trace(workflow_name="Multi-MCP Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run([server_a, server_b])


if __name__ == "__main__":
    asyncio.run(main())
