from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from pydantic import BaseModel
from langchain.tools import tool

@tool
# Define a simple weather tool
def get_weather(location: str) -> None:
    """Get weather at a location."""
    return "It's sunny."

# Define the output schema for the tool using pydantic
class OutputSchema(BaseModel):
    """Schema for response."""
    answer: str
    justification: str

# Initialize the LLM with a specific model
llm = ChatOpenAI(model="gpt-4.1")

# Bind the tool to the LLM with a structured response format
structured_llm = llm.bind_tools(
    [get_weather],
    response_format=OutputSchema,
    strict=True,
)

# Response contains tool calls 
tool_call_response = structured_llm.invoke("What is the weather in SF?")

# Print the tool call response
print(tool_call_response)

# Execute the tool call
tool_call = tool_call_response.tool_calls[0]
tool_result = get_weather(tool_call["args"]["location"])
print(f"\nTool executed: {tool_result}")

# Pass the result back to the model
messages = [
    HumanMessage(content="What is the weather in SF?"),
    tool_call_response,
    ToolMessage(content=tool_result, tool_call_id=tool_call["id"])
]

final_response = structured_llm.invoke(messages)
print(f"\nFinal response: {final_response}")


