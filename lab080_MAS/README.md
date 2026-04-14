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
| **Agno** | Lightweight model-agnostic agent runtime (formerly PhiData) | Fast instantiation, clean API, MCP support, persistent history; 39k+ stars |
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

CrewAI and PydanticAI have incompatible pydantic version constraints
(`crewai` pins `pydantic<2.12`, `pydantic-ai` requires `>=2.12`), so
each framework gets its own venv. Agno is flexible enough to live with
either, but gets its own venv to keep things clean. FastAgent uses `uv`
and has its own setup (see section 4).

Create the venvs:

```bash
python3 -m venv .venv-agno
python3 -m venv .venv-crewai
python3 -m venv .venv-pydanticai
```

```bash
.venv-agno/bin/pip install -r requirements-agno.txt
.venv-crewai/bin/pip install -r requirements-crewai.txt
.venv-pydanticai/bin/pip install -r requirements-pydanticai.txt
```

Activate the appropriate venv before running each framework's scripts.

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
source .venv-crewai/bin/activate
cd crewai
python3 CRAI_01.py
cd ..
deactivate
```

Things to notice: the `@tool` decorator, the `process=Process.sequential`
pipeline, and how `memory=True` gives the crew cross-task context.

## 2. Agno

Agno (formerly PhiData, 39k+ GitHub stars) is a lightweight,
model-agnostic agent framework. Agents are plain Python objects with a
model, tools, and optional persistent history backed by SQLite or
Postgres. It supports multi-agent coordination through a `Team`
abstraction, first-class MCP tool integration, and an optional
AgentOS/FastAPI layer to turn any agent into a REST API.

```bash
source .venv-agno/bin/activate
cd agno
python3 AN_01.py             # Multi-agent Team (Researcher + Writer)
python3 AN_02.py             # Chat history with SQLite persistence
python3 AN_03_mcp_agent.py   # MCP tool (Agno docs) + persistent history
cd ..
deactivate
```

Compare Agno's `Team` abstraction with CrewAI's `Crew`: both
coordinate multiple agents, but Agno keeps the API surface smaller.
Exercise 3 shows how Agno connects to an MCP server with a single
`MCPTools(url=...)` call, making it a good stepping stone from lab070.

## 3. PydanticAI

PydanticAI (from the Pydantic team, 16k+ stars) leans into type safety.
Agents return Pydantic models instead of raw strings, and tool
definitions are validated at import time. It is model-agnostic; these
exercises use Anthropic Claude to demonstrate provider flexibility.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

```bash
source .venv-pydanticai/bin/activate
cd pydanticai
python3 PD_01.py    # Web search tool
python3 PD_02.py    # Code execution tool
cd ..
deactivate
```

If you come from a typed-Python background, PydanticAI will feel
natural. Notice how the structured output contract is part of the
agent definition, not an afterthought.

> **Note**: PydanticAI pulls in heavy transitive dependencies
> (OpenTelemetry, Logfire). If you see version conflicts during
> `pip install`, they are cosmetic and do not affect the exercises.

## 4. FastAgent

FastAgent is built around MCP from the ground up. Every tool is an MCP
server, and the framework handles transport, retries, and session
management. It supports agent chaining (`@fast.chain`) and orchestrator
patterns (`@fast.orchestrator`) for multi-agent coordination.

FastAgent uses `uv` instead of pip, so it runs in its own venv:

```bash
cd fastagent
uv venv && uv init --bare && uv add fast-agent-mcp
```

| # | Directory | Pattern |
|---|-----------|---------|
| 1 | `example1/` | Interactive agent (OpenAI gpt-4o) |
| 2 | `example2/` | Remote instructions (XSS education) |
| 3 | `example3/` | Microsoft Learn MCP (streamable HTTP, no tokens) |
| 4 | `example4/` | K8s security auditor (orchestrator + local MCP servers) |

```bash
cd example1 && uv run agent.py    # simplest example
cd ..
```

FastAgent is the most MCP-native framework in this lab. If you liked
lab070's MCP exercises, this is where those ideas scale to real
multi-agent workflows.

## Additional resources

- CrewAI docs: https://docs.crewai.com
- Agno docs: https://docs.agno.com
- PydanticAI docs: https://ai.pydantic.dev
- FastAgent repo: https://github.com/evalstate/fast-agent
- Microsoft Agent Framework (successor to AutoGen): https://github.com/microsoft/agent-framework
- Distributed agent runtime paper: https://arxiv.org/abs/2411.04468

## Cleanup environment

```bash
rm -rf .venv-agno .venv-crewai .venv-pydanticai
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
