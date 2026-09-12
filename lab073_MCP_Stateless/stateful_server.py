"""
State WITHOUT server-side sessions (Exercise 4).

The 2026-07-28 spec era is sessionless: the transport no longer keeps a
per-connection session for you. That does not mean agents can never be
stateful. It means state has to be modelled explicitly, as data that
travels in tool arguments, instead of hidden inside the transport.

This one server shows both approaches side by side so you can feel the
difference:

  1. The WRONG way for a scaled deployment: a module-global counter.
     It "works" on a single process, but the moment you run two replicas
     behind a load balancer, each replica has its own counter and the
     numbers are nonsense. The state lives in one process's memory.

  2. The RIGHT way: the explicit-handle pattern. `open_cart()` returns an
     unguessable id. The client passes that id back as an argument on
     every follow-up call. The server looks the state up by id. Here the
     store is an in-memory dict for the demo, but in production it would
     be Redis/Postgres/etc., shared by every replica, so any replica can
     serve any request. State travels as an ordinary tool argument.

Read the security note in the README: because the handle is now a normal
tool argument, it shows up in logs, traces, and your mitmproxy capture.
An id that grants access to state is a credential, and this pattern puts
credentials on the wire in plain sight.

Run:
    python3 stateful_server.py   # streamable HTTP on :8101/mcp
"""
import sys
import secrets

from fastmcp import FastMCP

mcp = FastMCP("Stateful Patterns Server")

# ---- 1. Naive global state (breaks across replicas) -----------------------

_global_counter = 0


@mcp.tool
def increment() -> dict:
    """Increment a process-global counter and return it.

    Anti-pattern for a scaled deployment: this number is per-process, so
    two replicas will disagree. Run two copies of this server and call
    increment() against each to see the divergence.
    """
    global _global_counter
    _global_counter += 1
    return {"counter": _global_counter, "note": "per-process, not shared"}


# ---- 2. Explicit-handle pattern (scales; state travels as an argument) ----

# In production this dict is Redis/Postgres, shared by all replicas.
_carts: dict[str, list[str]] = {}


@mcp.tool
def open_cart() -> dict:
    """Create a new cart and return its handle (an unguessable id)."""
    cart_id = "cart_" + secrets.token_urlsafe(12)
    _carts[cart_id] = []
    return {"cart_id": cart_id}


@mcp.tool
def add_item(cart_id: str, item: str) -> dict:
    """Add an item to the cart named by `cart_id`."""
    if cart_id not in _carts:
        return {"error": "unknown cart_id"}
    _carts[cart_id].append(item)
    return {"cart_id": cart_id, "items": _carts[cart_id]}


@mcp.tool
def view_cart(cart_id: str) -> dict:
    """Return the contents of the cart named by `cart_id`."""
    if cart_id not in _carts:
        return {"error": "unknown cart_id"}
    return {"cart_id": cart_id, "items": _carts[cart_id]}


if __name__ == "__main__":
    port = 8101
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
    mcp.run(transport="http", host="127.0.0.1", port=port)
