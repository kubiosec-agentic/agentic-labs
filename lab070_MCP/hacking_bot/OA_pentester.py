import asyncio
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from agents.memory import SQLiteSession

async def run(mcp_servers: list[MCPServerStreamableHttp]):
    agent = Agent(
        name="Assistant",
        instructions=(
            "You are a security review and pentesting agent. "
            "Use the available MCP tools to run scans. "
            "Missing tools must be installed. This is a sandboxed environment."
            "Use apt-get update and apt-get install to install missing tools."
        ),
        mcp_servers=mcp_servers,
        model_settings=ModelSettings(tool_choice="required"),
    )

    session = SQLiteSession("lab070")  # <- multi-turn memory

    message = "Install nikto if not available." \
              "Scan http://192.168.0.202:80 using nikto and save the results to /tmp/nikto_scan_<random_id>.txt." \
              "Run nikto in the background." \
              "Always proceed with the required actions to complete the task."

    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message, session=session)
    print(f"Result:\n{result.final_output}")

async def init_servers():
    # Longer timeouts so installs/scans can finish
    server_a = MCPServerStreamableHttp(
        name="Server A",
        params={
            "url": "http://127.0.0.1:8000/mcp",
            "timeout": 120,  # per-request HTTP timeout
        },
        client_session_timeout_seconds=300,  # read timeout for long ops
        max_retry_attempts=3,
    )
    return server_a

async def main():
    server_a = await init_servers()
    async with server_a:
        trace_id = gen_trace_id()
        with trace(workflow_name="Multi-MCP Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run([server_a])

if __name__ == "__main__":
    asyncio.run(main())
