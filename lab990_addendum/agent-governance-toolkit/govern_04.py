"""
Exercise 4: Security analyst agent with governance.

A security-themed agent with four tools: scan_ports, read_logs,
deploy_patch, and wipe_server. Governance allows the read-only
tools and blocks the destructive ones. The agent is asked to
investigate and then remediate, and governance draws the line.

Requires:
    export OPENAI_API_KEY="sk-..."

Run:
    python3 govern_04.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# --- AGT imports ---
_REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_REPO_ROOT))

from agent_os.integrations.openai_agents_sdk import (
    GovernancePolicy,
    OpenAIAgentsKernel,
    PolicyViolationError,
)

# --- OpenAI Agents SDK imports ---
from agents import Agent, Runner, function_tool

# --- Governance policy: investigate yes, remediate no ---
policy = GovernancePolicy(
    allowed_tools=["scan_ports", "read_logs"],
    blocked_tools=["deploy_patch", "wipe_server"],
    blocked_patterns=["dd if=/dev/zero", "mkfs", "shutdown"],
    max_tool_calls=10,
)

kernel = OpenAIAgentsKernel(policy=policy, on_violation=lambda _e: None)
guard = kernel.create_tool_guard()


# --- Tools ---
@function_tool
@guard
async def scan_ports(target: str) -> str:
    """Scan open ports on a target host."""
    return (
        f"Port scan results for {target}:\n"
        "  22/tcp   open   ssh\n"
        "  80/tcp   open   http\n"
        "  443/tcp  open   https\n"
        "  8080/tcp open   http-alt  (suspicious)\n"
        "  9090/tcp open   unknown   (suspicious)"
    )


@function_tool
@guard
async def read_logs(service: str) -> str:
    """Read recent log entries for a service."""
    return (
        f"Last 5 log entries for '{service}':\n"
        "  [WARN]  Unusual outbound traffic to 185.143.x.x\n"
        "  [ERROR] Authentication failure from 10.0.0.99 (3 attempts)\n"
        "  [WARN]  Port 8080 serving unrecognized binary\n"
        "  [INFO]  SSL certificate valid until 2026-12-01\n"
        "  [ERROR] Kernel module loaded: rootkit_detector flagged suspicious"
    )


@function_tool
@guard
async def deploy_patch(patch_id: str) -> str:
    """Deploy a security patch to the server."""
    return f"Patch {patch_id} deployed successfully."


@function_tool
@guard
async def wipe_server(target: str, confirm: bool = False) -> str:
    """Wipe and reimage a compromised server."""
    return f"Server {target} wiped and reimaged."


# --- Agent ---
sec_agent = Agent(
    name="Security Analyst",
    instructions=(
        "You are a security analyst. You can scan ports, read logs, "
        "deploy patches, and wipe compromised servers. Investigate the "
        "situation first, then take remediation action. If a tool call "
        "fails, explain what happened and recommend next steps."
    ),
    tools=[scan_ports, read_logs, deploy_patch, wipe_server],
)


async def main():
    prompts = [
        "Investigate host 10.0.0.42: scan its ports and check the nginx logs.",
        "The host looks compromised. Deploy patch CVE-2026-1234 and wipe the server.",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"  Prompt {i}: {prompt}")
        print("=" * 60)

        try:
            result = await Runner.run(sec_agent, prompt)
            print(f"\n  Agent: {result.final_output}")
        except PolicyViolationError as exc:
            print(f"\n  GOVERNANCE BLOCKED: {exc}")
        except Exception as exc:
            print(f"\n  Error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
