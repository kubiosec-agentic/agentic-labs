![Google](https://img.shields.io/badge/Google-green) ![ADK](https://img.shields.io/badge/ADK-brightgreen) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB061: Google Agent Development Kit (ADK)

## Introduction

Google's Agent Development Kit (ADK) is a framework for building agents powered by Gemini models. An ADK agent is a Python module that defines a `root_agent` with a model, instructions, and optional tools. The `adk` CLI discovers agents automatically and serves them through a web UI and a REST API.

This lab contains four agents that demonstrate different tool-integration patterns, plus a standalone script that shows how to run an agent programmatically (without the `adk` CLI). The agents cover plain function tools, Google Search, MCP filesystem access, and MCP flight search.

| Directory | Agent | Tools | Model |
|-----------|-------|-------|-------|
| `adk/multi_tool_agent/` | Weather and time lookup | Python functions (mock data) | gemini-2.0-flash |
| `adk/google_search_agent/` | Web research assistant | `google_search` (built-in) | gemini-2.5-flash |
| `adk/mcp_agent/` | Filesystem manager | MCP `@modelcontextprotocol/server-filesystem` | gemini-2.0-flash |
| `adk/flight_assistant/` | Flight search | MCP `mcp-flight-search` | gemini-2.0-flash |
| `adk_standalone/flight_schedule/` | Flight search (standalone) | MCP `mcp-flight-search` via Runner API | gemini-2.0-flash |

## Set up your environment

```bash
export GOOGLE_API_KEY="your-google-api-key"
```

```bash
./lab_setup.sh
source .lab061/bin/activate
```

### API keys

**Google API Key** (required for all agents): get one from [Google AI Studio](https://aistudio.google.com/). Click "Get API Key" and create a new key. Google AI Studio offers free quotas for Gemini models.

**SERP API Key** (optional, only for the flight assistant): sign up at [SerpApi](https://serpapi.com/) and get your key from the dashboard. The other three agents work without it.

### Environment file

Create `adk/.env` with your credentials:

```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here
SERP_API_KEY=your_serp_api_key_here
```

Never commit this file to version control.

### Node.js (for MCP agents)

The MCP agent and flight assistant use MCP servers that run as Node.js processes. Install Node.js if you do not already have it:

```bash
# macOS
brew install node

# Ubuntu / Debian
sudo apt install nodejs npm

# verify
node --version   # v18+ recommended
```

The multi_tool_agent and google_search_agent do not need Node.js.

## Lab instructions

### Step 1: Multi-tool agent (`adk/multi_tool_agent/`)

The simplest ADK agent. Two Python functions (`get_weather`, `get_current_time`) are passed directly to the `tools` parameter. ADK wraps them as function tools automatically; no decorator or schema needed.

```bash
cd adk
adk web
```

Open `http://localhost:8000`, select **weather_time_agent** from the agent picker, and ask:

> "What is the weather in New York?"

**What to observe:**
- The `tools` list accepts plain Python functions. ADK infers the JSON schema from the type hints and docstring. Compare with lab050 (manual JSON schema) and lab060 (`@function_tool` decorator).
- The functions return mock data. In production you would call a real weather API.
- `adk web` discovers all agent directories automatically; you do not register them anywhere.

### Step 2: Google Search agent (`adk/google_search_agent/`)

Uses the built-in `google_search` tool from `google.adk.tools`. This is a hosted tool: the search runs server-side on Google's infrastructure, similar to OpenAI's `web_search_preview` in lab054.

Still in the `adk web` session, select **basic_search_agent** and ask:

> "What are the latest developments in agentic AI security?"

**What to observe:**
- The `google_search` tool is imported as a module-level object, not instantiated. It can only be the sole tool on an agent (ADK limitation).
- The agent instruction ("stick to the facts") shapes how the model uses the search results. Without it, the model might speculate beyond the retrieved content.
- Compare with lab054 Step 3 (LangChain + Responses API web search): same concept, different framework.

### Step 3: MCP filesystem agent (`adk/mcp_agent/`)

Connects to the `@modelcontextprotocol/server-filesystem` MCP server via `MCPToolset`. The MCP server runs as a child process (via `npx`), and ADK discovers its tools automatically.

Before running, edit `adk/mcp_agent/agent.py` and set `TARGET_FOLDER` to a directory on your machine that you want the agent to access.

Select **filesystem_assistant_agent** in the web UI and ask:

> "List the Python files in this directory."

**What to observe:**
- `MCPToolset` wraps an MCP server and exposes its tools as ADK tools. The agent does not know it is talking to an MCP server; it sees regular function tools.
- `StdioServerParameters` configures the child process (command, args). The MCP server must be available via `npx` or as a local binary.
- The `TARGET_FOLDER` path must be absolute. A common mistake is passing a relative path, which the MCP server cannot resolve.

### Step 4: Flight assistant (`adk/flight_assistant/`)

An MCP agent that connects to `mcp-flight-search`, a third-party MCP server that searches flights via the SerpApi Google Flights API.

Select **flight_assistant_agent** in the web UI and ask:

> "Find flights from San Francisco to Tokyo next month."

This requires `SERP_API_KEY` in your `.env`. Without it the MCP server will fail to start and the agent will have no tools.

**What to observe:**
- Same `MCPToolset` + `StdioServerParameters` pattern as Step 3, but with a different MCP server.
- The `env` parameter passes environment variables to the child process. This is how you inject secrets without hardcoding them.
- If the SERP key is missing, the agent starts but has no tools. Compare with the standalone version (Step 5) which handles this gracefully.

### Step 5: Standalone agent (`adk_standalone/flight_schedule/`)

Runs the same flight search agent without the `adk` CLI. This script uses the ADK Runner API directly: it creates an `InMemorySessionService`, builds a session, and iterates over events from `runner.run_async`.

```bash
cd ../adk_standalone/flight_schedule
python3 agent.py
```

(Run from the lab root if you prefer: `python3 adk_standalone/flight_schedule/agent.py`)

**What to observe:**
- The Runner API gives you programmatic control: create sessions, inject messages, and process events in a loop.
- `runner.run_async` yields events with `content.parts` (text or function calls). This is the Gemini content format (`google.genai.types`).
- If `SERP_API_KEY` is missing, the agent degrades gracefully: it still runs but gives general travel advice instead of live data.
- Compare with `adk web`: the CLI handles all the session management for you, but you lose control over the conversation flow.

### API server

`adk web` also starts a REST API on the same port. Open `http://localhost:8000/docs` for the Swagger UI.

You can interact with agents via curl:

```bash
# Create a session
curl -X POST http://localhost:8000/apps/mcp_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"name": "demo"}}'

# Send a message
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "mcp_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [{"text": "List the files in the current directory"}]
    }
  }'
```

This is useful for integrating ADK agents into other systems, testing from CI, or building custom frontends.

## ADK agent structure

Every agent directory follows the same convention:

```
agent_name/
  __init__.py     # from . import agent
  agent.py        # defines root_agent at module level
```

`adk web` scans subdirectories for modules that export a `root_agent`. See `adk/instructions.md` for templates when creating your own agents.

## Resources

- [Google ADK documentation](https://google.github.io/adk-docs/)
- [ADK quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [ADK sample agents](https://github.com/google/adk-samples)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google AI Studio](https://aistudio.google.com/)

## Cleanup environment

```bash
deactivate
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
