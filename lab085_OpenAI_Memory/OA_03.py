"""
Example 3: Compaction for long conversations.

As conversations grow, the full history can exceed the model's context
window or simply waste tokens. OpenAIResponsesCompactionSession wraps
any session and automatically summarizes older turns once a threshold
is reached. The summary replaces the raw history, keeping the session
small while preserving the important context.

Run:
    python3 OA_03.py
"""

import asyncio
from agents import Agent, Runner, SQLiteSession
from agents.memory import OpenAIResponsesCompactionSession

agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# Wrap a regular SQLiteSession with compaction.
underlying = SQLiteSession("compaction_demo")
session = OpenAIResponsesCompactionSession(
    session_id="compaction_demo",
    underlying_session=underlying,
)


async def main():
    questions = [
        "What is the capital of France?",
        "How many people live there?",
        "What is the most visited monument?",
        "When was it built?",
        "How tall is it?",
        "Summarize everything we discussed so far.",
    ]

    for q in questions:
        print(f"User: {q}")
        result = await Runner.run(agent, q, session=session)
        print(f"Agent: {result.final_output}\n")

    # After compaction, the session holds a summary instead of every
    # raw turn. Retrieve items to see the difference.
    items = await session.get_items()
    print(f"Session items after compaction: {len(items)}")


if __name__ == "__main__":
    asyncio.run(main())
