# Enhanced flight search agent with better error handling - Updated for latest google-adk
import asyncio
import os
import logging
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def get_tools_async():
    """Try to connect to MCP Flight Search server, return empty list if it fails"""
    try:
        print("Attempting to connect to MCP Flight Search server...")
        serp_key = os.getenv("SERP_API_KEY")
        env_vars = {"SERP_API_KEY": serp_key} if serp_key else {}
        server_params = StdioServerParameters(
            command="mcp-flight-search",
            args=["--connection_type", "stdio"],
            env=env_vars,
        )
        
        # Create toolset and get tools using new API
        toolset = MCPToolset(connection_params=server_params)
        tools = await toolset.get_tools()
        print(f"Successfully loaded {len(tools)} tool(s).")
        return tools, toolset
    except Exception as e:
        print(f"Failed to connect to MCP Flight Search server: {e}")
        print("Continuing without flight search tools...")
        return [], None

async def get_agent_async():
    tools, toolset = await get_tools_async()
    
    # Enhanced instruction that handles both cases - with and without tools
    instruction = """You are a flight search assistant. 

If you have access to flight search tools, use them to find real flight information.

If you don't have access to flight search tools (due to API key issues), provide helpful general advice about:
- Best times to book flights
- Tips for finding good deals
- Information about airports and airlines
- General travel advice for the route requested
- Suggest alternative ways to search for flights (Google Flights, airline websites, etc.)

Always be helpful and provide value even when you can't access real-time flight data."""
    
    agent = LlmAgent(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest"),
        name="flight_search_assistant",
        instruction=instruction,
        tools=tools,
    )
    return agent, toolset

async def async_main():
    ss = InMemorySessionService()
    # Updated for latest version - create_session is now async
    session = await ss.create_session(
        app_name="flight_search_app",
        user_id="user_flights",
        state={}
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text="Find flights from Atlanta to Brussels 2025-09-05 one-way")]
    )

    agent, toolset = await get_agent_async()
    runner = Runner(app_name="flight_search_app", agent=agent, session_service=ss)

    print("Running agent...")
    async for event in runner.run_async(session_id=session.id, user_id=session.user_id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"\n{event.author}: {part.text}")
                elif part.function_call:
                    print(f"\n{event.author} calling function: {part.function_call.name}")

    print("\nClosing connections...")
    if toolset:
        await toolset.close()  # Updated method name
    print("Cleanup complete.")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError("Set GOOGLE_API_KEY in your .env")
    
    # SERP_API_KEY is optional - the agent will work without it
    if not os.getenv("SERP_API_KEY"):
        print("Warning: SERP_API_KEY not found. Flight search tools will not be available.")
    
    asyncio.run(async_main())
