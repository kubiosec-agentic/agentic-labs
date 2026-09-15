"""
Exercise 7: context engineering. Offloading and summarisation.

A harness earns its keep by NOT sending everything to the model. Two
mechanisms are built in:

  1. Tool-result eviction (FilesystemMiddleware). A tool result bigger than
     tool_token_limit_before_evict (default 20k tokens) is written to
     /large_tool_results/<call_id> on the backend and the model only gets a
     pointer. It then uses grep/read_file with offsets to look at the part
     it needs. Same idea as `command | head` instead of `command`.

  2. Conversation summarisation (SummarizationMiddleware). When the history
     crosses a trigger, older messages are replaced by a model-written
     summary. The deepagents flavour first dumps the evicted messages to
     /conversation_history/<session>.md so the agent can read them back.

The defaults trigger at 85% of the model's context window. To see it happen
in a lab run we add a second summariser with a tiny trigger. The tool below
returns ~30k tokens of fake syslog, enough to trip mechanism 1 as well.
"""

import random

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware import SummarizationMiddleware
from langchain_core.tools import tool

from common import get_model, print_stream, require_key

require_key()

random.seed(7)
HOSTS = ["web01", "web02", "db01", "bastion"]
MSGS = [
    "sshd[{pid}]: Accepted publickey for deploy from 10.0.20.{ip} port {port} ssh2",
    "sshd[{pid}]: Failed password for invalid user admin from 45.83.{a}.{b} port {port} ssh2",
    "kernel: [UFW BLOCK] IN=eth0 SRC=45.83.{a}.{b} DST=10.0.20.{ip} PROTO=TCP DPT={port}",
    "cron[{pid}]: (root) CMD (run-parts /etc/cron.hourly)",
    "systemd[1]: Started Session {pid} of user deploy.",
]


@tool
def fetch_syslog(host: str) -> str:
    """Return the last 24h of syslog for a host (large!)."""
    lines = []
    for i in range(4000):
        tpl = random.choice(MSGS)
        lines.append(
            f"Sep 14 {i // 170:02d}:{i % 60:02d}:{random.randint(0, 59):02d} {host} "
            + tpl.format(pid=random.randint(1000, 65000), ip=random.randint(2, 250), port=random.randint(1024, 65000), a=random.randint(1, 254), b=random.randint(1, 254))
        )
    # One needle. A real attacker's line is buried in the middle.
    lines[2617] = f"Sep 14 15:23:41 {host} sshd[31337]: Accepted password for root from 185.220.101.4 port 51022 ssh2"
    return "\n".join(lines)


backend = StateBackend()
model = get_model()

agent = create_deep_agent(
    model=model,
    backend=backend,
    tools=[fetch_syslog],
    system_prompt="You are a SOC analyst. Be economical with context: never read a large file in full.",
    middleware=[
        # Demo-sized trigger: summarise once the history holds 12 messages, keep the last 4.
        SummarizationMiddleware(model, backend=backend, trigger=("messages", 12), keep=("messages", 4)),
    ],
)

task = (
    "Fetch the syslog for web01, web02 and db01 one host at a time. For each, find any "
    "'Accepted password for root' event and note the source IP. Then write /findings.md "
    "with one line per host and answer with the same three lines."
)

print("== Run ==")
print_stream(agent.stream({"messages": [{"role": "user", "content": task}]}, stream_mode="updates"))

print(
    "\nWhat to notice:\n"
    "  * every fetch_syslog result came back as 'Tool result too large ... saved at /large_tool_results/<id>'\n"
    "  * the model then grep'ed the offloaded file instead of reading it; the needle is one line of 4000\n"
    "  * after the history passed 12 messages a summarisation call replaced the old turns; the evicted\n"
    "    messages were written to /conversation_history/<id>.md on the backend\n"
    "Run with mitmproxy (lab050) to count how many tokens actually went to the API per turn."
)
