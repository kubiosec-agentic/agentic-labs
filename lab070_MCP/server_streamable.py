import random
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo Server", host="0.0.0.0", port=8000)

@mcp.tool()
def add(a: int, b: int) -> dict:
    return {"result": a + b}

@mcp.tool()
def get_secret_word() -> dict:
    word = random.choice(["apple", "banana", "cherry"])
    return {"secret_word": word}

@mcp.tool()
def get_current_weather(city: str) -> dict:
    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}?format=3")
    return {"weather": response.text.strip()}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
