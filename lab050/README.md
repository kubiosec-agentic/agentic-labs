![OpenAI](https://img.shields.io/badge/OpenAI-lightblue)
![LangChain](https://img.shields.io/badge/LangChain-lightgrey)
![Tools](https://img.shields.io/badge/Tools-purple)
![Agents](https://img.shields.io/badge/Agents-orange)
![Python](https://img.shields.io/badge/Python-blue) 


# LAB050: Tool Based Workflows in LangChain
## Introduction
In this lab, you will learn how to build and extend tool-augmented LLM workflows using LangChain and OpenAI. We’ll start with simple, standalone chains and later progress toward agents that can call tools, process their outputs, and reason about the next step. You will also learn how to inspect and debug API calls using mitmproxy.

By completing this lab, you will:
- Understand the basics of creating LangChain chains with and without tools
- Learn how to integrate external APIs (e.g., Wikipedia, weather services)
- Explore structured output handling for tool responses
- Experiment with OpenAI’s Responses API in a LangChain context
- Inspect model–tool interactions for debugging and transparency

This lab is ideal for developers who want practical, hands-on experience with building, extending, and debugging LLM agents that can interact with real-world data sources.

## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab050/bin/activate
```
To avoide the **_LangSmith_** warnings (build, test, debug, and monitor framework developed **_LangChain_**)
```
export LANGCHAIN_TRACING_V2" = "false"
export LANGCHAIN_API_KEY"= ""
```
In your code you can add:
```
# Suppress LangSmith warnings 
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langsmith")
```

## Lab instructions
#### Example 1: LangChain chain without tool support
This script demonstrates how to use a LangChain chain without any tool integration or structured output.
```
python3 LC_01.py
```
#### Example 2: LangChain chain with tool integration and structured output example
This script demonstrates how to use a LangChain chain **with tool integration and structured output**. It connects an LLM to a simple weather tool, handles tool invocation and result parsing and feeds the result back into the chain for a final response. It uses the `ChatOpenAI` from `langchain_openai` class that provides an interface for interacting with OpenAI's chat-based language models, like GPT-3.5 and GPT-4. It simplifies the process of sending prompts to these models and receiving their responses, making it easier to build conversational AI applications.
```
python3 LC_02.py
```
There is a real weather app example to try out, see [lab990_addendum](../lab990_addendum/)

#### Example 3: LangChain chain with using OpenAI responses API
In this lab, we explore how to extend a language model with tool integration using LangChain and **OpenAI’s Responses API**. We initialize a ChatOpenAI instance with the lightweight `gpt-4.1-mini` model, then bind it to a preview web search tool. This allows the model to augment its responses with live information from the web. Finally, we invoke the tool-enabled LLM to retrieve a positive news story from the current day and display the result.
```
python3 LC_03.py
```
#### Example 4: Building a Custom Translation Pipeline with LangChain and OpenAI (Advanced)
In this lab, we demonstrate how to create a custom LangChain pipeline that integrates directly with the OpenAI API. We start by defining a ChatPromptTemplate for translating text into French, then implement a RunnableLambda to send messages to OpenAI’s gpt-4 model. By combining the prompt, the LLM call, and a StrOutputParser into a runnable chain, we create a simple yet flexible translation workflow. Finally, we test the chain by translating a sample English phrase into French and printing the result.
```
python3 LC_core.py
```

## Cleanup environment
```
unset OPENAI_BASE_URL
```
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
