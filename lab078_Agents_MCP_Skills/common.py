"""
Shared bits for lab078: model selection and tracing.

The Agents SDK sends traces to OpenAI by default. In a training lab that is
surprising network traffic, so we disable it centrally here. Import this
module (or call disable_tracing()) before running any agent.
"""

import os

from agents import set_tracing_disabled

# Any model string the Agents SDK understands. Override with DA_MODEL to reuse
# the same knob as the other labs.
MODEL = os.environ.get("DA_MODEL", "gpt-4o-mini")


def disable_tracing() -> None:
    # Equivalent to env OPENAI_AGENTS_DISABLE_TRACING=1. Without this the SDK's
    # trace exporter tries to reach OpenAI even for a local-only run.
    set_tracing_disabled(True)


def require_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("export OPENAI_API_KEY=... first (the agent run needs it; MCP wiring does not)")
