from agents import Agent, Runner
import asyncio

# --- Specialist agents ---

red_team_agent = Agent(
    name="Red-Team Planner",
    instructions="""
You are a responsible red-team planner. Provide NON-DESTRUCTIVE, authorization-assuming guidance:
- Plan safe recon and scanning steps only (no exploitation).
- Prefer read-only commands with clear scoping flags and rate limits.
- Output format:
  1) Objective (short)
  2) Scope & Assumptions
  3) Safe Plan (ordered steps)
  4) Sample Commands (annotated)
  5) Expected Artifacts (files/reports)
  6) Risk & Safety Notes
""",
)

blue_team_agent = Agent(
    name="Blue-Team Remediator",
    instructions="""
You are a blue-team engineer. Provide pragmatic hardening and remediation:
- Prioritize fixes (High/Med/Low).
- Include config snippets, detections, log sources, and validation steps.
- Output format:
  A) Summary
  B) Prioritized Actions
  C) Config/Policy Snippets
  D) Detection & Logging
  E) Validation/Testing
""",
)

compliance_agent = Agent(
    name="Compliance Mapper",
    instructions="""
You are a security compliance specialist. Map requests to controls and checklists:
- Reference OWASP ASVS sections, CIS Benchmarks, and ISO/IEC 27001 Annex A when relevant.
- Output format:
  I) Control Mapping (IDs + short rationale)
  II) Minimal Checklist (5–10 items)
  III) Evidence to Collect (artifacts/logs)
  IV) Pass/Fail Criteria
""",
)

# --- Orchestrator with handoffs ---

triage_agent = Agent(
    name="Security Triage",
    instructions="""
Route the user's request to the most appropriate specialist:
- If the user asks about scanning, recon, “how to test,” “nmap,” “zap,” “burp,” or pentest planning → Red-Team Planner.
- If they ask about patching, hardening, SIEM, detections, alerts, or “how to fix” → Blue-Team Remediator.
- If they ask about policies, standards, controls, audits, evidence, or compliance frameworks → Compliance Mapper.

If ambiguous, ask ONE clarifying question, then hand off.
""",
    handoffs=[red_team_agent, blue_team_agent, compliance_agent],
)

# --- Demo runner ---

async def main():
    print("\n--- Example 1: Red-Team route (safe recon) ---")
    result = await Runner.run(
        triage_agent,
        input="We just exposed an internal app. Can you plan a safe, non-destructive recon and give sample nmap + HTTP fingerprinting commands?"
    )
    print(result.final_output)

    print("\n--- Example 2: Blue-Team route (remediation) ---")
    result = await Runner.run(
        triage_agent,
        input="We found outdated OpenSSH on several Ubuntu hosts and weak TLS on our API. How do we remediate and validate?"
    )
    print(result.final_output)

    print("\n--- Example 3: Compliance route (controls & evidence) ---")
    result = await Runner.run(
        triage_agent,
        input="We need to show audit readiness for authentication hardening. Map to OWASP ASVS and give a short checklist with evidence."
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
