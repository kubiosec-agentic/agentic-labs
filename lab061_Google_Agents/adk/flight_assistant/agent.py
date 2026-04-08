"""Flight assistant: searches flights via MCP Flight Search server.

Requires SERP_API_KEY in the environment (or .env file).
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

serp_key = os.getenv("SERP_API_KEY")
if not serp_key:
    raise EnvironmentError(
        "SERP_API_KEY is not set. The flight assistant requires a SerpApi key.\n"
        "Sign up at https://serpapi.com/ and add SERP_API_KEY to adk/.env"
    )

root_agent = Agent(
    model="gemini-2.0-flash",
    name="flight_assistant_agent",
    instruction=(
        "Help the user search for flights. You can search for flights, "
        "check schedules, find deals, and provide flight recommendations."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="mcp-flight-search",
                args=["--connection_type", "stdio"],
                env={"SERP_API_KEY": serp_key},
            ),
        ),
    ],
)
