"""
Exercise 3: File assistant agent with governance.

A real OpenAI agent with four tools: search_docs, read_file,
execute_shell, and delete_file. The governance policy allows only
the first two. The agent is asked to do something that requires
the blocked tools, and governance stops it mid-conversation.

Requires:
    export OPENAI_API_KEY="sk-..."

Run:
    python3 govern_03.py
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

# --- Governance policy: only read-only tools allowed ---
policy = GovernancePolicy(
    allowed_tools=["search_docs", "read_file"],
    blocked_tools=["execute_shell", "delete_file"],
    blocked_patterns=["rm -rf", "DROP TABLE", "format c:"],
    max_tool_calls=10,
)

kernel = OpenAIAgentsKernel(policy=policy, on_violation=lambda _e: None)
guard = kernel.create_tool_guard()


# --- Tools ---
@function_tool
@guard
async def search_docs(query: str) -> str:
    """Search internal documents for relevant information."""
    return (
        f"Found 3 results for '{query}':\n"
        "  1. security_policy_v3.pdf\n"
        "  2. incident_response_playbook.md\n"
        "  3. access_control_matrix.xlsx"
    )


@function_tool
@guard
async def read_file(path: str) -> str:
    """Read the contents of a file."""
    return f"[Contents of {path}]: This document describes the standard security review process ..."


@function_tool
@guard
async def execute_shell(command: str) -> str:
    """Execute a shell command on the server."""
    return f"Executed: {command}"


@function_tool
@guard
async def delete_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"


# --- Agent ---
file_agent = Agent(
    name="File Assistant",
    instructions=(
        "You are a file assistant. You can search documents, read files, "
        "execute shell commands, and delete files. Use whatever tools are "
        "needed to fulfill the user's request. If a tool call fails, "
        "explain what happened."
    ),
    tools=[search_docs, read_file, execute_shell, delete_file],
)


async def main():
    prompts = [
        "Search for documents about security policies and read the first result.",
        "Delete the file /tmp/old_logs.txt and then run 'ls /tmp' to confirm.",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"  Prompt {i}: {prompt}")
        print("=" * 60)

        try:
            result = await Runner.run(file_agent, prompt)
            print(f"\n  Agent: {result.final_output}")
        except PolicyViolationError as exc:
            print(f"\n  GOVERNANCE BLOCKED: {exc}")
        except Exception as exc:
            print(f"\n  Error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
