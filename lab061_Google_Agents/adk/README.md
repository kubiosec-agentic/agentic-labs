# ADK Agents

This directory contains four ADK agent modules discovered by `adk web`:

| Directory | Agent | Description |
|-----------|-------|-------------|
| `multi_tool_agent/` | weather_time_agent | Weather and time lookup (mock data, plain Python functions) |
| `google_search_agent/` | basic_search_agent | Web research using the built-in `google_search` tool |
| `mcp_agent/` | filesystem_assistant_agent | File management via MCP filesystem server |
| `flight_assistant/` | flight_assistant_agent | Flight search via MCP flight search server |

See the [lab README](../README.md) for setup instructions and a full walkthrough.

## Quick start

```bash
adk web
```

Open `http://localhost:8000` and pick an agent from the dropdown.

## Creating new agents

See [instructions.md](./instructions.md) for templates and conventions.
