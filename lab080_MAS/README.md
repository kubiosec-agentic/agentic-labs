![Python](https://img.shields.io/badge/Python-blue) ![CrewAI](https://img.shields.io/badge/CrewAI-pink) ![Agno](https://img.shields.io/badge/Agno-green) ![PydanticAI](https://img.shields.io/badge/PydanticAI-purple) ![FastAgent](https://img.shields.io/badge/FastAgent-orange)

# LAB080: Multi-Agent Frameworks

## Introduction

This lab gives you a side-by-side tour of four open-source multi-agent
frameworks. The goal is not to master any single one; it is to see how
each solves the same core problems (tool calling, agent coordination,
memory, structured output) so you can pick the right one for a given
project.

| Framework | What it is | Why it is here |
|-----------|-----------|----------------|
| **CrewAI** | Role-based multi-agent workflows with built-in tool ecosystem | Most popular Python-native multi-agent framework; 45k+ GitHub stars, production-ready |
| **Agno** | Lightweight agent runtime (formerly PhiData) | Fast instantiation, clean API, growing ecosystem |
| **PydanticAI** | Type-safe agent framework from the Pydantic team | First-class structured output, strong typing, weekly releases |
| **FastAgent** | MCP-native agent framework | Deep MCP integration, agent chaining, orchestrator patterns |

> **Note on AutoGen**: AutoGen (Microsoft) entered maintenance mode in
> early 2026 and has been superseded by the
> [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
> (GA 1.0, April 2026). The AutoGen examples remain in the `autogen/`
> subfolder for reference, but they are no longer part of the guided
> exercises. See **lab075** for the current Microsoft stack.

## Set up your environment

```bash
export OPENAI_API_KEY="xxxxxxxxx"
```

```bash
python3 -m venv .lab080
source .lab080/bin/activate
pip install -r requirements.txt
```

## 1. CrewAI

CrewAI organizes work around **roles**: you define agents with a title,
backstory, and goal, then wire them into a sequential or hierarchical
crew. The framework handles delegation, memory, and caching.

This example sets up a Senior Researcher and a Writer. The researcher
gathers insights using a search tool; the writer turns the findings
into a markdown article.

```bash
export SERPER_API_KEY=xxxxxxxxxx
```

```bash
cd crewai
python3 CRAI_01.py
cd ..
```

Things to notice: the `@tool` decorator, the `process=Process.sequential`
pipeline, and how `memory=True` gives the crew cross-task context.

## 2. Agno

Agno (formerly PhiData) focuses on speed and simplicity. Agents are
plain Python objects with a model, tools, and optional memory.

```bash
cd agno
python3 AN_01.py    # Team of researcher + writer agents
python3 AN_02.py    # Agent memory with add_history_to_messages
cd ..
```

Compare Agno's `Team` abstraction with CrewAI's `Crew`: both
coordinate multiple agents, but Agno keeps the API surface smaller.

## 3. PydanticAI

PydanticAI leans into type safety. Agents return Pydantic models
instead of raw strings, and tool definitions are validated at import
time.

```bash
cd pydanticai
python3 PD_01.py    # Web search tool
python3 PD_02.py    # Code execution tool
cd ..
```

If you come from a typed-Python background, PydanticAI will feel
natural. Notice how the structured output contract is part of the
agent definition, not an afterthought.

## 4. FastAgent

FastAgent is built around MCP from the ground up. Every tool is an MCP
server, and the framework handles transport, retries, and session
management.

The `fastagent/` subfolder has seven progressive examples:

| Example | Pattern |
|---------|---------|
| example1 | Interactive agent (Anthropic Claude) |
| example2 | XSS learning agent with remote instructions |
| example3 | YouTube transcriber + Exa search (MCP servers) |
| example4 | Agent chaining: URL fetcher then social-media writer |
| example5 | Orchestrator-workers pattern |
| example6 | Kubernetes security auditor (4-agent orchestration) |
| example7 | Pentest tutor with OpenMemory MCP |

```bash
cd fastagent
# each example has its own subfolder with a README
cd ..
```

FastAgent is the most MCP-native framework in this lab. If you liked
lab070's MCP exercises, this is where those ideas scale to real
multi-agent workflows.

## AutoGen (legacy reference)

The `autogen/` subfolder contains five examples (AG_01 through AG_05)
covering MCP integration, group chat, MultimodalWebSurfer, MagenticOne,
and Docker code execution. These still run but target AutoGen 0.4,
which is in maintenance mode. For the current Microsoft agent story,
see **lab075**.

## Additional resources

- CrewAI docs: https://docs.crewai.com
- Agno docs: https://docs.agno.com
- PydanticAI docs: https://ai.pydantic.dev
- FastAgent repo: https://github.com/evalstate/fast-agent
- Microsoft Agent Framework (successor to AutoGen): https://github.com/microsoft/agent-framework
- Distributed agent runtime paper: https://arxiv.org/abs/2411.04468

## Cleanup environment

```bash
deactivate
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
