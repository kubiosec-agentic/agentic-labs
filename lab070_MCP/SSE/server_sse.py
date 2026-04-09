"""
Reference MCP server over SSE using standalone fastmcp (>=3.2).

SSE is the *legacy* transport. The current MCP spec deprecates it in favor
of streamable HTTP, but it is still widely used by existing servers and
clients, so fastmcp still ships it and it is still interoperable. Prefer
streamable HTTP for new work; keep SSE around to connect to older servers.

Run:
    python3 server_sse.py
    # serves MCP at http://127.0.0.1:8000/sse/
"""
import random
import requests
from fastmcp import FastMCP

mcp = FastMCP("Echo Server")


@mcp.tool
def add(a: int, b: int) -> dict:
    """Add two numbers."""
    print(f"[debug-server] add({a}, {b})")
    return {"result": a + b}


@mcp.tool
def get_secret_word() -> dict:
    """Return a secret word from a small fixed list."""
    print("[debug-server] get_secret_word()")
    return {"secret_word": random.choice(["apple", "banana", "cherry"])}


@mcp.tool
def get_current_weather(city: str) -> dict:
    """Look up the current weather for a city via wttr.in."""
    print(f"[debug-server] get_current_weather({city})")
    response = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
    return {"weather": response.text.strip()}


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
