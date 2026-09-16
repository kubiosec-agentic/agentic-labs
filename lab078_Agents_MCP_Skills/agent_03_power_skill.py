"""
Exercise 3: a powerful skill (SKILL.md + script + reference).

The `http-header-audit` skill is the interesting case: it composes all three
building blocks of this lab.

  - MCP tool http_get(url)  does the network fetch (the side effect).
  - the skill's script audit_headers.py  grades the headers (deterministic,
    offline, testable) via run_skill_script.
  - the skill's reference grading.md  holds the per-header knowledge, read on
    demand via read_reference.

The model orchestrates them by following SKILL.md: fetch, grade, explain,
report. None of that logic lives in this file; it lives in the skill. Swap in
a different skill folder and the same agent does a different job.

NOTE: the agent here is IDENTICAL to agent_02. Same skill loader, same tools,
same menu. What changed is the prompt: this one is a header-audit task, so the
model judges its way to the skill that ships a script and a reference and runs
the full fetch/grade/explain sequence. This prompt also asks for an incident
note at the end, so the model chains into the incident-note skill too. The
"advanced" part is the skill the prompt selects, not the agent.

Run (needs OPENAI_API_KEY, and outbound network for the fetch):
    python3 agent_03_power_skill.py
    python3 agent_03_power_skill.py https://github.com
"""

import asyncio
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

from common import MODEL, disable_tracing, require_key
from skills_runtime import SKILL_TOOLS, build_instructions

HERE = Path(__file__).parent


async def main() -> None:
    disable_tracing()
    require_key()

    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

    async with MCPServerStdio(
        name="lab078",
        params={"command": sys.executable, "args": [str(HERE / "mcp_server.py")], "cwd": str(HERE)},
        cache_tools_list=True,
        client_session_timeout_seconds=15,
    ) as server:
        agent = Agent(
            name="AppSec assistant",
            model=MODEL,
            instructions=build_instructions(
                "You are an application-security assistant. When a task matches a skill, "
                "read it and follow its steps exactly. Prefer the skill's script over your "
                "own judgement for anything the script covers."
            ),
            tools=SKILL_TOOLS,
            mcp_servers=[server],
        )

        result = await Runner.run(
            agent,
            f"Audit the HTTP security headers of {target} and give me the grade, the "
            f"weakest headers, and record the overall result as an incident note.",
        )
        print("\n--- final output ---")
        print(result.final_output)
        print(
            "\nExpected tool sequence: http_get (MCP) -> read_skill('http-header-audit') "
            "-> run_skill_script(audit_headers.py) -> maybe read_reference('grading.md') "
            "-> read_skill('incident-note'). Fetch, grade, explain, report: four files, "
            "one agent."
        )


if __name__ == "__main__":
    asyncio.run(main())
