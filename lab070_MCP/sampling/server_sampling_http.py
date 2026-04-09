"""
Sampling demo: MCP server over streamable HTTP.

Sampling is the MCP feature that lets a *server-side tool* ask the
*client* to run an LLM call on its behalf. The tool calls `ctx.sample(...)`,
the server forwards a `sampling/createMessage` request back through the
open session to the client, and the client's `sampling_handler` produces
the completion. This inverts the usual direction (client calls model, then
calls tools) and it is the piece of MCP that makes tool-backed reasoning
possible without the server holding any model credentials.

Run:
    python3 server_sampling_http.py
    # serves MCP at http://0.0.0.0:8000/mcp/
"""
import random
from fastmcp import FastMCP, Context

mcp = FastMCP("Sampling Demo", host="0.0.0.0", port=8000)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    print(f"[server] add({a}, {b})")
    return a + b


@mcp.tool()
def get_secret_word_0() -> str:
    """Return a secret word from a small fixed list."""
    print("[server] get_secret_word_0()")
    return random.choice(["Hacked", "Pwnd", "Trouble"])


@mcp.tool()
def pay_amount_0() -> str:
    """Amount to pay."""
    print("[server] pay_amount_0()")
    return random.choice(["100", "200", "300", "400"])


@mcp.tool()
def available_balance_0() -> str:
    """Available balance."""
    print("[server] available_balance_0()")
    return "200"


@mcp.tool()
async def analyze_sentiment(text: str, ctx: Context) -> dict:
    """
    Classify a piece of text as positive, negative, or neutral.

    Implementation note: the server does *not* call an LLM directly. It
    asks the connected client to do the inference via `ctx.sample(...)`.
    The client is free to use whichever model and provider it likes, and
    the server never sees the client's model credentials.
    """
    prompt = (
        "Analyze the sentiment as positive, negative, or neutral. "
        f"Text: {text}"
    )
    response = await ctx.sample(prompt, model_preferences="claude-3-sonnet")
    print(f"[server] sampling response: {response.text!r}")
    reply = response.text.strip().lower()
    if "positive" in reply:
        sentiment = "positive"
    elif "negative" in reply:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"text": text, "sentiment": sentiment}


if __name__ == "__main__":
    mcp.run(transport="http")
