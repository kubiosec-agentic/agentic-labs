# FastAgent

[FastAgent](https://fast-agent.ai/) is an MCP-native agent framework.
Every tool is an MCP server, and the framework handles transport,
retries, and session management. It supports agent chaining (output of
one agent feeds into the next) and orchestrator patterns (a planner
agent coordinates specialist workers).

FastAgent uses `uv` (not pip) for dependency management and runs in
its own virtual environment, separate from the lab080 venv.

> These examples are written for `fast-agent-mcp` 0.10.x, which
> **requires Python 3.12+**. As of 0.10 the package was renamed
> internally from `mcp_agent` to `fast_agent`, so the import is now
> `from fast_agent import FastAgent` (older `from mcp_agent...`
> imports no longer work).

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
uv venv --python 3.12
uv init --bare
uv add "fast-agent-mcp==0.10.24"
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
| 4 | `example4/` | Orchestrator + local MCP | 4-agent K8s security auditor with filesystem and fetch MCP servers |

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

### 4. Kubernetes security auditor (orchestrator + local MCP)

Four agents: a generator creates a baseline NGINX Pod manifest, then
an orchestrator coordinates a reviewer (audits against CIS, NSA/CISA,
Pod Security Standards), a remediator (fixes the manifest), and a
writer (saves everything to disk). Uses two local MCP servers:
`filesystem` (disk I/O) and `fetch` (pulls benchmark docs from URLs).
No tokens needed.

```bash
cd example4 && uv run agent.py
```

Check `./manifests/` for the generated report and fixed YAML.

## Exposing agents over MCP (agent-as-server)

FastAgent runs in both directions. Everything above *consumes* MCP
servers, but a FastAgent app can also *be* an MCP server: each
`@fast.agent` (and orchestrators) is published as a callable MCP tool,
so another MCP client (Claude Desktop, an IDE, or another agent) can
drive it. This is built on FastMCP under the hood.

Two ways to do it, both on `fast-agent-mcp` 0.10.x:

Run one of the example scripts as a server. Passing `--transport`
switches it into server mode:

```bash
# stdio: what Claude Desktop and most MCP clients speak
uv run agent.py --transport stdio

# streamable HTTP
uv run agent.py --transport http --host 127.0.0.1 --port 8000
```

Or use the dedicated CLI (serves the agents defined in the current
directory's config):

```bash
uv run fast-agent serve --transport stdio
uv run fast-agent serve --transport http --port 8000
```

MCP transports are `stdio` and `http`. (The `acp` and `a2a` transport
options are separate agent-to-agent protocols, not classic MCP.)

To wire an agent into Claude Desktop, point an `mcpServers` entry at the
script over stdio:

```json
{
  "mcpServers": {
    "fastagent-demo": {
      "command": "uv",
      "args": ["run", "agent.py", "--transport", "stdio"],
      "cwd": "/absolute/path/to/lab080_MAS/fastagent/example1"
    }
  }
}
```

> [SECURITY] Serving an agent over MCP turns the agent itself into an
> exposed attack surface: its instruction, its tools, and any MCP
> servers it in turn connects to are now reachable by whatever client
> calls it. Treat it like any other MCP endpoint (auth, network scope,
> tool allow-listing) and revisit the MCP security labs (lab070, lab071,
> lab073) with the agent now sitting on the server side of the boundary.

## Configuration

Each example has a `fastagent.config.yaml` that defines the default
model, provider API keys (via `${ENV_VAR}` placeholders), and MCP
server configurations. The config supports multiple transports:

- **stdio**: local MCP servers launched as subprocesses (e.g. `npx`, `uvx`)
- **http**: remote MCP servers over streamable HTTP (recommended for new projects)
- **sse**: remote MCP servers over Server-Sent Events (legacy)

## Docs

- https://fast-agent.ai/
