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
| 3 | `example3/` | MCP servers | YouTube transcriber using remote MCP servers (SSE transport) |
| 4 | `example4/` | Agent chaining | URL fetcher piped into a social media writer via `@fast.chain` |
| 5 | `example5/` | Orchestrator-workers | Planner coordinates finder, writer, and proofreader agents |
| 6 | `example6/` | Security orchestration | 4-agent K8s security auditor with CIS/NSA benchmarks |
| 7 | `example7/` | Memory + MCP | Pentest tutor with OpenMemory MCP for persistent user profiles |

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

### 3. YouTube transcriber (MCP servers)

Connects to two remote MCP servers over SSE: `youtube_transcribe` and
`exa_search`. The agent searches for a video, transcribes it, and
summarizes the content.

Requires extra tokens:

```bash
export YOUTUBE_TRANSCRIBE_TOKEN="..."
export EXA_SEARCH_TOKEN="..."
```

```bash
cd example3 && uv run agent.py
```

### 4. Agent chaining

Two agents wired into a chain with `@fast.chain`:

1. `url_fetcher` retrieves and summarizes a webpage (uses `fetch` MCP server)
2. `social_media` condenses the summary into a 280-character post

```bash
cd example4 && uv run agent.py
```

### 5. Orchestrator-workers

An `author` agent writes a short story, then an orchestrator
coordinates three specialist agents (finder, proofreader, writer) to
review, grade, and fix the text. Uses filesystem and fetch MCP servers.

```bash
cd example5 && uv run agent.py
```

### 6. Kubernetes security auditor

Four-agent orchestration that generates a K8s Pod manifest, audits it
against CIS Benchmarks, NSA/CISA Hardening Guide, and Pod Security
Standards, then produces a remediated manifest and a graded report.

```bash
cd example6 && uv run agent.py
```

### 7. Pentest tutor with OpenMemory

A three-agent chain (greeter, level estimator, tutor) that adapts
teaching difficulty based on the user's skill level. Uses OpenMemory
MCP for persistent user profiles stored in Qdrant.

Requires Docker for the memory backend:

```bash
cd example7
docker compose up -d
uv run pentest_tutor.py
```

## Configuration

Each example has a `fastagent.config.yaml` that defines the default
model, provider API keys (via `${ENV_VAR}` placeholders), and MCP
server configurations. The config supports multiple transports:

- **stdio**: local MCP servers launched as subprocesses (e.g. `npx`, `uvx`)
- **sse**: remote MCP servers accessed over HTTP Server-Sent Events

## Docs

- https://fast-agent.ai/
- https://fast-agent.ai/llms.txt
