from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

# Initialize the LLM with a specific model
llm = ChatOpenAI(model="gpt-4.1")

# Print the tool call response
print(tool_call_response)

# Execute the tool call
tool_call = tool_call_response.tool_calls[0]
tool_result = get_weather(tool_call["args"]["location"])
print(f"\nTool executed: {tool_result}")

# Pass the result back to the model
messages = [
    HumanMessage(content="What is the weather in SF?"),
]

final_response = structured_llm.invoke(messages)
print(f"\nFinal response: {final_response}")


