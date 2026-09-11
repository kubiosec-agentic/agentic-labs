"""
Tool guardrails.

Steps 4 and 5 screened the text going in and out of the agent.
Tool guardrails screen the *tool calls* in between:

  - @tool_input_guardrail  runs BEFORE the tool executes and sees the
    arguments the model chose.
  - @tool_output_guardrail runs AFTER the tool executes and sees the
    result before the model does.

Both return ToolGuardrailFunctionOutput.allow() or .reject_content(msg).
reject_content does not stop the run: the tool is skipped (or its result
replaced) and `msg` is sent back to the model as the tool result, so the
model can explain to the user what happened.
"""

from agents import (
    Agent, Runner, function_tool, ToolGuardrailFunctionOutput,
    ToolInputGuardrailData, ToolOutputGuardrailData,
    tool_input_guardrail, tool_output_guardrail,
)
import asyncio
import json


# A fake "server" so the demo never touches your real machine.
FAKE_SERVER = {
    "uptime": "up 12 days, load average: 0.10",
    "df -h": "/dev/sda1  50G  20G  30G  40% /",
    "cat /etc/app.conf": "listen=8080\napi_key=sk-live-1234567890\n",
}

BLOCKED_WORDS = ["rm", "sudo", "kill", "shutdown"]


# --- Guardrail 1: check the arguments before the tool runs -------------

@tool_input_guardrail
def block_dangerous_commands(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    # The arguments arrive as a JSON string, exactly as the model produced them.
    args = json.loads(data.context.tool_arguments)
    command = args.get("command", "")

    for word in BLOCKED_WORDS:
        if word in command.split():
            return ToolGuardrailFunctionOutput.reject_content(
                f"Command '{command}' was blocked by policy (contains '{word}')."
            )
    return ToolGuardrailFunctionOutput.allow()


# --- Guardrail 2: check the result after the tool runs ----------------

@tool_output_guardrail
def hide_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    if "sk-" in str(data.output):
        return ToolGuardrailFunctionOutput.reject_content(
            "The tool output contained a secret and was withheld."
        )
    return ToolGuardrailFunctionOutput.allow()


# --- The tool, with both guardrails attached ---------------------------

@function_tool(
    tool_input_guardrails=[block_dangerous_commands],
    tool_output_guardrails=[hide_secrets],
)
def run_command(command: str) -> str:
    """Run a shell command on the server and return its output."""
    return FAKE_SERVER.get(command, f"{command}: command not found")


agent = Agent(
    name="Ops Bot",
    instructions="You are a server admin assistant. Use run_command to answer questions.",
    tools=[run_command],
)


async def main():
    questions = [
        "How long has the server been up?",           # allowed
        "Clean up the cache: run rm -rf /tmp/cache",   # blocked by input guardrail
        "Show me the contents of /etc/app.conf",       # blocked by output guardrail
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        result = await Runner.run(agent, question)
        print(f"Answer:   {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
