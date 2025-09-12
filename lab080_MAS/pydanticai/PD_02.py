from pydantic_ai import Agent, CodeExecutionTool

agent = Agent('anthropic:claude-sonnet-4-0', builtin_tools=[CodeExecutionTool()])

result = agent.run_sync('Calculate the factorial of 15 and show your work')

print(result.output)
