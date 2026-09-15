"""
Exercise 3: skills (progressive disclosure).

A skill is a directory with a SKILL.md: YAML front matter (name, description)
plus a procedure. At startup the harness reads only the front matter of every
skill and puts a one-line index into the system prompt. The model reads the
full file with read_file *when a task matches*. That is how a coding agent
carries hundreds of procedures without paying for them in every prompt.

skills/port-triage/SKILL.md is a small triage playbook. The scan it applies
it to is workspace/scan.txt. Skills are loaded through the backend, so the
paths below are backend paths (root_dir is this lab directory).
"""

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from common import get_model, print_stream, require_key, trace_prompt

require_key()

HERE = Path(__file__).parent
backend = FilesystemBackend(root_dir=HERE, virtual_mode=True)

agent = create_deep_agent(
    model=get_model(),
    backend=backend,
    skills=["/skills/"],  # every sub-directory with a SKILL.md becomes a skill
    system_prompt="You are a network security analyst.",
    middleware=[trace_prompt("skills")],
)

# What the model sees before it reads anything is only name + description of
# each skill. Run with DA_TRACE=1 to print the assembled system prompt and
# find the "Available Skills" block.
print("\n== Run ==")
print_stream(
    agent.stream(
        {"messages": [{"role": "user", "content": "Triage the scan in /workspace/scan.txt."}]},
        stream_mode="updates",
    )
)
print("\nExpected sequence: read_file(/skills/port-triage/SKILL.md) -> read_file(/workspace/scan.txt) -> write_file(/triage/portal.lab.internal.md)")
print("Open triage/ in this directory to see the table the skill produced.")
