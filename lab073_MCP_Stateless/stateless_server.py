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
    python3 stateless_server.py          # streamable HTTP on :8100/mcp
    python3 stateless_server.py --stdio  # stdio transport instead
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
        mcp.run(transport="http", host="127.0.0.1", port=8100)
