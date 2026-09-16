"""
Exercise 2: add a simple skill (instructions only).

A skill does not have to be code. The `incident-note` skill is one SKILL.md:
front matter (name, description) plus a procedure telling the model exactly
how to format a finding. We bolt the skill pattern onto the Agents SDK by
hand (see skills_runtime.py):

  - build_instructions() injects each skill's name+description into the system
    prompt (the model sees the menu, not the whole cookbook).
  - the read_skill tool lets the model pull the full SKILL.md when a task
    matches (progressive disclosure).

Compare with lab066, where deepagents did all of this for you. Here it is
about 30 lines you can read.

NOTE: this is the SAME agent and the SAME skill loader as agent_03. Both see
both skills on the menu (incident-note and http-header-audit) and both carry
the same tools (read_skill / read_reference / run_skill_script). The only
difference between the two exercises is the prompt. This prompt is an
incident-note task, so the model judges its way to the instruction-only skill.
Hand this same agent the header-audit prompt and it would behave like
agent_03. The prompt selects the skill; the agent does not change.

Run (needs OPENAI_API_KEY):
    python3 agent_02_simple_skill.py
"""

import asyncio
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

from common import MODEL, disable_tracing, require_key
from skills_runtime import SKILL_TOOLS, build_instructions, discover_skills

HERE = Path(__file__).parent


async def main() -> None:
    disable_tracing()
    require_key()

    print("Skills on the menu:", [s["dir"] for s in discover_skills()])

    async with MCPServerStdio(
        name="lab078",
        params={"command": sys.executable, "args": [str(HERE / "mcp_server.py")], "cwd": str(HERE)},
        cache_tools_list=True,
        client_session_timeout_seconds=15,
    ) as server:
        agent = Agent(
            name="SOC assistant",
            model=MODEL,
            instructions=build_instructions(
                "You are a SOC assistant. Use MCP tools for data and skills for procedures."
            ),
            tools=SKILL_TOOLS,          # read_skill / read_reference / run_skill_script
            mcp_servers=[server],
        )

        # A task that should trigger the incident-note skill: the model should
        # read_skill('incident-note') and emit the exact fields it specifies.
        result = await Runner.run(
            agent,
            "Record this as an incident note: the login page at https://portal.example "
            "is served over plain HTTP with no HSTS header.",
        )
        print("\n--- final output ---")
        print(result.final_output)
        print(
            "\nExpected: the model called read_skill('incident-note') and produced "
            "Title / Severity / Evidence / Impact / Recommendation, not a freeform blurb."
        )


if __name__ == "__main__":
    asyncio.run(main())
