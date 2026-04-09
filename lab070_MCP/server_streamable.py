"""
Reference MCP server over streamable HTTP using standalone fastmcp (>=3.2).

Exposes three tools: add, get_secret_word, get_current_weather.

Run:
    python3 server_streamable.py
    # serves MCP at http://0.0.0.0:8000/mcp/
"""
import random
import requests
from fastmcp import FastMCP

mcp = FastMCP("Echo Server", host="0.0.0.0", port=8000)


@mcp.tool()
def add(a: int, b: int) -> dict:
    """Add two numbers."""
    return {"result": a + b}


@mcp.tool()
def get_secret_word() -> dict:
    """Return a secret word from a small fixed list."""
    return {"secret_word": random.choice(["apple", "banana", "cherry"])}


@mcp.tool()
def get_current_weather(city: str) -> dict:
    """Look up the current weather for a city via wttr.in."""
    response = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
    return {"weather": response.text.strip()}


if __name__ == "__main__":
    # "http" is the fastmcp 3.x name for streamable HTTP; "streamable-http"
    # still works as an alias for back-compat with earlier examples.
    mcp.run(transport="http")
