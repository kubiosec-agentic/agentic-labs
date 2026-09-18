"""
LangChain tool binding with structured input.

Defines a weather tool using the @tool decorator, binds it to gpt-4o,
and walks through the four-phase tool-call cycle:

  1. Model emits a tool_calls response
  2. Code executes the tool locally
  3. Tool result is fed back as a ToolMessage
  4. Model produces a final natural-language answer
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel


# ---- Tool definition with Pydantic schema ----

class WeatherInput(BaseModel):
    location: str

@tool("get_weather", args_schema=WeatherInput)
def get_weather(location: str) -> str:
    """Get weather at a location."""
    return f"It's sunny in {location}."


# ---- LLM with tool binding ----

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([get_weather])

query = "What is the weather in San Francisco?"

# Step 1: model decides to call the tool
tool_call_response = llm_with_tools.invoke(query)
print("\nTool call response:")
print(tool_call_response)

# Step 2: execute the tool locally
tool_call = tool_call_response.tool_calls[0]
tool_args = tool_call["args"]
tool_result = get_weather.invoke(tool_args)
print(f"\nTool executed: {tool_result}")

# Step 3: feed tool result back
messages = [
    HumanMessage(content=query),
    tool_call_response,
    ToolMessage(content=tool_result, tool_call_id=tool_call["id"]),
]

# Step 4: model produces final answer
final_response = llm_with_tools.invoke(messages)
print(f"\nFinal response: {final_response.content}")
