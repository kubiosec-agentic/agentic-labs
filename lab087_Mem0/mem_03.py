"""
Exercise 3: OpenAI agent with Mem0 memory tools.

Combines the OpenAI Agents SDK with Mem0 by exposing three function
tools: add_to_memory, search_memory, and get_all_memory.  The agent
decides when to store or retrieve facts based on the user's message.

This is a single-shot example.  Exercise 4 turns it into an
interactive chat loop.

Run:
    python3 mem_03.py
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
    ItemHelpers,
    MessageOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
)

# --- Context: carries the user_id so tools know whose memories to use ---
@dataclass
class Mem0Context:
    user_id: str = "alice"


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


# --- Memory tools ---
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


# --- Agent definition ---
memory_agent = Agent[Mem0Context](
    name="Memory Assistant",
    instructions=(
        "You have access to three memory tools:\n"
        "- add_to_memory: store a fact the user shares.\n"
        "- search_memory: find relevant facts.\n"
        "- get_all_memory: list everything stored for this user.\n\n"
        "Always call the appropriate tool first, then give a concise answer."
    ),
    tools=[add_to_memory, search_memory, get_all_memory],
)


async def main():
    ctx = Mem0Context(user_id="alice")

    # The agent should search memory and suggest a movie
    result = await Runner.run(
        memory_agent,
        "Suggest a movie based on what you know about me.",
        context=ctx,
    )

    for item in result.new_items:
        if isinstance(item, MessageOutputItem):
            print("Assistant:", ItemHelpers.text_message_output(item))
        elif isinstance(item, ToolCallItem):
            print("Tool called:", item.raw_item.name if hasattr(item.raw_item, "name") else "unknown")
        elif isinstance(item, ToolCallOutputItem):
            print("Tool result:", item.output)


if __name__ == "__main__":
    asyncio.run(main())
