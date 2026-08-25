"""
A2A Bidirectional Conversation Demo
=====================================

This demo shows a multi-turn conversation between a Microsoft Agent
Framework (OpenAI) client and a Google ADK (Gemini) server via A2A.

The conversation flows back and forth:
  1. MS agent asks ADK agent to check if numbers are prime
  2. Based on the response, MS agent asks a follow-up
  3. ADK agent responds with more analysis
  4. MS agent synthesizes all results

Each round trip crosses the A2A protocol boundary:
  MS (OpenAI) --[A2A HTTP]--> ADK (Gemini) --[A2A HTTP]--> MS (OpenAI)

This demonstrates:
  - Multi-turn task conversations over A2A
  - Agent card discovery and tool wrapping
  - Cross-vendor interoperability (OpenAI + Gemini)
  - The agent reasoning about remote tool results
"""

import asyncio
import httpx

from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent
from agent_framework import Agent, AgentSession
from agent_framework.openai import OpenAIChatClient


async def main():
    # ── Discover the remote ADK agent ─────────────────────────────
    remote_base_url = "http://localhost:8001/a2a/check_prime_agent"
    card_path = "/.well-known/agent-card.json"

    print("=" * 60)
    print("A2A Bidirectional Conversation Demo")
    print("MS Agent Framework (OpenAI) <-> Google ADK (Gemini)")
    print("=" * 60)
    print()

    print("[Discovery] Resolving remote agent card...")
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(
            httpx_client=http_client, base_url=remote_base_url
        )
        agent_card = await resolver.get_agent_card(
            relative_card_path=card_path
        )

    print(f"[Discovery] Found: {agent_card.name} - {agent_card.description}")
    print(f"[Discovery] Skills: {[s.name for s in agent_card.skills]}")
    print()

    # ── Wrap remote agent as a tool ───────────────────────────────
    remote_agent = A2AAgent(
        name=agent_card.name,
        description=agent_card.description,
        agent_card=agent_card,
        url=remote_base_url,
    )

    prime_tool = remote_agent.as_tool(
        name="prime_checker",
        description=(
            "Check if one or more integers are prime. "
            "Provide the integers in your task."
        ),
    )

    # ── Create the local OpenAI-backed agent ──────────────────────
    openai_agent = Agent(
        client=OpenAIChatClient(),
        name="ms_openai_agent",
        instructions=(
            "You are a math research assistant. "
            "When you need to check if numbers are prime, use the "
            "prime_checker tool. You can call it multiple times. "
            "Always explain your reasoning and build on previous results."
        ),
        tools=prime_tool,
    )

    # ── Multi-turn conversation ───────────────────────────────────
    # Each message triggers the MS agent, which may call the remote
    # ADK agent via A2A, creating a cross-vendor conversation.

    conversation = [
        {
            "turn": 1,
            "label": "Initial query",
            "message": (
                "I'm looking at the first 10 numbers after 100. "
                "Which of them are prime? Check 101 through 110."
            ),
        },
        {
            "turn": 2,
            "label": "Follow-up based on results",
            "message": (
                "Interesting. For each prime you found, check if "
                "adding 2 to it also gives a prime (twin prime pairs). "
                "Use the prime checker tool for the verification."
            ),
        },
        {
            "turn": 3,
            "label": "Deeper analysis",
            "message": (
                "Now check the Mersenne candidates: 2^2-1=3, 2^3-1=7, "
                "2^5-1=31, 2^7-1=127, 2^11-1=2047, 2^13-1=8191. "
                "Which of these are actually prime? Use the tool to verify."
            ),
        },
        {
            "turn": 4,
            "label": "Synthesis",
            "message": (
                "Based on all the checks we've done, summarize: "
                "how many total numbers did we check, how many were prime, "
                "and what patterns did we observe?"
            ),
        },
    ]

    # An AgentSession carries the conversation history. Without it every
    # run() starts from an empty history, so turn 2 cannot see turn 1's
    # results and turn 4 has nothing to synthesise ("I don't have access
    # to past interactions"). Create it once, pass it to every run().
    session = AgentSession()

    for step in conversation:
        print("-" * 60)
        print(f"Turn {step['turn']}: {step['label']}")
        print(f"User: {step['message']}")
        print("-" * 60)

        result = await openai_agent.run(step["message"], session=session)
        print(f"\nAgent: {result.text}")
        print()

    print("=" * 60)
    print("Demo complete.")
    print()
    print("What happened:")
    print("  - 4 conversation turns between user and MS agent")
    print("  - MS agent (OpenAI) called ADK agent (Gemini) via A2A")
    print("  - Each prime_checker call crossed the A2A protocol boundary")
    print("  - Results accumulated across turns (conversational memory)")
    print("  - Two different LLM vendors collaborated seamlessly")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
