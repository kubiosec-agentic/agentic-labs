# Welcome to Agentic-Labs Training

**Agentic-Labs** is an advanced, hands-on training experience for those who want to go beyond the hype and dive deep into the **foundations of agentic AI**. Whether you're a **DevOps engineer**, **ethical hacker**, **network specialist**, **pen-tester**, or **developer**, this course is your gateway to mastering the **low-level internals** of the OpenAI ecosystem.

## 🔍 What You'll Learn

- How to work directly with the **OpenAI API Chat completion**, the brand new **OpenAI responses API** and the new **OpenAI Agents SDK**
- How to build and chain intelligent agents using **LangChain** and custom tools
- The core principles behind **agentic systems** that plan, reason, and act
- How to integrate AI agents into real-world workflows for **security**, **automation**, and **development**
- How to debug AI agents using **MITM proxy** and **tracing**
- Security pitfalls and hacking challenges
  
This is more than just a workshop, it's an exploration of how intelligent agents are transforming the way we build and secure systems.
By the end, you'll not only know how to use AI, you'll know how to *engineer* it.
Let’s plug in, patch deep, and push the boundaries of what’s possible.

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

| Lab | Focus Area                                      | Tools & Topics                              |
|-----|-------------------------------------------------|---------------------------------------------|
| [lab000_setup](./lab000_setup) | Lab environment setup                        | bash scripts, environment preparation       |
| [lab010](./lab010) | OpenAI - Chat completions basics              | curl, few-shot prompts, image analysis     |
| [lab020](./lab020) | OpenAI - Responses API basics                 | curl, tools, structured output              |
| [lab032](./lab032) | Advanced OpenAI features                      | python, chat, responses, structured output  |
| [lab035](./lab035) | Advanced prompting techniques                 | python, multi-turn conversations, HuggingFace |
| [lab040](./lab040) | RAG (Retrieval Augmented Generation)         | python, RAG, chroma, llama-index, OpenAI VectorStore |
| [lab050](./lab050) | LangChain tools and agents                    | python, langchain, tool integration        |
| [lab052](./lab052) | OpenAI Agent SDK                              | python, OpenAI Agent SDK, vulnerability analysis |
| [lab053](./lab053) | LangChain advanced features                   | python, langchain, advanced agent patterns |
| [lab060](./lab060) | Multi-agent orchestration                     | python, OpenAI Agent SDK, MCP integration  |
| [lab070](./lab070) | MCP (Model Context Protocol)                 | python, MCP, SSE, streamable responses     |
| [lab080](./lab080) | Multi-agent frameworks                       | python, Autogen, CrewAI, PydanticAI, FastAgent |
| [lab082_langgraph](./lab082_langgraph) | LangGraph workflows                | python, LangGraph, workflow orchestration  |
| [lab090](./lab090) | Enterprise-grade agents with tracing         | python, OpenAI tracing, metadata, persistence |
| [lab093](./lab093) | Memory management for agents                 | python, Mem0, Qdrant, persistent memory    |
| [lab100](./lab100) | Advanced agent patterns                      | TBD                                         |
| [lab105_evaluations](./lab105_evaluations) | Agent evaluation and testing       | python, evaluation frameworks              |
| [lab110](./lab110) | Production deployment                        | TBD                                         |
| [lab990_addendum](./lab990_addendum) | Additional examples and patterns    | python, various frameworks, specialized use cases |

Each lab has a different environment, feel free to fork, hack, and explore beyond the tasks!


