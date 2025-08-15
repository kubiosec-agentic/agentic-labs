from pydantic_ai import Agent, WebSearchTool

agent = Agent('anthropic:claude-sonnet-4-0', builtin_tools=[WebSearchTool()])

result = agent.run_sync('Give me a sentence with the biggest news in AI this week.')
# > Scientists have developed a universal AI detector that can identify deepfake videos.
print(result.output)