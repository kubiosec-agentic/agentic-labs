from agents import Agent, Runner, SQLiteSession
import asyncio

# Create agent
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# Create a session instance
session = SQLiteSession("conversation_123")

async def main():
    # First turn
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "What state is it in?",
        session=session
    )
    print(result.final_output)  # "California"

    # Third turn - use async runner for all calls
    result = await Runner.run(
        agent,
        "What's the population?",
        session=session
    )
    print(result.final_output)  # "Approximately 39 million"

if __name__ == "__main__":
    asyncio.run(main())
