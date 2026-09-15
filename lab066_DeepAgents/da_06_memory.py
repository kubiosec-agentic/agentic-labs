"""
Exercise 6: memory (AGENTS.md) and a store that outlives the run.

Two different things both get called "memory":

  a) memory=["/memory/AGENTS.md"]: files whose contents are pasted into the
     system prompt at startup, plus instructions telling the model to update
     them with edit_file when it learns something durable. This is the
     CLAUDE.md / AGENTS.md pattern. The file is the memory.

  b) StoreBackend: a LangGraph BaseStore behind a path prefix, so files
     written under that prefix survive across threads and processes (with a
     persistent store). CompositeBackend routes prefixes to backends.

This script wires both: /memory/ is on disk (a), /vault/ is a StoreBackend
(b), everything else is per-run state. Run it twice. The second run starts
with what the first one learned.

Think about who else can write those files. Exercise 8 does.
"""

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

from common import final_answer, get_model, print_stream, require_key

require_key()
HERE = Path(__file__).parent

# One process-wide store. Swap for a Postgres/Redis store in production and
# the /vault/ files survive restarts.
store = InMemoryStore()

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memory/": FilesystemBackend(root_dir=HERE / "memory", virtual_mode=True),
        "/vault/": StoreBackend(namespace=lambda rt: ("lab066", "vault")),
    },
)

agent = create_deep_agent(
    model=get_model(),
    backend=backend,
    memory=["/memory/AGENTS.md"],
    store=store,
    system_prompt="You are a personal security assistant.",
)

print("== Turn 1: teach it something durable ==")
print_stream(
    agent.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Two things to remember: my home lab subnet is 10.0.20.0/24 and I "
                        "always want scan results written under /vault/scans/. Also save a "
                        "note /vault/scans/README.md describing that convention."
                    ),
                }
            ]
        },
        stream_mode="updates",
    )
)

print("\n== Turn 2: brand-new thread, same process ==")
r = agent.invoke({"messages": [{"role": "user", "content": "What is my lab subnet, and where do scan results go? List /vault/scans/."}]})
print(final_answer(r))

print("\n== memory/AGENTS.md now on disk ==")
print((HERE / "memory" / "AGENTS.md").read_text())
print("Run the script again: the subnet is known from the first model call, before any tool runs.")
print("Reset with ./reset_workspace.sh")
