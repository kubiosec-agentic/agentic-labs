"""
Exercise 4: sub-agents and context isolation.

The `task` tool lets the main agent delegate a job to a sub-agent that runs
with its OWN message history. Only the sub-agent's final answer comes back,
as one tool result. Two consequences:

  1. Context hygiene: a sub-agent can read 40 files and burn 80k tokens, the
     parent only pays for the summary. This is the core trick behind every
     "deep research" or "coding agent" product.
  2. Blast radius: a sub-agent gets exactly the tools, model, permissions and
     system prompt you declare. Least privilege per role becomes a config
     option instead of an architecture project.

Below: a read-only `code-reviewer` (optionally on a cheaper model) and a
`fixer` that is the only one allowed to write. The parent keeps the file
tools (the harness does not let you remove them without also dropping the
top-level permissions) but every call it makes is denied, so it has to
delegate. The general-purpose sub-agent still exists; it inherits the
parent's rules.

Finding baked into this file: FilesystemPermission patterns are matched
without DOTGLOB, so "/**" does NOT cover /.env. A first version of this
exercise denied "/**" and the model happily listed and read /.env. See
EVERYTHING in common.py.
"""

import os
from pathlib import Path

from deepagents import FilesystemPermission, SubAgent, create_deep_agent
from deepagents.backends import FilesystemBackend

from common import DEFAULT_MODEL, EVERYTHING, get_model, print_stream, require_key

require_key()

ROOT = Path(__file__).parent / "workspace"
backend = FilesystemBackend(root_dir=ROOT, virtual_mode=True)

reviewer: SubAgent = {
    "name": "code-reviewer",
    "description": "Reads source files and reports concrete security findings with file and line. Read-only.",
    "system_prompt": (
        "You are a strict application security reviewer. Read the files you are "
        "asked about with read_file and return a numbered list of findings: "
        "file:line, weakness, one-line fix. No fixes applied, no chatter."
    ),
    # Sub-agent permissions REPLACE the parent's rules, so restate the secret rule.
    "permissions": [
        FilesystemPermission(operations=["read", "write"], paths=["/.env", "/**/.env"], mode="deny"),
        FilesystemPermission(operations=["write"], paths=EVERYTHING, mode="deny"),
    ],
    # A cheaper/faster model for the noisy job. Any provider:model string works,
    # e.g. DA_REVIEWER_MODEL="openai:gpt-4o-mini" or "ollama:qwen3:8b".
    "model": get_model(os.environ.get("DA_REVIEWER_MODEL", DEFAULT_MODEL)),
}

fixer: SubAgent = {
    "name": "fixer",
    "description": "Applies a specific, already-decided code change to one file using edit_file.",
    "system_prompt": (
        "You apply exactly the change you are given, using edit_file, then read "
        "the file back and confirm in one sentence. Do not refactor anything else."
    ),
    "permissions": [
        FilesystemPermission(operations=["read", "write"], paths=["/.env", "/**/.env"], mode="deny"),
        FilesystemPermission(operations=["write"], paths=["/app.py"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=EVERYTHING, mode="deny"),
    ],
}

agent = create_deep_agent(
    model=get_model(),
    backend=backend,
    subagents=[reviewer, fixer],
    system_prompt=(
        "You are a lead engineer. You have NO working file access of your own: "
        "every ls/read_file/glob/grep/edit you attempt is denied by policy. "
        "Delegate reading and reviewing to the code-reviewer sub-agent and "
        "edits to the fixer sub-agent, using the task tool, then report."
    ),
    permissions=[
        # Experiment: change EVERYTHING to ["/**"] and ask the parent to read /.env.
        FilesystemPermission(operations=["read", "write"], paths=EVERYTHING, mode="deny"),
    ],
)

print("== Run ==")
print_stream(
    agent.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Have /app.py reviewed for injection issues, then have the most "
                        "serious one fixed. Finish with a two-line report."
                    ),
                }
            ]
        },
        stream_mode="updates",
    )
)

print(
    "\nWhat to notice: the parent's stream shows only `task` calls and their "
    "results. The reviewer's read_file calls never entered the parent's context. "
    "Check workspace/app.py: the fixer's edit is real. Re-run reset_workspace.sh to undo it."
)
