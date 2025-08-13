from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

# Initialize the LLM with a specific model
llm = ChatOpenAI(model="gpt-4o")

# Pass the result back to the model
messages = [
    HumanMessage(content="What is the weather in SF?"),
]

final_response = llm.invoke(messages)
print(f"\nFinal response: {final_response}")


