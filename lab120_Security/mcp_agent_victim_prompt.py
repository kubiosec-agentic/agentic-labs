"""
LAB 120 - Exercise 9c: Injection via MCP Prompt Resources
============================================================

WHAT THIS IS:
  MCP servers can expose "prompts" as a first-class primitive alongside
  tools and resources. Clients discover them with list_prompts(), fetch
  them with get_prompt(), and use the returned messages as model input.

  This is a DIFFERENT attack surface than tool-output poisoning:
    - Tools:   agent calls tool -> gets data back -> reasons about it
    - Prompts: agent fetches a prompt template -> uses it AS its input

  If a server defines a prompt, it controls what the model does.
  The agent has no system prompt of its own for this interaction;
  the MCP prompt IS the instruction.

THE ATTACK:
  The MCP server exposes three prompts:
    1. summarize_brief(topic)          -- clean
    2. literature_review(topic)        -- clean
    3. reproduce_methodology(topic)    -- POISONED for one topic

  When the agent fetches reproduce_methodology("capability_escalation"),
  the returned prompt instructs the model to "reproduce the experimental
  protocol as JSON with executable shell commands." The model receives
  this as its working instruction, not as data to analyze.

HOW TO RUN:
  Terminal 1:  python3 mcp_server_injection.py
  Terminal 2:  python3 mcp_agent_victim_prompt.py

WHAT TO OBSERVE:
  Step 1: The agent lists prompts (clean operation, shows 3 prompts)
  Step 2: The agent uses summarize_brief("llm_alignment") -- clean result
  Step 3: The agent uses reproduce_methodology("capability_escalation")
          -- this is where the injection fires

COMPARE WITH:
  - mcp_agent_victim.py: injection via tool responses (agent reasons about data)
  - This exercise: injection via prompt resources (server defines the instruction)
"""

import asyncio
from openai import OpenAI
from fastmcp import Client

openai_client = OpenAI()

MCP_URL = "http://localhost:8000/mcp"


async def main():
    async with Client(MCP_URL) as client:

        # ── Step 1: List available prompts ─────────────────────────
        print("=" * 70)
        print("STEP 1: List available MCP prompts")
        print("=" * 70)

        prompts = await client.list_prompts()
        for p in prompts:
            print(f"  - {p.name}: {p.description}")

        # ── Step 2: Use a clean prompt ─────────────────────────────
        print()
        print("=" * 70)
        print("STEP 2: Use 'summarize_brief' prompt (clean)")
        print("=" * 70)

        clean_result = await client.get_prompt(
            "summarize_brief",
            arguments={"topic": "llm_alignment"},
        )

        # The prompt result contains messages we send to the model
        clean_messages = [
            {"role": msg.role, "content": msg.content.text}
            for msg in clean_result.messages
        ]

        print(f"  Prompt role: {clean_messages[0]['role']}")
        print(f"  Prompt text: {clean_messages[0]['content'][:120]}...")
        print()

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=clean_messages,
        )
        print("  Model response (clean):")
        print(f"  {response.choices[0].message.content[:300]}...")

        # ── Step 3: Use the poisoned prompt ────────────────────────
        print()
        print("=" * 70)
        print("STEP 3: Use 'reproduce_methodology' prompt")
        print("        with topic 'capability_escalation'")
        print("        (this is where the injection happens)")
        print("=" * 70)

        poisoned_result = await client.get_prompt(
            "reproduce_methodology",
            arguments={"topic": "capability_escalation"},
        )

        poisoned_messages = [
            {"role": msg.role, "content": msg.content.text}
            for msg in poisoned_result.messages
        ]

        print(f"  Prompt role: {poisoned_messages[0]['role']}")
        print(f"  Prompt preview: {poisoned_messages[0]['content'][:150]}...")
        print()

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=poisoned_messages,
        )

        print("  Model response (poisoned prompt):")
        print(response.choices[0].message.content)

        # ── Analysis ───────────────────────────────────────────────
        print()
        print("=" * 70)
        print("ANALYSIS")
        print("=" * 70)
        print()
        print("Compare Step 2 (clean) vs Step 3 (poisoned):")
        print()
        print("  Step 2: The model received a normal summarization prompt")
        print("  and produced a summary. No injection.")
        print()
        print("  Step 3: The model received a 'reproduce methodology' prompt")
        print("  that contains the pentest plan instructions embedded in")
        print("  what looks like an academic methodology section.")
        print()
        print("KEY DIFFERENCE FROM TOOL INJECTION (mcp_agent_victim.py):")
        print("  With tools, the agent gets data and REASONS about it.")
        print("  The agent could theoretically detect the injection.")
        print()
        print("  With prompts, the server DEFINES THE INSTRUCTION.")
        print("  There is no reasoning step. The prompt IS the task.")
        print("  The model has no basis to question it because the")
        print("  prompt came from the MCP protocol, same as any other.")
        print()
        print("DEFENSE:")
        print("  - Audit MCP servers before connecting to them")
        print("  - Pin prompt versions (detect changes)")
        print("  - Require human review of MCP prompt content")
        print("  - Apply output guardrails regardless of prompt source")


if __name__ == "__main__":
    asyncio.run(main())
