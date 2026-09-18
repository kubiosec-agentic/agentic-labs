![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![Tools](https://img.shields.io/badge/Tools-purple) ![Python](https://img.shields.io/badge/Python-blue)

# LAB054: LangChain Basics and Tools

## Introduction

In the previous labs you called OpenAI through raw HTTP and the official SDK. LangChain adds a layer on top: a common interface for models, prompt templates, and a way to compose them into chains and tool-calling loops.

This lab goes from a bare LangChain call to a real agent loop in six short scripts. The security angle is in the last steps: where does the tool code actually run, and what can go wrong when the model controls it.

| Step | Script | What it shows |
|------|--------|---------------|
| 1 | `LC_01.py` | Bare LLM call, no tools |
| 2 | `LC_02.py` | Prompt templates with roles, chains with the `\|` operator (LCEL) |
| 3 | `LC_03.py` | `@tool` + `bind_tools`, the four-phase tool-call cycle |
| 4 | `LC_04.py` | Hosted tools via the Responses API (web search, code interpreter) |
| 5 | `LC_05.py` | Local Python REPL tool in a multi-step agent loop |
| 6 | `LC_06.py` | Raw OpenAI function calling wrapped in a LangChain chain |

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
```

```bash
./lab_setup.sh
source .lab054/bin/activate
```

Optional, to silence LangSmith tracing warnings:

```bash
export LANGCHAIN_TRACING_V2="false"
export LANGCHAIN_API_KEY=""
```

## Lab instructions

### Step 1: Basic LLM call (`LC_01.py`)

The simplest LangChain program: create a `ChatOpenAI` model, call `.invoke()`, print the result.

```bash
python3 LC_01.py
```

**What to observe:**
- The result is an `AIMessage` with `.content` and `.response_metadata` (model, token usage).
- No tools yet, the model answers from what it learned during training.

### Step 2: Prompts and chains (`LC_02.py`)

Two things LangChain is good at: prompt templates with `system` and `user` roles, and chaining components with the pipe operator.

```bash
python3 LC_02.py
```

**What to observe:**
- `prompt | llm | parser` is a chain. Each piece is a "Runnable", the output of one becomes the input of the next.
- `StrOutputParser` turns the `AIMessage` into a plain string.
- The second part pipes one chain into another: the joke becomes the input of the review.
- Compare the roles with lab010: same system/user concept, one abstraction level higher.

### Step 3: Tool binding (`LC_03.py`)

Defines a `get_weather` tool with the `@tool` decorator and a Pydantic input schema, binds it with `bind_tools`, and walks through the full cycle: model asks for the tool, your code runs it, the result goes back, the model answers.

```bash
python3 LC_03.py
```

**What to observe:**
- The first response has no text, only `tool_calls`. The model decided it needs the tool.
- The `ToolMessage` must carry the matching `tool_call_id` or the API rejects it (same as lab050).
- Compare with lab050: same four phases, but `@tool` generates the JSON schema for you.

### Step 4: Hosted tools (`LC_04.py`)

`output_version="responses/v1"` switches `ChatOpenAI` to the Responses API. That gives you OpenAI's hosted tools: web search and a code interpreter that run on OpenAI's servers.

```bash
python3 LC_04.py
```

**What to observe:**
- Web search: the model uses live data, unlike Step 1. In the `responses/v1` format `response.content` is a list of blocks, look for the text block and the annotations with source URLs.
- Code interpreter: the model writes Python and runs it in an OpenAI sandbox. Nothing runs on your machine.
- Think about it: what could a prompt injection make that interpreter do?

### Step 5: Local Python REPL agent loop (`LC_05.py`)

Now the code runs on **your** machine. A `python_repl` tool is bound to the model, and a loop keeps going until the model stops emitting tool calls (capped by `MAX_STEPS`).

```bash
python3 LC_05.py
```

**What to observe:**
- The loop: `invoke -> tool_calls? -> run locally -> ToolMessage -> invoke again`.
- The REPL namespace persists between calls, so the model can build up state.
- **Security:** model-generated Python runs unsandboxed in your process. It can read files, leak `OPENAI_API_KEY`, open network connections. Run this only in a disposable environment. Compare with Step 4 where the same idea runs in OpenAI's sandbox.

### Step 6: Function calling inside a chain (`LC_06.py`)

Drops down to the raw OpenAI SDK, wrapped in a `RunnableLambda` so it still composes as a chain. Adds a `get_current_datetime` tool.

```bash
python3 LC_06.py
```

**What to observe:**
- The tool schema is raw JSON (lab050 style), not `@tool`.
- The chain `prompt | llm | parser` has no idea tools are involved. The tool loop is hidden inside the `RunnableLambda`.

## Note: fast-moving APIs

LangChain's API changes often. Older tutorials use `ConversationChain`, `langchain.memory`, or `RunnableWithMessageHistory` for conversation memory. All of these were the official recommendation at some point and all are now deprecated (LangGraph persistence replaced them, see lab064).

This is not just a maintenance issue. Code copied from a blog, Stack Overflow, or an LLM with an old training cutoff comes with whatever was current then, including known vulnerabilities and abandoned dependencies. Read deprecation warnings instead of silencing them, check the changelog, and scan your dependencies (lab050 `pip-audit`).

A working example of the deprecated memory pattern is kept in [lab990_addendum/langchain](../lab990_addendum/langchain/) (`multi_turn.py`) if you want to see the warning yourself.

## Cleanup environment

```bash
unset LANGCHAIN_TRACING_V2
unset LANGCHAIN_API_KEY
deactivate
./lab_cleanup.sh
```

## Going further

[lab990_addendum/langchain](../lab990_addendum/langchain/) has more LangChain examples: running a local HuggingFace model, swapping providers (OpenAI vs Gemini), a real weather API tool, shell script security reviews, and a Gradio writing assistant.

## What's next

- **lab060**: OpenAI Agents SDK
- **lab064**: LangGraph, stateful agent graphs and a CTF

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
