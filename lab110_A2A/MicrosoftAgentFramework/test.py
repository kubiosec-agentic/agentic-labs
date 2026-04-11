"""
Quick test: verify that the A2A agent card is reachable.
Run this before demo.py to check connectivity.
"""

import asyncio
import httpx
from a2a.client import A2ACardResolver


async def main():
    remote_base_url = "http://localhost:8001/a2a/check_prime_agent"
    card_path = "/.well-known/agent-card.json"

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(
            httpx_client=http_client, base_url=remote_base_url
        )
        card = await resolver.get_agent_card(relative_card_path=card_path)

    print(f"Agent: {card.name}")
    print(f"Description: {card.description}")
    print(f"URL: {remote_base_url}")
    print(f"Skills: {[s.name for s in card.skills]}")
    print("Agent card OK.")


if __name__ == "__main__":
    asyncio.run(main())
