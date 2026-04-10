"""
Example 4: Session history operations.

This example shows how to inspect and manipulate session contents
directly: retrieve items, limit history, and clear sessions. Useful
for debugging and for building custom memory management on top of the
session API.

Run:
    python3 OA_04.py
"""

import asyncio
from agents import Agent, Runner, SQLiteSession, RunConfig


agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)


async def main():
    session = SQLiteSession("ops_demo", "ops_demo.db")

    # Seed a few turns
    for q in ["Hello!", "What is 2+2?", "And 3+3?"]:
        await Runner.run(agent, q, session=session)

    # --- Retrieve all items ---
    items = await session.get_items()
    print(f"Total items in session: {len(items)}\n")

    # --- Limit history with SessionSettings ---
    # Only feed the last 2 items as context (useful for long sessions)
    from agents import SessionSettings

    result = await Runner.run(
        agent,
        "What numbers did we just add?",
        session=session,
        run_config=RunConfig(
            session_settings=SessionSettings(limit=2),
        ),
    )
    print(f"With limit=2: {result.final_output}\n")

    # --- Pop the last item ---
    last = await session.pop_item()
    print(f"Popped last item (type={type(last).__name__})")

    # --- Clear the session ---
    await session.clear_session()
    items = await session.get_items()
    print(f"Items after clear: {len(items)}")

    # Clean up the demo database
    import os
    os.remove("ops_demo.db")
    print("\nDone. Database removed.")


if __name__ == "__main__":
    asyncio.run(main())
