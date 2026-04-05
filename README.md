# Welcome to Agentic-Labs Training

**Agentic-Labs** is an advanced, hands-on training experience for those who want to go beyond the hype and dive deep into the **foundations of agentic AI**. Whether you're a **DevOps engineer**, **ethical hacker**, **network specialist**, **pen-tester**, or **developer**, this course is your gateway to mastering the **low-level internals** of the OpenAI ecosystem.

## 🔍 What You'll Learn

- How to work directly with the **OpenAI Chat Completions API**, the brand new **OpenAI Responses API**, and the new **OpenAI Agents SDK**
- How to build and chain intelligent agents using **LangChain** and custom tools
- The core principles behind **agentic systems** that plan, reason, and act
- How to integrate AI agents into real-world workflows for **security**, **automation**, and **development**
- How to debug AI agents using **MITM proxy** and **tracing**
- Security pitfalls and hacking challenges
  
This is more than just a workshop, it's an exploration of how intelligent agents are transforming the way we build and secure systems.
By the end, you'll not only know how to use AI, you'll know how to *engineer* it.
Let’s plug in, dig deep, and push the boundaries of what’s possible.

Welcome to the lab and let's **#HACKTOLEARN** 🚀

## 🔐 Getting Access to the Lab via SSH

Each lab student has access to a virtual machine, accessible over SSH. Use the credentials provided to you and use the following pattern to connect:
### Terminal_1
```bash
ssh -i agentics-key.pem -L 8080:localhost:8080 \
               -L 8081:localhost:8081 \
               -L 8000:localhost:8000 \
               -L 5000:localhost:5000 \
               -L 8501:localhost:8501 \
                ubuntu@x.x.x.x.x
```
```
git clone https://github.com/kubiosec-agentic/agentic-labs.git
```
```
cd agentic-labs/lab000_setup/
```
```
./setup.sh
```
```
./prepare_labs.sh
```
```
cd ..
```
### To open Terminal_2 and Terminal_3 during labs use:
```bash
ssh -i agentics-key.pem  ubuntu@x.x.x.x.x
```
**Note**: 
- Provided lab environment is based on Ubuntu, T2.medium and 50G root volume. 
- Labs are tested and should also run on Mac.

## 🧪 Lab Overview

Each lab is structured to gradually build your understanding and capabilities, from basic API calls to full agent orchestration and security integration.

| Lab | Focus Area | Tools & Topics |
|-----|------------|----------------|
| [lab000_setup](./lab000_setup) | Lab environment setup | bash, environment preparation |
| [lab004_transformers](./lab004_transformers) | LLM Security Analysis with Qwen Model | python, docker, transformers, security |
| [lab010_ChatCompletion](./lab010_ChatCompletion) | Chat Completions API | curl, OpenAI, few-shot prompts, image analysis |
| [lab020_ResponsesAPI](./lab020_ResponsesAPI) | OpenAI Responses API | curl, OpenAI, tools, web search, streaming |
| [lab032_PythonFrameworks](./lab032_PythonFrameworks) | Python Frameworks | python, OpenAI SDK, chat completions, responses API, mitmproxy |
| [lab035_Langchain](./lab035_Langchain) | LangChain Quickstart | python, LangChain, prompting, multi-turn, HuggingFace |
| [lab040_RAG](./lab040_RAG) | Retrieval Augmented Generation (RAG) | python, LlamaIndex, Chroma, OpenAI VectorStore, Responses API |
| [lab050_OpenAI_Tools](./lab050_OpenAI_Tools) | OpenAI Function Calling and Tool Integration | python, OpenAI, tools, pip-audit, mitmproxy |
| [lab054_LangChain_Tools](./lab054_LangChain_Tools) | Tool-Based Workflows in LangChain | python, LangChain, OpenAI, agents, tools |
| [lab060_OpenAI_Agents](./lab060_OpenAI_Agents) | Multi-Agent Orchestration & OpenAI APIs | python, OpenAI Agents SDK, Responses API, guardrails |
| [lab061_Google_Agents](./lab061_Google_Agents) | Google ADK | python, Google ADK, Gemini, MCP, agents |
| [lab062_LangChain_Agents](./lab062_LangChain_Agents) | LangChain ReAct Agents (Experimental) | python, LangChain, experimental, ReAct, tools |
| [lab064_Langgraph](./lab064_Langgraph) | LangGraph - Stateful Workflow Orchestration | python, LangGraph, StateGraph, conditional routing |
| [lab070_MCP](./lab070_MCP) | Model Context Protocol (MCP) | python, MCP, OpenAI, streamable HTTP, security |
| [lab080_MAS](./lab080_MAS) | Agentic Frameworks | python, AutoGen, CrewAI, MCP, Docker |
| [lab085_OpenAI_Memory](./lab085_OpenAI_Memory) | OpenAI Agents with Memory Persistence | python, OpenAI Agents SDK, SQLiteSession |
| [lab087_Mem0](./lab087_Mem0) | Mem0 - Intelligent Memory Layer | python, Mem0, Qdrant, Docker, OpenAI |
| [lab090_Enterprise](./lab090_Enterprise) | Enterprise-Ready Agent Systems | python, OAuth 2.0, tracing, RAG metadata, Chroma |
| [lab105_evaluatuions](./lab105_evaluatuions) | Prompt Evaluation | curl, OpenAI Evals, JSONL, classification testing |
| [lab110_A2A](./lab110_A2A) | Agent-to-Agent Communication (A2A) | python, A2A protocol, agent discovery, inspector |
| [lab120_Security](./lab120_Security) | Security Analysis | python, OpenAI, security testing |
| [lab122_runtime](./lab122_runtime) | Runtime Security Monitoring | python, Tetragon, Docker, event tracing |
| [lab990_addendum](./lab990_addendum) | Additional examples and patterns | python, various frameworks, specialized use cases |
| [lab950_Template](./lab950_Template) | Lab template | template for creating new labs |

Each lab has a different environment, feel free to fork, hack, and explore beyond the tasks!


