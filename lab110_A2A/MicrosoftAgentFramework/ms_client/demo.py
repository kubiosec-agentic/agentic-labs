import asyncio
import httpx

from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient


async def main():
    remote_base_url = "http://localhost:8001/a2a/check_prime_agent"
    card_path = "/.well-known/agent-card.json"

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=remote_base_url)
        agent_card = await resolver.get_agent_card(relative_card_path=card_path)

    remote_agent = A2AAgent(
        name=agent_card.name,
        description=agent_card.description,
        agent_card=agent_card,
        url=remote_base_url,
    )

    # Turn the remote ADK agent into a callable tool for the OpenAI-backed agent
    prime_tool = remote_agent.as_tool(
        name="prime_checker",
        description="Check if one or more integers are prime. Provide the integers in your task.",
    )

    openai_agent = Agent(
        client=OpenAIChatClient(),
        name="ms_openai_agent",
        instructions=(
            "You are a helpful assistant. "
            "If the user asks whether a number is prime or asks to check primes, "
            "call the prime_checker tool. Then summarize the result."
        ),
        tools=prime_tool,
    )

    result = await openai_agent.run("Is 97 prime? If needed, use the prime checker tool.")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
