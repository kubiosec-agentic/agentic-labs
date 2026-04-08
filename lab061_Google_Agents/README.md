![Google](https://img.shields.io/badge/Google-green) ![ADK](https://img.shields.io/badge/ADK-brightgreen) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB061: Google Agent Development Kit (ADK)

## Introduction

Google's Agent Development Kit (ADK) is a framework for building agents powered by Gemini models. An ADK agent is a Python module that defines a `root_agent` with a model, instructions, and optional tools. The `adk` CLI discovers agents automatically and serves them through a web UI and a REST API.

This lab contains five agents that demonstrate different tool-integration and multi-agent patterns, plus a standalone script that shows how to run an agent programmatically (without the `adk` CLI).

| Directory | Agent | Pattern | Model |
|-----------|-------|---------|-------|
| `adk/multi_tool_agent/` | Weather and time lookup | Plain Python functions as tools | gemini-2.0-flash |
| `adk/mcp_agent/` | Filesystem manager | MCP server integration | gemini-2.0-flash |
| `adk/flight_assistant/` | Flight search | MCP server with API key injection | gemini-2.0-flash |
| `adk/llm_red_team_agent/` | AI safety red team | 3 sub-agents as tools (attack, target, evaluate) | gemini-2.0-flash |
| `adk/cyber_guardian/` | Incident response | 4 sub-agents with transfer mechanism | gemini-2.5-flash |
| `adk_standalone/flight_schedule/` | Flight search (standalone) | Runner API without `adk` CLI | gemini-2.0-flash |
| `adk_standalone/cyber_guardian/` | Incident response (standalone) | Runner API, multi-agent + planner | gemini-2.5-flash |

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

**SERP API Key** (optional, only for the flight assistant): sign up at [SerpApi](https://serpapi.com/) and get your key from the dashboard. All other agents work without it.

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

The multi_tool_agent, llm_red_team_agent, and cyber_guardian do not need Node.js.

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

### Step 2: MCP filesystem agent (`adk/mcp_agent/`)

Connects to the `@modelcontextprotocol/server-filesystem` MCP server via `MCPToolset`. The MCP server runs as a child process (via `npx`), and ADK discovers its tools automatically.

Before running, edit `adk/mcp_agent/agent.py` and set `TARGET_FOLDER` to a directory on your machine that you want the agent to access.

Select **filesystem_assistant_agent** in the web UI and ask:

> "List the Python files in this directory."

**What to observe:**
- `MCPToolset` wraps an MCP server and exposes its tools as ADK tools. The agent does not know it is talking to an MCP server; it sees regular function tools.
- `StdioServerParameters` configures the child process (command, args). The MCP server must be available via `npx` or as a local binary.
- The `TARGET_FOLDER` defaults to `~/Documents`. Note the security comment: defaulting to `~` would expose SSH keys, dotfiles, and other sensitive data. Think about what happens when an agent framework auto-discovers tools that grant filesystem access.

### Step 3: Flight assistant (`adk/flight_assistant/`)

An MCP agent that connects to `mcp-flight-search`, a third-party MCP server that searches flights via the SerpApi Google Flights API.

Select **flight_assistant_agent** in the web UI and ask:

> "Find flights from San Francisco to Tokyo next month."

This requires `SERP_API_KEY` in your `.env`. Without it the agent will refuse to start (clear error message).

**What to observe:**
- Same `MCPToolset` + `StdioServerParameters` pattern as Step 2, but with a different MCP server.
- The `env` parameter passes environment variables to the child process. This is how you inject secrets without hardcoding them.
- The agent validates the SERP key at import time and fails fast with a clear error. Compare with the original version that silently passed an empty string, leading to confusing runtime errors.

### Step 4: LLM Red Team agent (`adk/llm_red_team_agent/`)

An automated adversarial testing pipeline with three sub-agents working as tools. The orchestrator chains them in sequence: generate attack, simulate target response, evaluate.

Select **security_orchestrator** in the web UI and ask:

> "Test the target for Prompt Injection vulnerabilities."

Or try other risk categories: "PII Leakage", "Financial Advice", "AML", "Toxicity".

**What to observe:**
- The pipeline has three stages, each running a separate sub-agent: a Red Team agent (temperature 0.9, creative attacks), a Target banking chatbot (temperature 0.1, strict safety rules), and an Evaluator (temperature 0.0, deterministic JSON verdict).
- Each sub-agent runs in an isolated session via `ThreadPoolExecutor` to prevent context leakage between attacker and target. This mimics a real-world stateless API call.
- The safety constitution in `safety_rules.py` defines the rules the target must follow. The evaluator grades against these same rules. Try modifying the constitution and observe how the verdicts change.
- The orchestrator uses temperature 0.0 for reliable tool chaining. Compare with the red team agent's 0.9 for creative diversity.
- Retry logic (`tenacity`) handles 429 rate limits automatically.
- Read `config.py` to see how different models can be assigned to different roles. In production, you might use a stronger model for evaluation and a cheaper one for the target.

Based on [google/adk-samples/ai-security-agent](https://github.com/google/adk-samples/tree/main/python/agents/ai-security-agent) (Apache 2.0).

### Step 5: Cyber Guardian (`adk/cyber_guardian/`)

A multi-agent incident response system with 4 specialized sub-agents orchestrated by a planner that uses Gemini's extended thinking capability.

Select **cyber_guardian_orchestrator** in the web UI and paste this alert:

> "ALERT: IOC_MATCH detected on host srv-web-prod-01 by user svc-apache. Outbound connection to 185.220.101.42:443 flagged by network IDS. Process: certutil.exe downloading from 185.220.101.42."

**What to observe:**
- The orchestrator delegates to 4 sub-agents: **triage** (deduplication, asset enrichment), **threat intel** (IOC lookup), **investigation** (process trees, network logs), and **response** (playbook selection, action execution).
- The orchestrator delegates to sub-agents via ADK's transfer mechanism. The model decides which sub-agent to call next based on the instruction, rather than following a hardcoded sequence.
- Each sub-agent uses `output_key` to store its results in a shared state, allowing downstream agents to access upstream findings.
- The mock tools in `tools.py` return realistic incident data (Cobalt Strike C2, certutil abuse, lateral movement indicators). In production, these would query BigQuery, a SIEM, or a SOAR platform.
- The response agent flags actions that `requires_approval: true` (e.g., host isolation), demonstrating the Human-In-The-Loop (HITL) pattern for high-impact actions.
- Try submitting the same alert twice. The triage agent should detect the duplicate and stop processing.

Based on [google/adk-samples/cyber-guardian-agent](https://github.com/google/adk-samples/tree/main/python/agents/cyber-guardian-agent) (Apache 2.0).

### Step 6: Standalone agent (`adk_standalone/flight_schedule/`)

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
- The `mcp-flight-search` server writes debug logs to stdout, which the MCP client tries (and fails) to parse as JSON-RPC. These "Failed to parse JSONRPC message" errors are harmless; the client skips bad lines and still connects. The script suppresses them by raising the log level for `mcp.client.stdio`. If you see them when using `adk web`, they can be safely ignored.
- You may also see a deprecation warning about `StdioServerParameters`. ADK is migrating to `StdioConnectionParams`, but both work at the time of writing.
- If you hit a 429 RESOURCE_EXHAUSTED error, wait a minute. The free Google AI Studio tier has per-minute rate limits that reset quickly.

### Step 7: Standalone Cyber Guardian (`adk_standalone/cyber_guardian/`)

Same multi-agent incident response pipeline as Step 5, but running from the command line without `adk web`. Everything is in a single file: mock tools, sub-agents, orchestrator, and the Runner loop.

```bash
cd ../adk_standalone/cyber_guardian
python3 agent.py
```

The script ships with a sample IOC_MATCH alert (Cobalt Strike C2 via certutil on srv-web-prod-01). You can override it with the `ALERT_TEXT` environment variable:

```bash
ALERT_TEXT="ALERT: EDR_DETECTION on ws-dev-042. Process tree: w3wp.exe -> powershell.exe -> cmd.exe. Suspicious encoded command detected." python3 agent.py
```

**What to observe:**
- Compare the output with Step 5 (`adk web` version). The agent reasoning and tool calls are the same, but here you see them as raw events from `runner.run_async`.
- Watch how the orchestrator decides which sub-agent to delegate to at each step based on the alert classification.
- The standalone version gives you full control over the conversation loop: you could inject follow-up messages, branch on tool results, or feed the output into another system.
- No external dependencies needed. Only `google-adk` and `python-dotenv`.

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

For multi-agent architectures (llm_red_team_agent, cyber_guardian), the pattern extends with `sub_agents/` directories containing specialized agents, shared `tools.py`, and configuration/prompt modules.

## Resources

- [Google ADK documentation](https://google.github.io/adk-docs/)
- [ADK quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [ADK sample agents](https://github.com/google/adk-samples)
- [ADK Python source](https://github.com/google/adk-python)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google AI Studio](https://aistudio.google.com/)

## Cleanup environment

```bash
deactivate
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
