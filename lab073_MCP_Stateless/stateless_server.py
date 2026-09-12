"""
A genuinely STATELESS MCP server (Exercise 3).

Every tool here is a pure function: its output depends only on its input
arguments, and nothing is remembered between calls. There is no module
state, no session, no database. That property is what makes a server
"stateless" in the sense the 2026-07-28 MCP spec cares about.

Why it matters: a stateless server can run behind a load balancer as N
identical replicas. Any replica can serve any request because there is
nothing to keep in sync. No sticky sessions, no shared cache, no session
affinity. This is the model the modern MCP transport is optimised for.

Run:
    python3 stateless_server.py               # streamable HTTP on 127.0.0.1:8100/mcp
    python3 stateless_server.py --stdio       # stdio transport instead
    python3 stateless_server.py --host 0.0.0.0  # bind all interfaces (mitmproxy demo)

The default binds loopback only. The mitmproxy exercise (README section 6)
runs the proxy in Docker, which must reach this server over the host LAN IP,
so start it there with --host 0.0.0.0.
"""
import sys
from fastmcp import FastMCP

mcp = FastMCP("Stateless Math Server")


@mcp.tool
def add(a: float, b: float) -> dict:
    """Add two numbers."""
    return {"result": a + b}


@mcp.tool
def multiply(a: float, b: float) -> dict:
    """Multiply two numbers."""
    return {"result": a * b}


@mcp.tool
def celsius_to_fahrenheit(celsius: float) -> dict:
    """Convert a temperature from Celsius to Fahrenheit."""
    return {"celsius": celsius, "fahrenheit": celsius * 9 / 5 + 32}


if __name__ == "__main__":
    if "--stdio" in sys.argv:
        mcp.run(transport="stdio")
    else:
        host = "127.0.0.1"
        for arg in sys.argv[1:]:
            if arg.startswith("--host="):
                host = arg.split("=", 1)[1]
            elif arg == "--host" and sys.argv.index(arg) + 1 < len(sys.argv):
                host = sys.argv[sys.argv.index(arg) + 1]
        mcp.run(transport="http", host=host, port=8100)
