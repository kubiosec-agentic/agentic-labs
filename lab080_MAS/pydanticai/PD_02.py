from pydantic_ai import Agent, CodeExecutionTool
from pydantic_ai.capabilities import NativeTool

# pydantic-ai 2.x: native (provider-side) tools are passed via
# capabilities=[NativeTool(...)]. The old builtin_tools= kwarg was removed.
agent = Agent('anthropic:claude-sonnet-4-0', capabilities=[NativeTool(CodeExecutionTool())])

result = agent.run_sync('Calculate the factorial of 15 and show your work')

print(result.output)
