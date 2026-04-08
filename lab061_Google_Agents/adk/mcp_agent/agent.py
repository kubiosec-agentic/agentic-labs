"""Filesystem assistant: manages files via MCP filesystem server.

Uses the @modelcontextprotocol/server-filesystem Node.js MCP server.
Requires Node.js (npx) to be installed.

Change TARGET_FOLDER to point at the directory you want the agent to access.
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Change this to the absolute path of the folder you want the agent to manage.
TARGET_FOLDER = os.path.expanduser("~")

root_agent = Agent(
    model="gemini-2.0-flash",
    name="filesystem_assistant_agent",
    instruction="Help the user manage their files. You can list files, read files, etc.",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    os.path.abspath(TARGET_FOLDER),
                ],
            ),
        ),
    ],
)
