import asyncio
from agents import Agent, GuardrailFunctionOutput, InputGuardrail, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from pydantic import BaseModel

# Initialize Langtrace SDK
langtrace.init()

# Define the expected output format from the guardrail agent
class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

# Guardrail agent that detects if the question is about homework
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

# Specialized agents
math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

# Guardrail function to determine if the input is a homework question
async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

# Main triage agent that applies the guardrail and routes to tutors
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

# Entry point with Langtrace tracing and guardrail exception handling
@with_langtrace_root_span()
async def main():
    queries = [
        "who was the first president of the united states?",
        "what is life",
        "what is the derivative of x squared?",
    ]

    for query in queries:
        try:
            result = await Runner.run(triage_agent, query)
            print(f"\n✅ Accepted input: {query}")
            print("Output:", result.final_output)
        except InputGuardrailTripwireTriggered as e:
            print(f"\n❌ Blocked input by guardrail: {query}")
            print("Reason:", e)

if __name__ == "__main__":
    asyncio.run(main())
