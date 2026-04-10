# FastAgent

[FastAgent](https://fast-agent.ai/) is an MCP-native agent framework.
Every tool is an MCP server, and the framework handles transport,
retries, and session management. It supports agent chaining (output of
one agent feeds into the next) and orchestrator patterns (a planner
agent coordinates specialist workers).

FastAgent uses `uv` (not pip) for dependency management and runs in
its own virtual environment, separate from the lab080 venv.

## Prerequisites

```bash
export OPENAI_API_KEY="sk-..."
```

Install `uv` if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup (one time, from this directory)

```bash
uv venv
uv init --bare
uv add fast-agent-mcp
```

## Running examples

Run from within an example directory:

```bash
cd example1
uv run agent.py
```

All examples use `openai.gpt-4o` as the default model, configured in
each example's `fastagent.config.yaml`.

## Exercises

| # | Directory | Pattern | What it covers |
|---|-----------|---------|----------------|
| 1 | `example1/` | Interactive agent | Simplest FastAgent; starts an interactive chat session |
| 2 | `example2/` | Remote instructions | Agent loads instructions from a URL; XSS education use case |
| 3 | `example3/` | Streamable HTTP MCP | Microsoft Learn docs agent via remote MCP (no tokens needed) |

### 1. Interactive agent

The "hello world" of FastAgent. Creates an agent with a single
instruction and starts an interactive prompt.

```bash
cd example1 && uv run agent.py
```

### 2. Remote instructions (XSS education)

Loads the agent's instruction from a remote URL using Pydantic's
`AnyUrl`. Demonstrates how instructions can live outside the codebase.

```bash
cd example2 && uv run agent.py
```

### 3. Microsoft Learn MCP (streamable HTTP)

Connects to the Microsoft Learn documentation MCP server over
streamable HTTP. The agent discovers available tools from the MCP
server and uses them to answer documentation questions. No extra
tokens needed; the endpoint is public.

```bash
cd example3 && uv run agent.py
```

The config is minimal:

```yaml
mcp:
  servers:
    mslearn:
      transport: "http"
      url: "https://learn.microsoft.com/api/mcp"
```

## Configuration

Each example has a `fastagent.config.yaml` that defines the default
model, provider API keys (via `${ENV_VAR}` placeholders), and MCP
server configurations. The config supports multiple transports:

- **stdio**: local MCP servers launched as subprocesses (e.g. `npx`, `uvx`)
- **http**: remote MCP servers over streamable HTTP (recommended for new projects)
- **sse**: remote MCP servers over Server-Sent Events (legacy)

## Docs

- https://fast-agent.ai/
- https://fast-agent.ai/llms.txt
