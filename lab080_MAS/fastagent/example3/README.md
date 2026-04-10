# Example 3: Microsoft Learn MCP Agent

Connects to the Microsoft Learn documentation MCP server using
streamable HTTP transport. The agent can search and query Microsoft
documentation to answer technical questions.

## What it demonstrates

- Remote MCP server over **streamable HTTP** (not SSE, not stdio)
- Minimal config: just `transport: "http"` and a URL
- No API tokens needed; Microsoft Learn MCP is a public endpoint

## Run

```bash
cd example3
uv run agent.py
```

## Configuration

The `fastagent.config.yaml` defines one MCP server:

```yaml
mcp:
  servers:
    mslearn:
      transport: "http"
      url: "https://learn.microsoft.com/api/mcp"
```

This is the simplest possible remote MCP setup: a single URL with no
authentication headers.
