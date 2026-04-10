# PydanticAI

[PydanticAI](https://ai.pydantic.dev) is a type-safe agent framework
from the team behind Pydantic. It brings the same validation-first
philosophy to LLM agents: structured output is a first-class concept,
tool definitions are validated at import time, and the framework
supports multiple model providers through a single interface.

Key features relevant to this lab:

- **Model-agnostic**: works with OpenAI, Anthropic, Google, Groq, and
  others. These exercises use Anthropic Claude to show provider
  flexibility.
- **Built-in tools**: `WebSearchTool` and `CodeExecutionTool` come
  with the framework, no extra packages needed.
- **Structured output**: agents can return Pydantic models instead of
  raw strings, with validation enforced at the framework level.
- **Logfire integration**: optional observability through Pydantic's
  Logfire platform.

## Prerequisites

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Exercises

| Exercise | File | What it covers |
|----------|------|----------------|
| 1 | `PD_01.py` | Web search tool with structured output |
| 2 | `PD_02.py` | Code execution tool (sandboxed Python) |

### 1. Web search

Uses `WebSearchTool` to search the web and return a summary. The
agent decides when and how to search based on the prompt.

```bash
python3 PD_01.py
```

### 2. Code execution

Uses `CodeExecutionTool` to write and run Python code in a sandboxed
environment. The agent generates code, executes it, and returns the
result.

```bash
python3 PD_02.py
```

## Docs

- https://ai.pydantic.dev
- https://ai.pydantic.dev/llms-full.txt
