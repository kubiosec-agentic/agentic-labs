from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel

# Define a tool with structured input
class WeatherInput(BaseModel):
    location: str

@tool("get_weather", args_schema=WeatherInput)
def get_weather(location: str) -> str:
    """Get weather at a location."""
    return f"It's sunny in {location}."

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o")

# Bind tools
llm_with_tools = llm.bind_tools([get_weather])

# User query
query = "What is the weather in San Francisco?"

# Step 1: Let the LLM decide whether to call a tool
tool_call_response = llm_with_tools.invoke(query)
print("\nTool call response:")
print(tool_call_response)

# Step 2: Simulate tool execution
tool_call = tool_call_response.tool_calls[0]
tool_args = tool_call["args"]
tool_result = get_weather.invoke(tool_args)

print(f"\nTool executed: {tool_result}")

# Step 3: Feed back tool result
messages = [
    HumanMessage(content=query),
    tool_call_response,
    ToolMessage(content=tool_result, tool_call_id=tool_call["id"])
]

# Step 4: Final answer from model
final_response = llm_with_tools.invoke(messages)
print(f"\nFinal response: {final_response.content}")
