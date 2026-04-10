"""
Exercise 6: Agent with a hosted code interpreter (OpenAI Responses API).

This exercise gives the agent access to OpenAI's hosted code
interpreter. The agent can write and execute Python code server-side
to solve problems, generate charts, and process data.

The code interpreter runs in a sandboxed environment managed by
OpenAI. It supports Python with common libraries (numpy, pandas,
matplotlib, etc.).

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"

Run:
    python3 MAF_06_code_interpreter.py
"""

import asyncio
import os
import sys

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")
if not os.environ.get("OPENAI_CHAT_MODEL"):
    sys.exit("Error: OPENAI_CHAT_MODEL is not set. Run: export OPENAI_CHAT_MODEL=\"gpt-4o-mini\"")

from agent_framework.openai import OpenAIChatClient


async def main() -> None:
    print("=== Code Interpreter Agent Example ===\n")

    # OpenAIChatClient uses the Responses API which supports hosted
    # tools. get_code_interpreter_tool() enables server-side Python
    # execution inside a sandboxed environment managed by OpenAI.
    client = OpenAIChatClient()

    code_interpreter = client.get_code_interpreter_tool()

    agent = client.as_agent(
        name="CodingAgent",
        instructions=(
            "You are a helpful assistant that can write and execute "
            "Python code to solve problems. Always show the code you "
            "write and explain the output."
        ),
        tools=[code_interpreter],
    )

    # --- Example 1: computation ---
    query1 = "Calculate the first 20 Fibonacci numbers and show them as a formatted table."
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1}\n")

    # --- Example 2: data analysis ---
    query2 = (
        "Generate a dataset of 100 random exam scores (0-100), "
        "compute the mean, median, and standard deviation, "
        "and describe the distribution."
    )
    print(f"User: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2}\n")


if __name__ == "__main__":
    asyncio.run(main())
