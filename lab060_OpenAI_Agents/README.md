![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Agents_SDK](https://img.shields.io/badge/Agents_SDK-brightgreen) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB060: OpenAI Agent SDK

## Introduction

The OpenAI Agent SDK (`openai-agents`) provides a lightweight framework for building multi-agent systems. Agents are defined with a name, instructions, optional tools, and optional handoffs to other agents. The SDK handles the tool-call loop, agent routing, and guardrail enforcement, so you can focus on the agent design rather than the plumbing.

This lab walks through nine examples that progress from a single async agent to a multi-agent security analysis pipeline. Along the way you will see handoffs, function tools, input/output guardrails, tool guardrails, and a side-by-side comparison of the raw Responses API versus the Agent SDK.

| Step | Script | What it demonstrates |
|------|--------|---------------------|
| 1 | `agent_01.py` | Your first Agent SDK script: one agent, async `Runner.run` |
| 2 | `agent_02.py` | Multi-agent handoff based on language detection |
| 3 | `agent_03.py` | Agent with a @function_tool (weather lookup) |
| 4 | `agent_04.py` | Output guardrail: block dangerous OS commands |
| 5 | `agent_05.py` | Input + output guardrails combined |
| 6 | `agent_06.py` | Responses API: security trace analysis (raw client, no SDK) |
| 7 | `agent_07.py` | Agent SDK: same analysis with structured JSON output |
| 8 | `agent_08.py` | Multi-agent pipeline: analyzer, summary writer, JSON formatter |
| 9 | `agent_09.py` | Tool guardrails: screen tool arguments and tool results |

The `data/` directory contains a sysdig system call capture (`docker-curl-https.txt`) used by Steps 6-8.

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
```

```bash
./lab_setup.sh
source .lab060/bin/activate
```

## Lab instructions

### Step 1: Your first Agent SDK script (`agent_01.py`)

The smallest useful Agent SDK program: one agent, no tools, no handoffs. It asks the agent for a haiku and prints the answer.

```bash
python3 agent_01.py
```

Walk through the script top to bottom:

```python
from agents import Agent, Runner
```
The SDK exposes two core classes. `Agent` describes *what* the agent is; `Runner` *executes* it.

```python
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)
```
An agent is just configuration: a name and a system prompt (`instructions`). Nothing is sent to OpenAI yet. Tools, handoffs, guardrails and `output_type` are added to this same constructor in later steps.

```python
async def main():
    result = await Runner.run(agent, "Write a haiku about recursion.")
    print(result.final_output)
