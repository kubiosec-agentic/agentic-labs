"""
Trigger lab070's sampling tool under fastmcp 4.x (Exercise 2).

lab070's sampling server (sampling/server_sampling_http.py) exposes an
`analyze_sentiment` tool whose body calls `await ctx.sample(...)`, the
server-initiated back-channel that asks the client to run an LLM call.

fastmcp 4.x REMOVED `ctx.sample` from the server Context (the 2026-07-28
era has no server-initiated back-channel). So the tool raises, at call
time, on unchanged server code:

    'Context' object has no attribute 'sample'

This probe connects to that server and calls the tool. It registers a
canned sampling handler so NO OpenAI key is needed: we are demonstrating
the protocol break, not doing real inference. If sampling still worked,
the handler would just return the word "positive". Instead you should see
the AttributeError surfaced as a tool error, which is exactly why lab070
pins fastmcp==3.4.7.

Start lab070's sampling server first, in this venv (fastmcp 4.x):
    cd ../lab070_MCP && python3 sampling/server_sampling_http.py
Then, in another terminal (this venv):
    python3 sampling_probe.py
"""
import sys
import asyncio

from fastmcp import Client


async def canned_sampling_handler(messages, params, context):
    # Never actually reached on fastmcp 4.x: ctx.sample is gone, so the
    # server never issues a sampling/createMessage request.
    return "positive"


async def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/mcp"
    print(f"Connecting to {url} and calling analyze_sentiment ...")
    client = Client(url, sampling_handler=canned_sampling_handler)
    async with client as c:
        try:
            r = await c.call_tool("analyze_sentiment", {"text": "I love this lab"})
            print("Sampling WORKED (you are on fastmcp 3.x):", getattr(r, "data", r))
        except Exception as e:
            print("Sampling FAILED (expected on fastmcp 4.x):")
            print(f"  {type(e).__name__}: {str(e)[:200]}")
            print("\nThis is why lab070 pins fastmcp==3.4.7. See the compatibility")
            print("matrix in the README.")


if __name__ == "__main__":
    asyncio.run(main())
