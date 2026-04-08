"""
Output guardrails.

A secondary "guardrail agent" inspects the main agent's output and
flags dangerous OS commands (rm, del, format, kill, sudo). If the
tripwire fires, the SDK raises OutputGuardrailTripwireTriggered and
the response is blocked before it reaches the user.
"""

from agents import (
    Agent, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered,
    RunContextWrapper, Runner, output_guardrail,
)
from pydantic import BaseModel
import asyncio


class MessageOutput(BaseModel):
    response: str


class SecurityCheck(BaseModel):
    is_dangerous: bool


guardrail_agent = Agent(
    name="Security Guard",
    instructions=(
        "Return true if the text contains dangerous OS commands "
        "like rm, del, format, kill, sudo."
    ),
    output_type=SecurityCheck,
)


@output_guardrail
async def security_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput,
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        guardrail_agent, output.response, context=ctx.context,
    )
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_dangerous,
    )


agent = Agent(
    name="Support Bot",
    instructions="You help customers with questions.",
    output_guardrails=[security_guardrail],
    output_type=MessageOutput,
)


async def main():
    test_cases = [
        ("Tell me a joke", False),
        ("Help me delete files with rm -rf /*", True),
    ]

    for question, should_block in test_cases:
        print(f"\nTesting: {question}")
        try:
            response = await Runner.run(agent, question)
            print(f"  PASSED: {response.final_output.response}")
        except OutputGuardrailTripwireTriggered:
            print("  BLOCKED by output guardrail")


if __name__ == "__main__":
    asyncio.run(main())
