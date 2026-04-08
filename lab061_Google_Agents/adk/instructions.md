# Creating a new ADK agent

These are working examples of Google ADK agents using the Google Generative AI API and MCP.

## Skeleton

Every ADK agent lives in its own subdirectory under `adk/` and requires three files.

### 1. `.env` (in the `adk/` root, shared by all agents)

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. `__init__.py`

```python
from . import agent
```

### 3. `agent.py`

Define a `root_agent` at module level. `adk web` discovers it automatically.

**Example: MCP filesystem agent**

```python
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Change this to the folder you want the agent to manage.
TARGET_FOLDER = os.path.expanduser("~/projects")

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
```

**Example: MCP flight search agent**

```python
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

root_agent = Agent(
    model="gemini-2.0-flash",
    name="flight_assistant_agent",
    instruction="Help the user search for flights.",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="mcp-flight-search",
                args=["--connection_type", "stdio"],
                env={"SERP_API_KEY": os.getenv("SERP_API_KEY", "")},
            ),
        ),
    ],
)
```
