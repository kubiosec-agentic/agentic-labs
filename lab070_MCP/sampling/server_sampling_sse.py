"""Sampling demo: MCP server over SSE. Same tools as the HTTP version.

SSE is kept for compatibility with older clients. See
server_sampling_http.py for inline notes on how sampling works.
"""
import random
from fastmcp import FastMCP, Context

mcp = FastMCP("Sampling Demo (SSE)", host="0.0.0.0", port=8000)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def get_secret_word_0() -> str:
    """Return a secret word."""
    return random.choice(["Hacked", "Pwnd", "Trouble"])


@mcp.tool()
def pay_amount_0() -> str:
    """Amount to pay."""
    return random.choice(["100", "200", "300", "400"])


@mcp.tool()
def available_balance_0() -> str:
    """Available balance."""
    return "200"


@mcp.tool()
async def analyze_sentiment(text: str, ctx: Context) -> dict:
    """Classify sentiment via client-side sampling."""
    prompt = (
        "Analyze the sentiment as positive, negative, or neutral. "
        f"Text: {text}"
    )
    response = await ctx.sample(prompt, model_preferences="claude-3-sonnet")
    reply = response.text.strip().lower()
    if "positive" in reply:
        sentiment = "positive"
    elif "negative" in reply:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"text": text, "sentiment": sentiment}


if __name__ == "__main__":
    mcp.run(transport="sse")
