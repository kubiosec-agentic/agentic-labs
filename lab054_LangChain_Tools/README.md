![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![Tools](https://img.shields.io/badge/Tools-purple) ![Python](https://img.shields.io/badge/Python-blue)

# LAB054: LangChain Tool Integration

## Introduction

LangChain provides a high-level abstraction over LLM providers, but the real power comes from connecting models to tools. This lab walks through six examples that progress from a bare LLM call to full tool-call cycles, Responses API hosted tools, and custom chains that wrap raw OpenAI function calling inside LangChain runnables.

The first two examples use LangChain's `bind_tools` and `@tool` decorator. The next two switch to OpenAI's Responses API (`output_version="responses/v1"`) for server-side web search and code execution. The final two drop down to the OpenAI SDK directly, wrapping it in `RunnableLambda` to show how LangChain chains compose with any callable.

| Step | Script | What it demonstrates |
|------|--------|---------------------|
| 1 | `LC_01.py` | Bare LLM invoke, no tools |
| 2 | `LC_02.py` | Tool binding with `@tool` decorator, four-phase tool-call cycle |
| 3a | `LC_03.py` | Responses API: `web_search_preview` hosted tool |
| 3b | `LC_03_CI.py` | Responses API: `code_interpreter` hosted tool |
| 4 | `LC_core.py` | Custom chain: `ChatPromptTemplate` | `RunnableLambda` (raw OpenAI) | `StrOutputParser` |
| 5 | `LC_core_tools.py` | Same chain pattern with OpenAI function calling and a datetime tool |

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
```

```bash
./lab_setup.sh
source .lab054/bin/activate
```

To suppress LangSmith tracing warnings (optional):

```bash
export LANGCHAIN_TRACING_V2="false"
export LANGCHAIN_API_KEY=""
```

## Lab instructions

### Step 1: Basic LLM query (`LC_01.py`)

A minimal call with no tools. LangChain's `ChatOpenAI` sends a single `HumanMessage` to gpt-4o and prints the raw response object.

```bash
python3 LC_01.py
```

**What to observe:**
- The response is an `AIMessage` object with `.content`, `.response_metadata`, and token usage fields.
- No tool calls happen here; the model answers from its parametric knowledge.

### Step 2: Tool binding and structured output (`LC_02.py`)

Defines a `get_weather` tool with a Pydantic input schema, binds it to the model via `bind_tools`, and walks through the complete four-phase cycle: tool request, local execution, result feedback, final answer.

```bash
python3 LC_02.py
```

**What to observe:**
- The first response contains `tool_calls` instead of a text answer. The model decided to call `get_weather` rather than answer directly.
- `tool_call_response.tool_calls[0]` gives you the function name and arguments as a dict.
- The `ToolMessage` must include the matching `tool_call_id` or the API rejects the request (same constraint as lab050's OA_02 exercise).
- Compare with lab050: same four-phase pattern, but LangChain's `@tool` decorator replaces the manual JSON schema.

There is a real weather API example in [lab990_addendum/langchain](../lab990_addendum/langchain).

### Step 3a: Responses API with web search (`LC_03.py`)

Uses `output_version="responses/v1"` to access the OpenAI Responses API through LangChain. The `web_search_preview` tool is a hosted tool: OpenAI runs the search server-side, so you do not need to implement anything locally.

```bash
python3 LC_03.py
```

**What to observe:**
- The model fetches live web content to answer the query. Compare with Step 1 where the model can only use its training data.
- The `responses/v1` output format returns a different response structure than the default Chat Completions format. Check the raw object for annotations and source URLs.

### Step 3b: Responses API with code interpreter (`LC_03_CI.py`)

Same pattern, different hosted tool. The `code_interpreter` tool lets the model write and execute Python code on OpenAI's servers to solve a math problem.

```bash
python3 LC_03_CI.py
```

**What to observe:**
- The model generates Python code, runs it in a sandboxed container, and returns the computed result.
- The `container: {"type": "auto"}` config lets OpenAI choose the runtime. This is a serverless execution environment, not your local machine.
- Think about the security implications: what code could a prompt injection trick the interpreter into running?

### Step 4: Custom translation chain (`LC_core.py`)

Drops down to the raw OpenAI SDK but wraps the call in a `RunnableLambda` so it plugs into a LangChain chain. The chain is: `ChatPromptTemplate` | `RunnableLambda(call_openai)` | `StrOutputParser`.

```bash
python3 LC_core.py
```

**What to observe:**
- The `RunnableLambda` receives a `ChatPromptValue` from the prompt template and must convert it to OpenAI message format manually.
- This pattern is useful when you need LangChain's prompt templating and chain composition but want full control over the API call (e.g., for custom headers, retries, or provider-specific parameters).

### Step 5: Chain with function calling (`LC_core_tools.py`)

Extends Step 4 by adding a `get_current_datetime` tool. The `RunnableLambda` now handles the full tool-call cycle internally: if the model requests the tool, the code executes it, appends the result, and makes a second API call for the final answer.

```bash
python3 LC_core_tools.py
```

**What to observe:**
- The tool schema is defined as raw JSON (same format as lab050), not via LangChain's `@tool` decorator. This shows the manual approach for comparison.
- The chain caller (`prompt | llm | parser`) has no idea tools are involved; the tool-call logic is encapsulated inside the `RunnableLambda`.
- The model's response includes the current timestamp, proving the tool was called.

## Cleanup environment

```bash
unset LANGCHAIN_TRACING_V2
unset LANGCHAIN_API_KEY
deactivate
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
