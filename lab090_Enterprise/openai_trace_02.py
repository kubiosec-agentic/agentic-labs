"""
Exercise: OpenAI Agents SDK built-in tracing.

The Agents SDK traces every agent run automatically: LLM generations,
tool calls, handoffs, guardrails.  This example shows how to:

1. Use the default tracing (just run the agent, traces appear in the
   OpenAI dashboard automatically).
2. Create custom traces that group multiple agent runs into one
   workflow.
3. Add custom spans to track your own application logic.
4. Control sensitive data inclusion.

After running this script, go to:
    https://platform.openai.com/traces
to see the full trace with every step visualized.

Run:
    python3 openai_trace_02.py
"""

import asyncio

from agents import (
    Agent,
    Runner,
    RunConfig,
    function_tool,
    trace,
    custom_span,
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@function_tool
def lookup_order(order_id: str) -> str:
    """Look up an order by ID and return its status."""
    # Stub: in production this hits a database
    orders = {
        "ORD-001": "shipped, arriving tomorrow",
        "ORD-002": "processing, estimated 3 days",
        "ORD-003": "delivered on April 8",
    }
    return orders.get(order_id, f"Order {order_id} not found.")


@function_tool
def cancel_order(order_id: str) -> str:
    """Cancel an order by ID."""
    return f"Order {order_id} has been cancelled."


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------
support_agent = Agent(
    name="Support Agent",
    instructions=(
        "You are a customer support agent. Use the lookup_order tool "
        "to check order status when asked. Use cancel_order if the "
        "customer wants to cancel. Be concise and helpful."
    ),
    tools=[lookup_order, cancel_order],
)


async def main():
    # -----------------------------------------------------------------
    # Example 1: Default tracing (automatic, no extra code needed)
    # -----------------------------------------------------------------
    print("=== Example 1: Default tracing ===")
    result = await Runner.run(
        support_agent,
        "What is the status of order ORD-001?",
    )
    print(f"Response: {result.final_output}\n")

    # -----------------------------------------------------------------
    # Example 2: Custom trace grouping multiple runs
    #
    # The trace() context manager groups everything inside it into
    # a single workflow trace. Useful when one user interaction
    # triggers multiple agent runs.
    # -----------------------------------------------------------------
    print("=== Example 2: Custom trace (grouped workflow) ===")
    with trace("Order Support Workflow"):
        # First run: check status
        r1 = await Runner.run(
            support_agent,
            "Check the status of ORD-002 please.",
        )
        print(f"Step 1: {r1.final_output}")

        # Second run: follow-up based on first result
        r2 = await Runner.run(
            support_agent,
            f"The status was: {r1.final_output}. "
            "The customer wants to cancel it.",
        )
        print(f"Step 2: {r2.final_output}\n")

    # -----------------------------------------------------------------
    # Example 3: Custom spans for application logic
    #
    # custom_span() lets you add your own spans alongside the
    # automatic agent spans. Good for tracking business logic,
    # database calls, or external API calls.
    # -----------------------------------------------------------------
    print("=== Example 3: Custom spans ===")
    with trace("Order Lookup with Validation"):
        # Custom span for input validation
        with custom_span("validate_input"):
            order_id = "ORD-003"
            assert order_id.startswith("ORD-"), "Invalid order ID format"
            print(f"Validated order ID: {order_id}")

        # Agent run (automatically traced)
        result = await Runner.run(
            support_agent,
            f"Look up order {order_id}.",
        )
        print(f"Response: {result.final_output}\n")

    # -----------------------------------------------------------------
    # Example 4: Controlling sensitive data
    #
    # By default, LLM inputs/outputs and tool call arguments are
    # included in traces. You can disable this for compliance.
    # -----------------------------------------------------------------
    print("=== Example 4: Trace without sensitive data ===")
    config = RunConfig(
        trace_include_sensitive_data=False,
        workflow_name="Redacted Support Flow",
    )
    result = await Runner.run(
        support_agent,
        "What happened with ORD-001?",
        run_config=config,
    )
    print(f"Response: {result.final_output}")
    print("(LLM inputs/outputs are NOT included in this trace)\n")

    print("Done. View traces at: https://platform.openai.com/traces")


if __name__ == "__main__":
    asyncio.run(main())
