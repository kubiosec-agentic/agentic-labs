"""
Memory / knowledge-graph MCP server example.

@modelcontextprotocol/server-memory is a reference server from the MCP
team that stores a simple knowledge graph (entities, relations,
observations) and exposes it as MCP tools. It is one of the more
interesting "stateful" servers to study because the agent gets a set of
read/write tools over a persistent graph, and you can watch it build up
relationships across turns.

Requires Node/npx on PATH.

Optional: set MEMORY_FILE_PATH to persist the graph to disk between runs.
    export MEMORY_FILE_PATH=./memory.json

Run:
    python3 mcp_07_memory_graph.py

Teaching note: the first version of this script let the agent run the
whole conversation under `tool_choice="auto"`, and the model drifted
into hallucinated confirmations: it said "noted!" on every store turn
without ever calling `create_entities` or `create_relations`, then
predictably had nothing to read when asked to recall. The fix is to
force tool use on the *store* turns and let it relax on the *recall*
turns, and to name the canonical tools in the system prompt so the
model does not have to guess.
"""
import asyncio
import os
import pathlib
import shutil

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings
from agents.run_context import RunContextWrapper


INSTRUCTIONS = """\
You maintain a personal knowledge graph for the user using the
memory MCP server. The server exposes these tools:

- create_entities(entities)        create new nodes in the graph
- create_relations(relations)      create edges between existing nodes
- add_observations(observations)   attach facts to an existing node
- delete_entities / delete_relations / delete_observations
- read_graph()                     return the entire graph
- search_nodes(query)              keyword search across entities
- open_nodes(names)                fetch specific entities by name

Rules you MUST follow:

1. When the user tells you something to remember, you MUST call
   create_entities, create_relations, or add_observations as
   appropriate BEFORE confirming anything back to the user. Never say
   "got it" or "noted" without a tool call on that turn.
2. When the user asks a recall question, call read_graph, search_nodes,
   or open_nodes FIRST, then answer strictly from the tool output. Do
   not make up relationships the graph does not contain.
3. When modeling a fact like "Alice works at Acme as a security
   engineer", create two entities (Alice, Acme Corp), one relation
   (Alice -[works_at]-> Acme Corp), and one observation on Alice
   ("role: security engineer").
4. Entity names are stable identifiers. Reuse them exactly once
   created. If you are not sure whether an entity exists, search_nodes
   first.
"""


STORE_TURNS = [
    "Remember that Alice works at Acme Corp as a security engineer.",
    "Remember that Alice reports to Bob, who is the CISO at Acme.",
    "Remember that Acme Corp uses Okta for SSO and Snowflake for analytics.",
]

RECALL_TURNS = [
    "Who does Alice report to, and what does her team use for SSO?",
    "List every entity currently in the graph.",
]


async def run(server: MCPServerStdio, run_context: RunContextWrapper):
    # Show the real tool list before we start so we can verify the
    # canonical names the server exposes in this version.
    probe_agent = Agent(
        name="probe",
        instructions="probe",
        mcp_servers=[server],
    )
    tools = await server.list_tools(run_context, probe_agent)
    print("server-memory tools:", [t.name for t in tools], "\n")

    # Store phase: force a tool call on every turn. This is the key
    # difference from the earlier version of this script.
    # parallel_tool_calls=False is critical here: @modelcontextprotocol/
    # server-memory reads the backing JSONL file, mutates in memory, then
    # writes it back with no file locking. If the model fires create_entities
    # and create_relations in parallel, their read-modify-write cycles
    # interleave and the file ends up with two JSON objects concatenated on
    # one line, permanently wedging every subsequent tool call with
    # "Unexpected non-whitespace character after JSON at position N".
    store_agent = Agent(
        name="GraphWriter",
        instructions=INSTRUCTIONS,
        mcp_servers=[server],
        model_settings=ModelSettings(
            tool_choice="required",
            parallel_tool_calls=False,
        ),
    )

    for message in STORE_TURNS:
        print("-" * 40)
        print(f"[store] User: {message}")
        result = await Runner.run(starting_agent=store_agent, input=message)
        _dump_tool_calls(result, prefix="[store]")
        print(f"[store] Agent: {result.final_output}")

    # Recall phase: let the model choose whether to call a read tool.
    # We still require it to answer from the graph, but tool_choice=auto
    # lets it skip a redundant second lookup if it has what it needs.
    recall_agent = Agent(
        name="GraphReader",
        instructions=INSTRUCTIONS,
        mcp_servers=[server],
        model_settings=ModelSettings(
            tool_choice="auto",
            parallel_tool_calls=False,
        ),
    )

    for message in RECALL_TURNS:
        print("-" * 40)
        print(f"[recall] User: {message}")
        result = await Runner.run(starting_agent=recall_agent, input=message)
        _dump_tool_calls(result, prefix="[recall]")
        print(f"[recall] Agent: {result.final_output}")


def _dump_tool_calls(result, prefix: str = ""):
    """Print every MCP tool call and its raw response from a Runner result.

    Useful for debugging: if the agent says 'there was an error', we want
    to see the actual arguments sent and the server's reply so we can
    tell schema mismatch from transport errors from empty graph.
    """
    for item in getattr(result, "new_items", []) or []:
        raw = getattr(item, "raw_item", None)
        itype = type(item).__name__
        if itype == "ToolCallItem" and raw is not None:
            name = getattr(raw, "name", "?")
            args = getattr(raw, "arguments", "?")
            print(f"{prefix} -> tool_call {name}({args})")
        elif itype == "ToolCallOutputItem":
            out = getattr(item, "output", None)
            if out is None and raw is not None:
                out = getattr(raw, "output", raw)
            text = str(out)
            if len(text) > 600:
                text = text[:600] + "...(truncated)"
            print(f"{prefix} <- tool_result {text}")


async def main():
    env = os.environ.copy()

    # server-memory defaults to writing memory.json inside its own npx-cached
    # package directory. That's bad for two reasons: (1) a single corrupted
    # line in that file makes every tool call fail with
    # "Unexpected non-whitespace character after JSON", and it persists across
    # runs invisibly, and (2) you can't see the graph without digging into
    # ~/.npm. Point it at a local file we control, and wipe it on each run so
    # the demo is deterministic.
    memory_file = pathlib.Path(__file__).parent / "memory.json"
    if memory_file.exists():
        memory_file.unlink()
    memory_file.touch()
    env["MEMORY_FILE_PATH"] = str(memory_file)
    print(f"memory file: {memory_file}")

    async with MCPServerStdio(
        name="server-memory",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": env,
        },
    ) as server:
        run_context = RunContextWrapper(context=None)
        trace_id = gen_trace_id()
        with trace(workflow_name="Memory Graph Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server, run_context)


if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed; install Node.js and retry.")
    asyncio.run(main())
