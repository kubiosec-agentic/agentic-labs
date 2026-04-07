"""
Security triage agent using the OpenAI Agent SDK (openai-agents).

Demonstrates multi-agent handoffs: a triage agent routes user requests
to one of four specialists (red team, blue team, compliance, file reader).
Each specialist has a focused system prompt that shapes its output format.

Requires: pip install openai-agents
"""

from agents import Agent, Runner, function_tool
import asyncio


# ---- File reader tool ---------------------------------------------------

@function_tool
def read_file(filename: str) -> str:
    """Read the contents of a file in the local directory."""
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {filename}: {e}"


# ---- Specialist agents --------------------------------------------------

file_reader_agent = Agent(
    name="File Reader",
    instructions="You can read the contents of a specified file in the "
                 "local directory.",
    tools=[read_file],
)

red_team_agent = Agent(
    name="Red Team Planner",
    instructions=(
        "You are a responsible red team planner. Provide NON-DESTRUCTIVE, "
        "authorization-assuming guidance:\n"
        "- Plan safe recon and scanning steps only (no exploitation).\n"
        "- Prefer read-only commands with clear scoping flags and rate "
        "limits.\n"
        "- Output format:\n"
        "  1) Objective (short)\n"
        "  2) Scope and Assumptions\n"
        "  3) Safe Plan (ordered steps)\n"
        "  4) Sample Commands (annotated)\n"
        "  5) Expected Artifacts (files/reports)\n"
        "  6) Risk and Safety Notes"
    ),
)

blue_team_agent = Agent(
    name="Blue Team Remediator",
    instructions=(
        "You are a blue team engineer. Provide pragmatic hardening and "
        "remediation:\n"
        "- Prioritize fixes (High/Med/Low).\n"
        "- Include config snippets, detections, log sources, and "
        "validation steps.\n"
        "- Output format:\n"
        "  A) Summary\n"
        "  B) Prioritized Actions\n"
        "  C) Config/Policy Snippets\n"
        "  D) Detection and Logging\n"
        "  E) Validation/Testing"
    ),
)

compliance_agent = Agent(
    name="Compliance Mapper",
    instructions=(
        "You are a security compliance specialist. Map requests to "
        "controls and checklists:\n"
        "- Reference OWASP ASVS sections, CIS Benchmarks, and "
        "ISO/IEC 27001 Annex A when relevant.\n"
        "- Output format:\n"
        "  I) Control Mapping (IDs + short rationale)\n"
        "  II) Minimal Checklist (5-10 items)\n"
        "  III) Evidence to Collect (artifacts/logs)\n"
        "  IV) Pass/Fail Criteria"
    ),
)


# ---- Triage (orchestrator) ----------------------------------------------

triage_agent = Agent(
    name="Security Triage",
    instructions=(
        "Route the user's request to the most appropriate specialist:\n"
        "- Scanning, recon, pentest planning, nmap, zap, burp "
        "-> Red Team Planner.\n"
        "- Patching, hardening, SIEM, detections, alerts, remediation "
        "-> Blue Team Remediator.\n"
        "- Policies, standards, controls, audits, evidence, compliance "
        "-> Compliance Mapper.\n"
        "- Read or analyze a file, mentions a filename "
        "(.json, .txt, .log) -> File Reader.\n\n"
        "If ambiguous, ask ONE clarifying question, then hand off."
    ),
    handoffs=[red_team_agent, blue_team_agent,
              compliance_agent, file_reader_agent],
)


# ---- Demo runner ---------------------------------------------------------

async def main():
    print("\n--- Example 1: Red Team route (safe recon) ---")
    result = await Runner.run(
        triage_agent,
        input=(
            "We just exposed an internal app. Can you plan a safe, "
            "non-destructive recon and give sample nmap + HTTP "
            "fingerprinting commands?"
        ),
    )
    print(result.final_output)

    print("\n--- Example 2: Blue Team route (remediation) ---")
    result = await Runner.run(
        triage_agent,
        input=(
            "We found outdated OpenSSH on several Ubuntu hosts and "
            "weak TLS on our API. How do we remediate and validate?"
        ),
    )
    print(result.final_output)

    print("\n--- Example 3: Compliance route (controls and evidence) ---")
    result = await Runner.run(
        triage_agent,
        input=(
            "We need to show audit readiness for authentication "
            "hardening. Map to OWASP ASVS and give a short checklist "
            "with evidence."
        ),
    )
    print(result.final_output)

    print("\n--- Example 4: File Reader route (analyse result.json) ---")
    result = await Runner.run(
        triage_agent,
        input="Read and analyze the file result.json. Summarize its contents.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
