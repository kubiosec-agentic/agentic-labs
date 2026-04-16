"""
Exercise 4: Interactive chat with persistent memory.

Like exercise 3, but as an interactive loop.  The agent stores facts
you share and recalls them on request.  Quit with 'exit' or 'quit'.

Because memories live in Qdrant, you can stop the script, restart it,
and the agent still remembers everything.

Run:
    python3 mem_04.py
"""

from __future__ import annotations
import asyncio
from dataclasses import dataclass

from mem0 import Memory
from agents import (
    Agent,
    Runner,
    function_tool,
    RunContextWrapper,
)

# --- Context ---
@dataclass
class Mem0Context:
    user_id: str = "demo-user"


# --- Mem0 client (Qdrant backend) ---
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0",
        },
    },
    "llm": {
        "provider": "openai_structured",
        "config": {"model": "gpt-4o-2024-08-06", "temperature": 0.0},
    },
}

MEM0 = Memory.from_config(config)


# --- Memory tools (same as exercise 3) ---
@function_tool
def add_to_memory(ctx: RunContextWrapper[Mem0Context], content: str) -> str:
    """Store a fact in Mem0."""
    uid = ctx.context.user_id
    resp = MEM0.add([{"role": "user", "content": content}], user_id=uid)
    return f"Saved {len(resp) if isinstance(resp, list) else 1} item(s)."


@function_tool
def search_memory(ctx: RunContextWrapper[Mem0Context], query: str) -> str:
    """Search facts in Mem0 relevant to the query."""
    uid = ctx.context.user_id
    res = MEM0.search(query, filters={"user_id": uid})
    items = res if isinstance(res, list) else res.get("results", [])
    memories = [it.get("memory", str(it)) for it in items]
    return "\n".join(memories) if memories else "(no matches)"


@function_tool
def get_all_memory(ctx: RunContextWrapper[Mem0Context]) -> str:
    """Return all stored facts for this user."""
    uid = ctx.context.user_id
    res = MEM0.get_all(filters={"user_id": uid})
    items = res if isinstance(res, list) else res.get("results", [])
    memories = [it.get("memory", str(it)) for it in items]
    return "\n".join(memories) if memories else "(empty)"


# --- Agent ---
memory_agent = Agent[Mem0Context](
    name="Memory Assistant",
    instructions=(
        "You have access to three memory tools:\n"
        "- add_to_memory: store a fact the user shares.\n"
        "- search_memory: find relevant facts.\n"
        "- get_all_memory: list everything stored for this user.\n\n"
        "Always call the appropriate tool first, then give a concise answer.\n"
        "When the user shares personal info, store it automatically."
    ),
    tools=[add_to_memory, search_memory, get_all_memory],
)


async def main():
    name = input("What is your name? ").strip() or "anonymous"
    ctx = Mem0Context(user_id=name)

    print(f"\nSession for '{name}' (memories stored in Qdrant)")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            user_input = input(f"{name}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break

        result = await Runner.run(memory_agent, user_input, context=ctx)
        print(f"Assistant: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
