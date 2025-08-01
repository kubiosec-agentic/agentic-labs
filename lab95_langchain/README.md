# LangChain Quickstart
## Introduction
Let's analyse the following code
```
from langchain_openai import ChatOpenAI, OpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
# from langchain_anthropic import ChatAnthropic
# from langchain_ollama import ChatOllama


# This script demonstrates how to use different LLMs with LangChain.
# initialize a completion or chat model
# Uncomment the one you want to use

# chat = ChatGoogleGenerativeAIGoogleGenerativeAI(model="gemini-2.0-flash")
# chat = ChatOpenAI(model="gpt-3.5-turbo")
# chat = ChatAnthropic(model="claude-3-opus-20240229")
# chat = ChatOllama(model="deepseek-r1:1.5b")
chat = ChatOllama(model="phi3:3.8b", temperature=0)


response = chat.invoke("Tell me a joke about light bulbs!")
print(response)
```

### Step 1:
Read this as follows: <br>
"From the langchain_openai package, import the classes ChatOpenAI and OpenAI." <br>
You only need to import what you actually need.
```
from langchain_openai import ChatOpenAI, OpenAI
```
A subtle difference here to note is `ChatOpenAI` is interacting `ith `/chat/completions` API endpoint, while `OpenAI` interacts with the older `/completions` endpoint.<br>
(_Note: We can actually omit OpenAI in this example_)

#### What is a Package
It’s a collection of code (tools) that someone else wrote to help you do specific things, like talk to an AI model, work with images, or build a website—without writing everything from scratch.

#### What is a Class
A class is like a blueprint in Python. It describes how to build something with specific features and actions.

### Step 2:
You need to instantiate a class to use it.
```
# chat = ChatGoogleGenerativeAIGoogleGenerativeAI(model="gemini-2.0-flash")
chat = ChatOpenAI(model="gpt-3.5-turbo")
# chat = ChatAnthropic(model="claude-3-opus-20240229")
# chat = ChatOllama(model="deepseek-r1:1.5b")
# chat = ChatOllama(model="phi3:3.8b", temperature=0)
```
`chat` is an object that represents an OpenAI chat client.
It was created (instantiated) from the ChatOpenAI class, and it knows how to send messages to an OpenAI chat model (like GPT-4) and return the responses.

### Step 3:
`invoke(...)` is a method call. You're calling the invoke method on the chat object.
```
response = chat.invoke("Tell me a joke about light bulbs!")
```
response contains is the result of the `invoke()` method.
