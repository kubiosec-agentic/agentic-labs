"""
Exercise S2: OpenAI agent with Mem0 SaaS backend.

Same agent pattern as exercise 3 (self-hosted), but backed by
MemoryClient instead of a local Qdrant.  The v2 API is used
throughout to avoid deprecation warnings.

Run:
    export MEM0_API_KEY="your_key"
    python3 mem0_managed/mem_02_saas.py
"""

from __future__ import annotations
import asyncio
import warnings
from dataclasses import dataclass

warnings.filterwarnings("ignore", category=DeprecationWarning)

from mem0 import MemoryClient
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


@dataclass
class Mem0Context:
    user_id: str = "demo-user"


MEM0 = MemoryClient()


@function_tool
def add_to_memory(ctx: RunContextWrapper[Mem0Context], content: str) -> str:
    """Store a fact in Mem0 (SaaS)."""
    uid = ctx.context.user_id
    resp = MEM0.add(
        [{"role": "user", "content": content}],
        user_id=uid,
        version="v2",
        output_format="v1.1",
    )
    return f"Saved {len(resp) if isinstance(resp, list) else 1} item(s)."


@function_tool
def search_memory(ctx: RunContextWrapper[Mem0Context], query: str) -> str:
    """Search facts in Mem0 (SaaS) relevant to the query."""
    uid = ctx.context.user_id
    res = MEM0.search(query, version="v2", filters={"user_id": uid})
    items = res if isinstance(res, list) else res.get("results", [])
    memories = [it.get("memory", str(it)) for it in items]
    return "\n".join(memories) if memories else "(no matches)"


@function_tool
def get_all_memory(ctx: RunContextWrapper[Mem0Context]) -> str:
    """Return all stored facts for this user (SaaS)."""
    uid = ctx.context.user_id
    res = MEM0.get_all(version="v2", filters={"user_id": uid})
    items = res if isinstance(res, list) else res.get("results", [])
    memories = [it.get("memory", str(it)) for it in items]
    return "\n".join(memories) if memories else "(empty)"


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
    ctx = Mem0Context(user_id="demo-user")
    result = await Runner.run(
        memory_agent, "My name is Philippe. Store it.", context=ctx
    )

    for item in result.new_items:
        if isinstance(item, MessageOutputItem):
            print("Assistant:", ItemHelpers.text_message_output(item))
        elif isinstance(item, ToolCallItem):
            print(
                "Tool called:",
                item.raw_item.name if hasattr(item.raw_item, "name") else "unknown",
            )
        elif isinstance(item, ToolCallOutputItem):
            print("Tool result:", item.output)


if __name__ == "__main__":
    asyncio.run(main())
