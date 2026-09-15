"""
lab078 MCP server (stdio, fastmcp).

Two tools:
  add(a, b)        a trivial tool, so the baseline agent has something to call.
  http_get(url)    fetch a URL and return status + response headers + a short
                   body snippet. This is the capability the http-header-audit
                   skill builds on: the MCP server does the I/O, the skill's
                   script does the grading.

Run it directly to sanity-check (Ctrl+D to exit the handshake):
    python3 mcp_server.py
Normally you do NOT run it yourself. The agent spawns it over stdio via
MCPServerStdio (see agent_01_mcp.py).

Security note (this is a security course): http_get is an SSRF primitive. An
agent that exposes it will fetch whatever URL it is told to, including
169.254.169.254 (cloud metadata) or an internal 10.x address. A real
deployment allow-lists destinations. This lab leaves it open on purpose so
you can see the exposure; agent_03 and the README discuss it.
"""

import requests
from fastmcp import FastMCP

mcp = FastMCP("lab078-server")

# Cap the body we return so a large page cannot blow up the agent's context.
MAX_BODY = 2000


@mcp.tool
def add(a: int, b: int) -> dict:
    """Add two integers and return the sum."""
    return {"result": a + b}


@mcp.tool
def http_get(url: str) -> dict:
    """Fetch a URL with a GET request and return its status code, response
    headers, and the first part of the body. Use this to inspect a site's
    HTTP response, for example to audit its security headers."""
    resp = requests.get(url, timeout=10, allow_redirects=True)
    return {
        "url": resp.url,
        "status": resp.status_code,
        # Header names are case-insensitive on the wire; normalise to a plain
        # dict with the casing the server sent.
        "headers": dict(resp.headers),
        "body_snippet": resp.text[:MAX_BODY],
    }


if __name__ == "__main__":
    # show_banner=False keeps fastmcp's startup banner off stderr so the lab
    # output stays clean. stdio is the transport MCPServerStdio speaks.
    mcp.run(transport="stdio", show_banner=False)
