from langchain_openai import ChatOpenAI, OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

# This script demonstrates how to use different LLMs with LangChain.
# initialize a completion or chat model
# Uncomment the one you want to use

# chat = ChatGoogleGenerativeAIGoogleGenerativeAI(model="gemini-2.0-flash")
chat = ChatOpenAI(model="gpt-3.5-turbo")
# chat = ChatAnthropic(model="claude-3-opus-20240229")
# chat = ChatOllama(model="deepseek-r1:1.5b")
# chat = ChatOllama(model="phi3:3.8b", temperature=0)


response = chat.invoke("Tell me a joke about light bulbs!")
print(response)
# print(response.content)
# print(response.response_metadata)
