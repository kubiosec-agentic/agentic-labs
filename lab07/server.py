import random
import requests
from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool()
def add(a: int, b: int) -> dict:
    """Add two numbers"""
    print(f"[debug-server] add({a}, {b})")
    return {"result": a + b}


@mcp.tool()
def get_secret_word() -> dict:
    print("[debug-server] get_secret_word()")
    word = random.choice(["apple", "banana", "cherry"])
    return {"secret_word": word}


@mcp.tool()
def get_current_weather(city: str) -> dict:
    print(f"[debug-server] get_current_weather({city})")

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}?format=3")  # shorter response
    return {"weather": response.text.strip()}


if __name__ == "__main__":
    mcp.run(transport="sse")