```
`Runner.run(agent, input)` sends the input to the model together with the agent's instructions and returns a `RunResult`. It is a coroutine, so it must be awaited inside an `async def`. `final_output` is the agent's answer, a plain string here because no `output_type` was set on the agent.

```python
asyncio.run(main())
```
Starts the event loop and runs `main()`. Every async Python program needs this one entry point.

**What to observe:**
- The agent definition and the agent execution are separate. You can call `Runner.run` on the same `agent` object as many times as you like.
- Because `Runner.run` is async, several runs can be awaited concurrently with `asyncio.gather(...)`; Step 8 relies on the async API for its pipeline.
- If you prefer a blocking call for a quick script, `Runner.run_sync(agent, "...")` does the same thing without `async`/`await`.

### Step 2: Multi-agent language handoff (`agent_02.py`)

A triage agent receives user input and hands off to either a Spanish or English agent based on the detected language. The SDK models handoffs as tools: the triage agent "calls" the target agent as if it were a function.

```bash
python3 agent_02.py
```

**What to observe:**
- The `handoffs` parameter accepts a list of Agent objects. Each becomes available as a tool the triage agent can call.
- The `result` object shows which agents were invoked and in what order.
- Try changing the input to English and observe which agent the triage routes to.

### Step 3: Agent with a function tool (`agent_03.py`)

Attaches a `get_weather` tool to an agent via the `@function_tool` decorator. The decorator infers the tool's JSON schema from the function's type hints and docstring.

```bash
python3 agent_03.py
```

**What to observe:**
- Compare with lab050's manual JSON schema approach and lab054's LangChain `@tool` decorator. The Agent SDK's `@function_tool` is the most concise: type hints are enough.
- The tool runs locally. The SDK handles the tool-call loop: model requests tool, code executes it, result goes back, model answers.

### Guardrails: screening agent inputs and outputs

Steps 4 and 5 introduce guardrails, a mechanism built into the Agent SDK for filtering what goes into and comes out of an agent. Without guardrails, the agent will happily answer any question and return any content the model generates, including content you would rather not expose to the user (shell commands, credentials, harmful instructions).

The SDK supports two guardrail types:

- **Input guardrails** run before the main agent processes the request. If the input is flagged, the agent never executes, saving tokens and preventing the model from reasoning about dangerous content in the first place.
- **Output guardrails** run after the agent produces a response but before it reaches the caller. If the output is flagged, the SDK raises an exception and the response is suppressed.

Both types follow the same pattern: a small "guardrail agent" acts as a classifier (returning a boolean verdict), and a decorated function (`@input_guardrail` or `@output_guardrail`) wires the classifier into the pipeline. When the tripwire fires, the SDK raises `InputGuardrailTripwireTriggered` or `OutputGuardrailTripwireTriggered`, which your code can catch and handle.

This is not a silver bullet. The guardrail agents are themselves LLMs, so they can be fooled by adversarial input. In production, you would combine LLM-based guardrails with deterministic checks (regex blocklists, allow-listed tool names, rate limits).

### Step 4: Output guardrail (`agent_04.py`)

A secondary "guardrail agent" inspects the main agent's output and flags dangerous OS commands. If the tripwire fires, the SDK raises `OutputGuardrailTripwireTriggered` before the response reaches the user.

```bash
python3 agent_04.py
```

**What to observe:**
- The guardrail itself is an agent with `output_type=SecurityCheck` (a Pydantic model with `is_dangerous: bool`). This is a pattern: using a small, cheap agent as a classifier.
- The `@output_guardrail` decorator wraps the check function. It receives the main agent's output and returns a `GuardrailFunctionOutput`.
- The first test case ("Tell me a joke") passes; the second ("rm -rf /*") gets blocked.

### Step 5: Input and output guardrails combined (`agent_05.py`)

Extends Step 4 by adding an `@input_guardrail` that screens the user's question before the main agent runs. Now both ends of the pipeline are protected.

```bash
python3 agent_05.py
```

**What to observe:**
- Input guardrails fire before the agent processes the request. If the input is flagged, the main agent never runs, saving tokens.
- The third test case ("What's the command to clean up temporary files in Linux?") is borderline: it may pass the input guardrail but get caught by the output guardrail if the agent includes `rm` in its response. Try it and see.
- Two distinct exception types let you handle input blocks and output blocks differently.

### Step 6: Responses API for security analysis (`agent_06.py`)

Switches from the Agent SDK to the raw OpenAI Responses API (`client.responses.create`). This is a direct API call with no agent abstraction: you pass instructions and input, and get back a response.

```bash
python3 agent_06.py
```

The input is `data/docker-curl-https.txt`, a sysdig capture of `curl -L http://www.radarhack.com` running inside a Docker container.

**What to observe:**
- No `Agent`, no `Runner`, just `client.responses.create`. Compare the boilerplate with Steps 1-5.
- The `instructions` parameter is the system prompt equivalent. The `input` parameter is the user content.
- The Responses API stores the response server-side (see `response.id`). You can retrieve it later with `client.responses.retrieve()`.

### Step 7: Agent SDK with JSON output (`agent_07.py`)

Same security analysis as Step 6 but implemented with the Agent SDK. The agent's instructions request structured JSON output with line-number references into the sysdig trace.

```bash
python3 agent_07.py
```

**What to observe:**
- Compare the code structure with Step 6: the Agent SDK version defines the agent declaratively and lets Runner handle the API call.
- The `model` parameter on the Agent overrides the default. Here we use `gpt-4o-mini` for cost efficiency on a large input.
- The JSON extraction logic (`find("{")` / `rfind("}")`) is a pragmatic workaround; in production you would use `output_type` with a Pydantic model for guaranteed structure.

