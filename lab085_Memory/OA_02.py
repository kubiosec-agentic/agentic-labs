from agents import Agent, Runner, SQLiteSession
import asyncio

# Custom SQLite database file
session = SQLiteSession("user_123", "conversations.db")
agent = Agent(name="Assistant")

async def main():
    # Different session IDs maintain separate conversation histories
    result1 = await Runner.run(
        agent,
        "Hello",
        session=session
    )
    print(result1.final_output)

    result2 = await Runner.run(
        agent,
        "Hello",
        session=SQLiteSession("user_456", "conversations.db")
    )
    print(result2.final_output)

if __name__ == "__main__":
    asyncio.run(main())
