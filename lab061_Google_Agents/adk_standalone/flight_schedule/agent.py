"""
Standalone flight search agent with Runner and InMemorySessionService.

Unlike the adk/ agents (which are loaded by `adk web`), this script
runs the agent directly from the command line using the ADK Runner API.

Requires:
  - GOOGLE_API_KEY in the environment (or .env file)
  - SERP_API_KEY for live flight search (optional; the agent degrades gracefully)
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def get_tools_async():
    """Connect to MCP Flight Search server; return empty list on failure."""
    try:
        print("Connecting to MCP Flight Search server...")
        serp_key = os.getenv("SERP_API_KEY")
        env_vars = {"SERP_API_KEY": serp_key} if serp_key else {}
        server_params = StdioServerParameters(
            command="mcp-flight-search",
            args=["--connection_type", "stdio"],
            env=env_vars,
        )
        toolset = MCPToolset(connection_params=server_params)
        tools = await toolset.get_tools()
        print(f"Loaded {len(tools)} tool(s).")
        return tools, toolset
    except Exception as e:
        print(f"MCP Flight Search server unavailable: {e}")
        print("Continuing without flight search tools.")
        return [], None


async def get_agent_async():
    tools, toolset = await get_tools_async()

    instruction = (
        "You are a flight search assistant.\n\n"
        "If you have access to flight search tools, use them to find "
        "real flight information.\n\n"
        "If you do not have access to flight search tools, provide "
        "helpful general advice: best times to book, tips for finding "
        "deals, airport and airline information, and suggest alternative "
        "search methods (Google Flights, airline websites, etc.).\n\n"
        "Always be helpful even when real-time data is unavailable."
    )

    agent = Agent(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        name="flight_search_assistant",
        instruction=instruction,
        tools=tools,
    )
    return agent, toolset


async def async_main():
    ss = InMemorySessionService()
    session = await ss.create_session(
        app_name="flight_search_app",
        user_id="user_flights",
        state={},
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text="Find flights from Atlanta to Brussels 2025-09-30 one-way")],
    )

    agent, toolset = await get_agent_async()
    runner = Runner(
        app_name="flight_search_app",
        agent=agent,
        session_service=ss,
    )

    print("Running agent...")
    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"\n{event.author}: {part.text}")
                elif part.function_call:
                    print(f"\n{event.author} calling: {part.function_call.name}")

    print("\nClosing connections...")
    if toolset:
        await toolset.close()
    print("Done.")


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError("Set GOOGLE_API_KEY in your .env")

    if not os.getenv("SERP_API_KEY"):
        print("Warning: SERP_API_KEY not found. Flight search tools will be unavailable.")

    asyncio.run(async_main())
