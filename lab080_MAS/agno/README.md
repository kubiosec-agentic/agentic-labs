# Agno

[Agno](https://docs.agno.com/introduction) (formerly PhiData) is a
lightweight Python agent framework with 39k+ GitHub stars. It focuses
on fast agent instantiation, a minimal API surface, and a model-agnostic
design that supports OpenAI, Anthropic, Google, and many others through
a single interface.

Key features relevant to this lab:

- **Teams**: coordinate multiple agents with a shared goal; similar to
  CrewAI's Crew but with less ceremony.
- **Tools**: first-class support for function tools, DuckDuckGo search,
  and MCP servers (hosted or local).
- **Persistent history**: plug in a SQLite (or Postgres) database and
  the agent remembers previous conversations across runs.
- **AgentOS**: optional FastAPI wrapper that turns any agent into a
  REST API with a playground UI (not covered in these exercises).

## Exercises

| Exercise | File | What it covers |
|----------|------|----------------|
| 1 | `AN_01.py` | Multi-agent Team (Researcher + Writer with DuckDuckGo) |
| 2 | `AN_02.py` | Chat history with SQLite persistence |
| 3 | `AN_03_mcp_agent.py` | MCP tool (Agno docs server) with persistent history |

### 1. Multi-agent Team

Creates a Researcher and a Writer agent, groups them in a `Team`, and
asks them to produce an article. The Researcher uses DuckDuckGo for
web search; the Writer synthesizes the findings.

```bash
python3 AN_01.py
```

### 2. Chat history

A single agent with `add_history_to_context=True` backed by a local
SQLite database. Run it, and the agent remembers what you told it in
the same session. The script sends two messages and prints the chat
history after each one.

```bash
python3 AN_02.py
```

### 3. MCP tool with persistent history

Connects to the Agno documentation MCP server
(`https://docs.agno.com/mcp`) so the agent can search the Agno docs
to answer questions. History is stored in SQLite, and the last 3 runs
are included in context automatically.

```bash
python3 AN_03_mcp_agent.py
```

## Docs

- https://docs.agno.com/introduction
- https://docs.agno.com/history/agent/overview
- https://docs.agno.com/tools/mcp
