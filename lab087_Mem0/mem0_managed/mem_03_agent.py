"""
Exercise S3: Multi-turn test of the SaaS memory agent.

Imports the agent from mem_02_saas and runs a sequence of add, search,
and get_all operations to verify end-to-end behavior.

Run:
    export MEM0_API_KEY="your_key"
    python3 mem0_managed/mem_03_agent.py
"""

import asyncio
from mem_02_saas import memory_agent, Mem0Context
from agents import Runner, ItemHelpers, MessageOutputItem, ToolCallItem, ToolCallOutputItem


def print_result(result):
    for item in result.new_items:
        if isinstance(item, MessageOutputItem):
            print("  Assistant:", ItemHelpers.text_message_output(item))
        elif isinstance(item, ToolCallItem):
            print("  Tool called:", item.raw_item.name if hasattr(item.raw_item, "name") else "unknown")
        elif isinstance(item, ToolCallOutputItem):
            print("  Tool result:", item.output)


async def main():
    ctx = Mem0Context(user_id="search-test-user")

    # Store some facts
    print("=== Adding memories ===")
    r1 = await Runner.run(memory_agent, "Remember: I love pizza and Italian food.", context=ctx)
    print_result(r1)

    r2 = await Runner.run(memory_agent, "Also remember: I work as a software engineer.", context=ctx)
    print_result(r2)

    # Search
    print("\n=== Searching ===")
    r3 = await Runner.run(memory_agent, "What do you know about my food preferences?", context=ctx)
    print_result(r3)

    # Get all
    print("\n=== Get all ===")
    r4 = await Runner.run(memory_agent, "What do you know about me?", context=ctx)
    print_result(r4)


if __name__ == "__main__":
    asyncio.run(main())
