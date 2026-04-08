"""
Multi-agent language handoff.

A triage agent inspects the user's input language and hands off to
either a Spanish-speaking or English-speaking agent. Demonstrates
the handoffs parameter and automatic routing.
"""

from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, como estas?")
    print(result.final_output)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
