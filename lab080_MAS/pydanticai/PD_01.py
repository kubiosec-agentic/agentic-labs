from pydantic_ai import Agent, WebSearchTool
from pydantic_ai.capabilities import NativeTool

# pydantic-ai 2.x: native (provider-side) tools are passed via
# capabilities=[NativeTool(...)]. The old builtin_tools= kwarg was removed.
agent = Agent('anthropic:claude-sonnet-5', capabilities=[NativeTool(WebSearchTool())])

result = agent.run_sync('Give me a sentence with the biggest news in AI this week.')
# > Scientists have developed a universal AI detector that can identify deepfake videos.
print(result.output)
