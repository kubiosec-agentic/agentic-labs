"""
A tiny fastmcp 4.x client used across the lab.

It connects to any MCP server over streamable HTTP, prints the tools it
exposes, and calls a couple of them. The interesting flag is --mode:

    --mode auto     (default) negotiate the modern, sessionless 2026-07-28
                    era. This is what a fresh fastmcp 4.x client does out of
                    the box.
    --mode legacy   negotiate the older, session-based era (2025-11-25),
                    i.e. behave the way a fastmcp 3.x client did.

Run it in both modes against the same server, with mitmproxy in front
(Exercise 5), and compare the initialize handshake and the mcp-session-id
header on the wire.

The `mode=` argument only exists on the fastmcp 4.x Client. On a 3.x
client this script would raise TypeError, which is itself the point of the
lab: the client API changed between generations.

Usage:
    python3 client_demo.py                              # :8100, auto
    python3 client_demo.py --url http://127.0.0.1:8100/mcp --mode legacy
"""
import sys
import asyncio

from fastmcp import Client


def _arg(name: str, default: str) -> str:
    for a in sys.argv[1:]:
        if a.startswith(f"--{name}="):
            return a.split("=", 1)[1]
        if a == f"--{name}" and sys.argv.index(a) + 1 < len(sys.argv):
            return sys.argv[sys.argv.index(a) + 1]
    return default


async def main() -> None:
    url = _arg("url", "http://127.0.0.1:8100/mcp")
    mode = _arg("mode", "auto")

    print(f"Connecting to {url}  (mode={mode})")
    client = Client(url, mode=mode)

    async with client as c:
        init = getattr(c, "initialize_result", None)
        # fastmcp 4.x renamed this field from protocolVersion -> protocol_version,
        # another small example of the churn this lab is about.
        proto = getattr(init, "protocol_version", None) if init else None
        print(f"Negotiated protocol era: {proto}")

        tools = await c.list_tools()
        print("Tools:", [t.name for t in tools])

        names = {t.name for t in tools}
        if "add" in names:
            r = await c.call_tool("add", {"a": 7, "b": 5})
            print("add(7, 5) ->", getattr(r, "data", r))
        if "celsius_to_fahrenheit" in names:
            r = await c.call_tool("celsius_to_fahrenheit", {"celsius": 21})
            print("celsius_to_fahrenheit(21) ->", getattr(r, "data", r))


if __name__ == "__main__":
    asyncio.run(main())
