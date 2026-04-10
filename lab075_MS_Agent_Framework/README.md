![Microsoft](https://img.shields.io/badge/Microsoft-blue) ![Agent_Framework](https://img.shields.io/badge/Agent_Framework_1.0-GA-green) ![Python](https://img.shields.io/badge/Python-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Azure](https://img.shields.io/badge/Azure-0078D4)

# LAB075: Microsoft Agent Framework

## Introduction

The **Microsoft Agent Framework** reached GA (version 1.0) in April
2026. It unifies AutoGen and Semantic Kernel into a single agent
runtime with a clean Python API and first-class support for both
**OpenAI** and **Azure OpenAI** backends.

This lab walks through the framework from simplest to most advanced:

| Exercise | File | What it covers |
|----------|------|---------------|
| 1 | `MAF_01_openai_agent.py` | Simple agent with OpenAI backend |
| 2 | `MAF_02_azure_agent.py` | Same agent, Azure backend (side-by-side diff) |
| 3 | `MAF_03_middleware.py` | Chat middleware + function middleware (security guardrails) |
| 4 | `MAF_04_workflow.py` | Worker/Reviewer workflow with reflection pattern |

Exercises 1, 3, and 4 run against the OpenAI API and need only an
`OPENAI_API_KEY`. Exercise 2 shows the Azure equivalent so you can see
exactly what changes when migrating from OpenAI to Azure.

## OpenAI vs Azure: what changes

The framework abstracts the backend behind a chat client interface.
Switching from OpenAI to Azure requires only three changes:

|   | OpenAI | Azure |
|---|--------|-------|
| **Extra import** | (none) | (none) |
| **Client constructor** | `OpenAIChatClient()` | `OpenAIChatClient(model=..., azure_endpoint=..., api_key=...)` |
| **Auth mechanism** | `OPENAI_API_KEY` env var | `AZURE_OPENAI_API_KEY` env var |
| **Env vars** | `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_CHAT_MODEL` |

Same class, same import path. Azure routing is activated by passing
`azure_endpoint` and `credential`.

Everything else, tools, instructions, middleware, workflows, stays
identical. Compare `MAF_01_openai_agent.py` and `MAF_02_azure_agent.py`
side-by-side to see the full picture.

## Set up your environment

```bash
./lab_setup.sh
source .lab075/bin/activate
```

### Environment variables

| Variable | Exercises | Example |
|----------|-----------|---------|
| `OPENAI_API_KEY` | 1, 3, 4 | `sk-...` |
| `OPENAI_CHAT_MODEL` | 1, 3, 4 | `gpt-4o-mini` |
| `AZURE_OPENAI_API_KEY` | 2 | `<your-azure-api-key>` |
| `AZURE_OPENAI_ENDPOINT` | 2 | `https://<resource>.cognitiveservices.azure.com/` |
| `AZURE_OPENAI_CHAT_MODEL` | 2 | `gpt-5-nano` |

```bash
# Exercises 1, 3, 4 (OpenAI)
export OPENAI_API_KEY="sk-..."
export OPENAI_CHAT_MODEL="gpt-4o-mini"

# Exercise 2 (Azure, optional)
export AZURE_OPENAI_API_KEY="<your-azure-api-key>"
export AZURE_OPENAI_ENDPOINT="https://<resource>.cognitiveservices.azure.com/"
export AZURE_OPENAI_CHAT_MODEL="gpt-5-nano"
```

> If you do not have an Azure OpenAI resource, skip exercise 2.
> Exercises 1, 3, and 4 cover the same framework concepts using the
> OpenAI backend.

## Exercises

### 1. Simple agent (OpenAI)

A weather agent with a single tool. This is the "hello world" of the
framework: define a function, register it as a tool, and let the agent
call it.

```bash
python3 MAF_01_openai_agent.py
```

Things to notice: the `Annotated[str, "..."]` tool parameter syntax,
the `create_agent` factory, and how the agent decides to call
`get_weather` twice (once per city).

### 2. Same agent (Azure)

Identical logic, Azure backend. Open both files side-by-side and diff
them. The tool, the instructions, and the query are copy-pasted; only
the client setup differs.

```bash
python3 MAF_02_azure_agent.py
```

Key differences: explicit `api_key`, `azure_endpoint`, and `model`
parameters on the constructor, and streaming via
`agent.run(..., stream=True)`.

### 3. Middleware (OpenAI)

Two middleware layers that intercept messages and tool calls:

- **Chat middleware** (`@chat_middleware`): inspects the user message
  before the LLM sees it. If it finds sensitive keywords (password,
  secret, token), it short-circuits with a refusal. The LLM is never
  called.
- **Function middleware** (`@function_middleware`): inspects tool call
  arguments after the LLM decides to call a tool but before the
  function runs. It blocks requests for fictional locations.

```bash
python3 MAF_03_middleware.py
```

The script runs three test cases: a normal request, a blocked tool
call, and a blocked chat message. Watch which middleware fires in each
case.

> Security angle: middleware is the framework's answer to guardrails.
> Instead of scattering validation across every tool function, you
> write it once and attach it to the agent. This is the pattern you
> want for production deployments.

### 4. Worker/Reviewer workflow (OpenAI)

A cyclic workflow where a Worker generates a response, a Reviewer
evaluates it with structured output (approve/reject + feedback), and
if rejected the Worker retries with the feedback. Only approved
responses are emitted to the user.

```bash
python3 MAF_04_workflow.py
```

This demonstrates `WorkflowBuilder`, `Executor`, `@handler`, and
`AgentRunUpdateEvent`. It is the framework's equivalent of
"agent-to-agent handoffs" in the OpenAI Agents SDK.

## Reference files

The directory also contains the original examples from the addendum:

| File | Description |
|------|-------------|
| `openai_agent.py` | Minimal OpenAI agent (original reference) |
| `azure_agent.py` | Azure agent with streaming (original reference) |
| `azure_agent_mcp.py` | Azure agent with MCP streamable HTTP tool (Microsoft Learn) |
| `azure_code_interpreter.py` | Azure agent with hosted code interpreter |
| `openai_workflow.py` | Full Worker/Reviewer workflow (more detailed than MAF_04) |

## Additional resources

- Framework repo: https://github.com/microsoft/agent-framework
- Docs: https://learn.microsoft.com/en-us/agent-framework/overview/
- Migration from AutoGen: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/

## Cleanup

```bash
deactivate
```

```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
