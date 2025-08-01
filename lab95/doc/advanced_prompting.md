
# Advanced Prompting with LangChain

## Introduction
This example demonstrates how to define **user prompts** using **LangChain best practices**, and run them with different **chat models** like `ChatOllama`, `ChatOpenAI`, or `ChatAnthropic`. We'll use a `ChatPromptTemplate` to structure the conversation and show how to build a full chain.

## 🔧 Code Example
```python
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

# Initialize chat model
chat = ChatOllama(model="phi3:3.8b", temperature=0)

# Define prompt using roles
system_msg = SystemMessagePromptTemplate.from_template(
    "You are a witty assistant who tells short and funny jokes."
)
user_msg = HumanMessagePromptTemplate.from_template("{input}")

# Combine messages into a structured chat prompt
prompt = ChatPromptTemplate.from_messages([system_msg, user_msg])

# Chain: prompt → model → output parser
chain = prompt | chat | StrOutputParser()

# Run the chain
response = chain.invoke({"input": "Tell me a joke about light bulbs!"})
print(response)
```

### Step 1
#### Import LangChain components
```python
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
```

LangChain provides special **message-based prompt templates** to simulate natural conversations. This helps structure interactions for models like GPT, Claude, or Gemini.

- `SystemMessagePromptTemplate`: defines the assistant’s **persona or behavior**
- `HumanMessagePromptTemplate`: defines the **user input**
- `ChatPromptTemplate`: combines messages into a **chat-style prompt**

### Step 2
#### Choose your model
```python
from langchain_ollama import ChatOllama
chat = ChatOllama(model="phi3:3.8b", temperature=0)
```

This initializes a **chat model**. You can switch to other providers by changing the import and model name:

```python
# from langchain_openai import ChatOpenAI
# chat = ChatOpenAI(model="gpt-4")

# from langchain_anthropic import ChatAnthropic
# chat = ChatAnthropic(model="claude-3-opus-20240229")
```

### Step 3
#### Create a structured prompt
```python
system_msg = SystemMessagePromptTemplate.from_template(
    "You are a witty assistant who tells short and funny jokes."
)
user_msg = HumanMessagePromptTemplate.from_template("{input}")
prompt = ChatPromptTemplate.from_messages([system_msg, user_msg])
```

- This creates a reusable, structured conversation prompt.
- `{input}` is a placeholder that you can fill in when running the chain.


### Step 4
#### Build and run the chain
```python
chain = prompt | chat | StrOutputParser()
response = chain.invoke({"input": "Tell me a joke about light bulbs!"})
```

- This uses **LangChain Expression Language (LCE)**: a clean way to link prompt → model → output.
- The final result is stored in the `response` variable.


