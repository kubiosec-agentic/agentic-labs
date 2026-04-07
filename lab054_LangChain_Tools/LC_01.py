"""
Basic LangChain LLM query without tools.

Sends a single user message to gpt-4o via LangChain's ChatOpenAI wrapper.
No tools, no chains, just a bare invoke to show the simplest possible call.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o")

messages = [
    HumanMessage(content="What is the weather in SF?"),
]

response = llm.invoke(messages)
print(f"\nResponse: {response}")
