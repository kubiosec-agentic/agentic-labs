"""
Exercise 2: Interactive chat with persistent sessions (SQLite).

The agent asks for your name and uses it as the session ID. If you
come back with the same name, the conversation continues where you
left off. A different name starts a fresh session. All sessions are
stored in a local SQLite database.

Prerequisites:
    export OPENAI_API_KEY="sk-..."

Run:
    python3 OA_02.py
"""

from agents import Agent, Runner, SQLiteSession
import asyncio

DB_FILE = "conversations.db"

agent = Agent(
    name="Assistant",
    instructions=(
        "You are a friendly assistant. Remember what the user told you "
        "in previous messages and refer back to it naturally."
    ),
)


async def main():
    name = input("What is your name? ").strip()
    if not name:
        name = "anonymous"

    session = SQLiteSession(name, DB_FILE)
    print(f"\nSession: {name} (stored in {DB_FILE})")
    print("Type 'exit' or 'quit' to end the conversation.\n")

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

        result = await Runner.run(agent, user_input, session=session)
        print(f"Assistant: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
