"""
Exercise 5: the `execute` tool, sandboxed vs not.

The harness always offers `execute`. Whether it does anything depends on the
backend:

  StateBackend / FilesystemBackend  -> execute returns an error (no runtime)
  LocalShellBackend                 -> runs on YOUR machine, as YOU
  a SandboxBackendProtocol impl     -> runs wherever you say (here: Docker)

Run the same three probes against both. The difference is the whole point of
the word "sandbox": with LocalShellBackend, virtual_mode and every
FilesystemPermission rule from Exercise 2 are decoration, because
`cat ../../.env` does not go through the file tools.

    python3 da_05_sandbox.py docker    # default
    python3 da_05_sandbox.py local     # unsandboxed, with human approval

Needs a working `docker` CLI for the docker mode (see lab000 get-docker.sh).
"""

import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from common import get_model, print_stream, require_key
from docker_sandbox import DockerSandbox

require_key()
MODE = sys.argv[1] if len(sys.argv) > 1 else "docker"
ROOT = Path(__file__).parent / "workspace"

PROBES = (
    "Run these shell commands one at a time and report each result verbatim:\n"
    "1. id && hostname\n"
    "2. cat /work/.env 2>/dev/null || cat .env 2>/dev/null || echo 'no .env here'\n"
    "3. cat /etc/hostname; ls / | head\n"
    "4. python3 -c \"import urllib.request;print(urllib.request.urlopen('http://example.com',timeout=3).status)\" 2>&1 | tail -1\n"
    "Then: write a file report.txt containing the four results and read it back."
)

if MODE == "docker":
    backend = DockerSandbox()           # network=none, read-only root, nobody, cap-drop ALL
    print(f"Sandbox container: {backend.id}")
    agent = create_deep_agent(
        model=get_model(),
        backend=backend,
        system_prompt="You are a build engineer with a shell. Report command output exactly.",
    )
    try:
        print_stream(agent.stream({"messages": [{"role": "user", "content": PROBES}]}, stream_mode="updates"))
    finally:
        backend.close()
        print("Container removed.")

elif MODE == "local":
    # Unsandboxed. The only thing standing between the model and your shell
    # is the human-in-the-loop interrupt on every execute call.
    backend = LocalShellBackend(root_dir=ROOT, virtual_mode=True)
    agent = create_deep_agent(
        model=get_model(),
        backend=backend,
        system_prompt="You are a build engineer with a shell. Report command output exactly.",
        interrupt_on={"execute": True},
        checkpointer=InMemorySaver(),   # interrupts need a checkpointer to resume
    )
    config = {"configurable": {"thread_id": "local-shell-demo"}}
    stream = agent.stream({"messages": [{"role": "user", "content": PROBES}]}, config=config, stream_mode="updates")
    while True:
        interrupted = None
        for update in stream:
            if "__interrupt__" in update:
                interrupted = update["__interrupt__"][0].value
                break
            print_stream([update])
        if interrupted is None:
            break
        # interrupted is a HITLRequest: {"action_requests": [...], "review_configs": [...]}
        # The model may emit several execute calls in one turn; the resume
        # needs exactly one decision per hanging call, in order.
        decisions = []
        for req in interrupted["action_requests"]:
            print(f"\n  >>> agent wants to run: {req['args'].get('command')}")
            answer = input("  approve? [y/N] ").strip().lower()
            decisions.append({"type": "approve"} if answer == "y" else {"type": "reject", "message": "Denied by operator."})
        stream = agent.stream(Command(resume={"decisions": decisions}), config=config, stream_mode="updates")
else:
    sys.exit("usage: da_05_sandbox.py [docker|local]")

print(
    "\nCompare: in docker mode `id` is nobody, there is no .env, / is the image, "
    "and the HTTP probe fails (network=none). In local mode every probe succeeds "
    "unless you said no, and the answer to probe 2 is your fake secret."
)
