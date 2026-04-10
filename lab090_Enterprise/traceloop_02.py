"""
Exercise: Traceloop with OpenAI Agents SDK.

Traceloop auto-instruments OpenAI calls, but you can add structure
with decorators: @workflow groups multiple steps into one trace,
@agent marks an autonomous unit, and @tool marks functions the
agent calls. This gives you a hierarchical trace in the Traceloop
dashboard (or any OpenTelemetry backend).

This example builds a simple research workflow:
  1. A research agent searches for information (stubbed tool)
  2. A writer agent summarizes the findings
  3. The whole thing is wrapped in a @workflow

Prerequisites:
    export TRACELOOP_API_KEY="tl_..."
    export OPENAI_API_KEY="sk-..."
    pip install traceloop-sdk openai-agents

Run:
    python3 traceloop_02.py

Then check https://app.traceloop.com to see the trace with:
  - workflow: "research_and_summarize"
    - agent: "researcher"
      - tool: "web_search"
    - agent: "writer"
"""

import asyncio
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, agent as trace_agent, tool as trace_tool

from agents import Agent, Runner, function_tool

# Initialize Traceloop (sends traces to Traceloop dashboard)
# For self-hosted OpenTelemetry, set api_endpoint to your collector URL
Traceloop.init(
    app_name="research_service",
    disable_batch=True,
)


# ---------------------------------------------------------------------------
# Tools (with Traceloop @tool decorator for visibility)
# ---------------------------------------------------------------------------
@function_tool
def web_search(query: str) -> str:
    """Search the web for information (stubbed)."""
    # In production, this calls a real search API
    return _web_search_impl(query)


@trace_tool(name="web_search")
def _web_search_impl(query: str) -> str:
    """Inner function decorated with Traceloop @tool for tracing."""
    results = {
        "kubernetes security": (
            "Key practices: use RBAC, network policies, pod security standards, "
            "image scanning, and secrets encryption at rest."
        ),
        "default": "No results found.",
    }
    for key, value in results.items():
        if key in query.lower():
            return value
    return results["default"]


@function_tool
def fact_check(claim: str) -> str:
    """Verify a claim (stubbed)."""
    return _fact_check_impl(claim)


@trace_tool(name="fact_check")
def _fact_check_impl(claim: str) -> str:
    """Inner function decorated with Traceloop @tool."""
    return f"Claim appears accurate: '{claim}'"


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------
researcher = Agent(
    name="Researcher",
    instructions=(
        "You are a security researcher. Use the web_search tool to find "
        "information about the topic. Return a concise summary of findings."
    ),
    tools=[web_search],
)

writer = Agent(
    name="Writer",
    instructions=(
        "You are a technical writer. Take the research findings and write "
        "a clear, concise paragraph suitable for a blog post. Use the "
        "fact_check tool to verify any specific claims before including them."
    ),
    tools=[fact_check],
)


# ---------------------------------------------------------------------------
# Workflow (decorated with Traceloop @workflow)
# ---------------------------------------------------------------------------
@workflow(name="research_and_summarize")
async def research_and_summarize(topic: str) -> str:
    """
    Full workflow: research a topic, then summarize the findings.
    Traceloop groups both agent runs under one workflow trace.
    """
    # Step 1: Research
    research_result = await _run_researcher(topic)
    print(f"Research findings:\n  {research_result}\n")

    # Step 2: Write summary based on research
    summary_result = await _run_writer(research_result)
    return summary_result


@trace_agent(name="researcher")
async def _run_researcher(topic: str) -> str:
    result = await Runner.run(researcher, f"Research: {topic}")
    return result.final_output


@trace_agent(name="writer")
async def _run_writer(findings: str) -> str:
    result = await Runner.run(
        writer,
        f"Write a blog paragraph based on these findings:\n{findings}",
    )
    return result.final_output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main():
    print("=== Research & Summarize Workflow ===\n")

    summary = await research_and_summarize("kubernetes security best practices")

    print(f"Final summary:\n  {summary}\n")
    print("View trace at: https://app.traceloop.com")
    print("(or your OpenTelemetry backend if self-hosted)")


if __name__ == "__main__":
    asyncio.run(main())
