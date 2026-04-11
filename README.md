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
ssh -i agentics-key.pem \
    -L 5000:localhost:5000 \
    -L 5173:localhost:5173 \
    -L 6274:localhost:6274 \
    -L 8000:localhost:8000 \
    -L 8001:localhost:8001 \
    -L 8080:localhost:8080 \
    -L 8081:localhost:8081 \
    -L 8089:localhost:8089 \
    -L 8501:localhost:8501 \
    ubuntu@x.x.x.x.x
```

| Port | Used by |
|------|---------|
| 5000 | Flask / API server |
| 5173 | MCP Inspector UI (lab071) |
| 6274 | MCP Inspector proxy (lab071) |
| 8000 | MCP streamable HTTP server (lab070) |
| 8001 | Rogue MCP server for shadowing exercises (lab070/lab071) |
| 8080 | mitmproxy reverse-proxy for OpenAI API (lab070 section 7) |
| 8081 | mitmweb UI (lab070 section 7) |
| 8089 | mitmproxy reverse-proxy for MCP server (lab070 section 7) |
| 8501 | Streamlit |
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
| [lab004_transformers](./lab004_transformers) | Transformers: generation vs extraction | python, Qwen 2.5, RoBERTa, docker |
| [lab010_ChatCompletion](./lab010_ChatCompletion) | OpenAI Chat Completions basics | curl, few-shot prompts, image analysis |
| [lab020_ResponsesAPI](./lab020_ResponsesAPI) | OpenAI Responses API basics | curl, tools, web search, structured output |
| [lab032_PythonFrameworks](./lab032_PythonFrameworks) | Advanced OpenAI features | python, chat completions, responses API, structured output |
| [lab035_Langchain](./lab035_Langchain) | LangChain and advanced prompting | python, multi-turn conversations, HuggingFace |
| [lab040_RAG](./lab040_RAG) | Retrieval Augmented Generation (RAG) | python, LlamaIndex, Chroma, OpenAI VectorStore |
| [lab050_OpenAI_Tools](./lab050_OpenAI_Tools) | OpenAI function calling and tool use | python, tools, pip-audit, mitmproxy |
| [lab054_LangChain_Tools](./lab054_LangChain_Tools) | LangChain tools and agents | python, LangChain, tool integration |
| [lab060_OpenAI_Agents](./lab060_OpenAI_Agents) | Multi-agent orchestration | python, OpenAI Agents SDK, MCP integration |
| [lab061_Google_Agents](./lab061_Google_Agents) | Google ADK | python, Google ADK, Gemini, agents |
| [lab064_Langgraph](./lab064_Langgraph) | LangGraph stateful workflows + agent CTF | python, LangGraph, StateGraph, CTF, prompt injection |
| [lab070_MCP](./lab070_MCP) | Model Context Protocol (MCP) core: transports, sampling, memory graph, security | python, fastmcp, MCP, streamable HTTP, SSE, stdio, sampling |
| [lab071_MCP_Inspector](./lab071_MCP_Inspector) | MCP Inspector and wire-level debugging | MCP Inspector, mcp-debugging, mitmproxy, Wireshark |
| [lab075_MS_Agent_Framework](./lab075_MS_Agent_Framework) | Microsoft Agent Framework (GA 1.0) | python, agent-framework, OpenAI, Azure OpenAI, middleware, workflows |
| [lab080_MAS](./lab080_MAS) | Multi-agent frameworks | python, CrewAI, Agno, PydanticAI, FastAgent |
| [lab085_OpenAI_Memory](./lab085_OpenAI_Memory) | OpenAI Agents with memory | python, OpenAI Agents SDK, SQLiteSession |
| [lab087_Mem0](./lab087_Mem0) | Mem0 intelligent memory layer | python, Mem0, Qdrant, Docker, OpenAI |
| [lab090_Enterprise](./lab090_Enterprise) | Enterprise-ready agent systems | python, OAuth 2.0, tracing, RAG metadata, Chroma |
| [lab105_evaluations](./lab105_evaluations) | Prompt evaluation | curl, OpenAI Evals, JSONL, classification testing |
| [lab110_A2A](./lab110_A2A) | Agent-to-Agent Communication (A2A) | python, A2A protocol, Google ADK, MS Agent Framework, cross-vendor interop |
| [lab120_Security](./lab120_Security) | Bypassing LLM guardrails and prompt injection | python, OpenAI, prompt engineering, MCP injection, guardrails |
| [lab122_runtime](./lab122_runtime) | Runtime security monitoring | python, Tetragon, eBPF, Docker, process tracing, egress filtering |
| [lab990_addendum](./lab990_addendum) | Additional examples and patterns | python, various frameworks, specialized use cases |

Each lab has a different environment, feel free to fork, hack, and explore beyond the tasks!