### Step 8: Multi-agent pipeline (`agent_08.py`)

Three agents run sequentially, each consuming the previous agent's output:

1. **Analyzer:** detailed sysdig trace analysis with line-number references
2. **Summary Generator:** converts the analysis into a markdown report (`summary.md`)
3. **JSON Formatter:** structures the analysis as machine-readable JSON (`details.json`)

```bash
python3 agent_08.py
```

**What to observe:**
- This is a pipeline, not a handoff: each agent is called explicitly with `Runner.run`, and the previous agent's `final_output` is passed as input to the next.
- The pipeline generates two files: `summary.md` (human-readable) and `details.json` (machine-readable). Check both after the run.
- Compare with the handoff pattern in Step 2. Handoffs let the model decide the routing; pipelines give you explicit control.
- Think about failure modes: what happens if the analyzer agent produces a poor analysis? The downstream agents will propagate (and possibly amplify) the error.

### Step 9: Tool guardrails (`agent_09.py`)

Steps 4 and 5 screened the *text* going into and out of the agent. Tool guardrails screen the *tool calls* in between. This matters for security: blocking `rm -rf` in the final answer is cosmetic, blocking the tool call that would actually run it is a real control.

The script gives an "Ops Bot" a single `run_command` tool. The tool does not touch your machine: it looks the command up in a small dictionary (`FAKE_SERVER`) and returns a canned answer. Two guardrails are attached to it:

```python
@tool_input_guardrail
def block_dangerous_commands(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    args = json.loads(data.context.tool_arguments)
    command = args.get("command", "")
    for word in BLOCKED_WORDS:
        if word in command.split():
            return ToolGuardrailFunctionOutput.reject_content(f"... blocked ...")
    return ToolGuardrailFunctionOutput.allow()
```
Runs **before** the tool executes. `data.context.tool_arguments` is the JSON string the model produced, so you can inspect the actual arguments, not just the tool name.

```python
@tool_output_guardrail
def hide_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    if "sk-" in str(data.output):
        return ToolGuardrailFunctionOutput.reject_content("... withheld ...")
    return ToolGuardrailFunctionOutput.allow()
```
Runs **after** the tool executes. `data.output` is the tool's return value, seen before the model sees it.

```python
@function_tool(
    tool_input_guardrails=[block_dangerous_commands],
    tool_output_guardrails=[hide_secrets],
)
def run_command(command: str) -> str:
    ...
```
Guardrails are attached per tool, not per agent. A different tool on the same agent can have different guardrails or none.

```bash
python3 agent_09.py
```

Three questions are asked: a harmless one (`uptime`), one that makes the model call `rm -rf` (stopped by the input guardrail), and one that reads a config file containing an API key (the tool runs, but the output guardrail withholds the result).

**What to observe:**
- `reject_content(msg)` does **not** raise an exception. The run continues and `msg` is handed to the model as if it were the tool result, so the model explains the refusal to the user. Compare with Steps 4 and 5, where a tripwire aborts the run. Use `ToolGuardrailFunctionOutput.raise_exception()` if you want the hard stop instead (it raises `ToolInputGuardrailTripwireTriggered` / `ToolOutputGuardrailTripwireTriggered`).
- These guardrails are plain Python, no LLM involved: deterministic, cheap, and not vulnerable to prompt injection. The LLM guardrails from Steps 4 and 5 and the deterministic tool guardrails here are complementary layers.
- Tool guardrails are different from a tool allowlist. An allowlist decides which tools the model is shown at all; a tool guardrail decides how an allowed tool may be used (which arguments, which results).
- If the model refuses the `rm -rf` request on its own, the guardrail never fires. That is fine: the guardrail is the safety net for the case where the model does not refuse.

## Cleanup environment

```bash
deactivate
./lab_cleanup.sh
```

Remove the generated analysis files if you no longer need them:

```bash
rm -f summary.md details.json
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
