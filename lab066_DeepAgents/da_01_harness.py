"""
Exercise 1: the harness out of the box.

create_deep_agent() gives you, with almost no configuration, the tool set a
coding-agent CLI ships with: a filesystem (ls / read_file / write_file /
edit_file / delete / glob / grep), an `execute` tool, and a `task` tool that
spawns a general-purpose sub-agent. Add TodoListMiddleware and you also get
`write_todos`. The model is a parameter, not a hard-wired vendor.

By default the filesystem is a StateBackend: files live inside the LangGraph
state of this one run and nothing touches your disk. That is the safest place
to start looking at what the agent actually does.
"""

from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

from common import final_answer, get_model, print_stream, require_key

require_key()

agent = create_deep_agent(
    model=get_model(),
    system_prompt=(
        "You are a careful security engineer. Work step by step and use files "
        "to keep notes when a task has more than one part."
    ),
    # Planning is opt-in in deepagents 0.7: this middleware adds `write_todos`.
    middleware=[TodoListMiddleware()],
)

# 1. What did the harness bolt on? The tool node knows every tool the model
#    can call. Compare this list with what you wrote by hand in lab064.
print("== Tools the model is offered ==")
print("  " + ", ".join(agent.nodes["tools"].bound.tools_by_name.keys()))

# 2. Give it a multi-step job and watch the loop.
task = (
    "Create /notes/plan.md with a 3-step plan for hardening an SSH server, "
    "then create /notes/sshd_config.snippet with the matching sshd_config "
    "lines, then read both files back and give me a two-sentence summary. "
    "Track the steps with write_todos."
)

print("\n== Run ==")
print_stream(agent.stream({"messages": [{"role": "user", "content": task}]}, stream_mode="updates"))

# 3. A second, independent invoke. StateBackend files belong to one run.
print("\n== Second invoke, fresh state ==")
again = agent.invoke({"messages": [{"role": "user", "content": "List the files under /notes."}]})
print(final_answer(again))
print(
    "\nThe second call cannot see /notes: StateBackend files live in the state "
    "of a single run. Persistence is Exercise 2 (disk) and Exercise 6 (memory)."
)
