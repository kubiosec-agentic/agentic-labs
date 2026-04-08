![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Agents_SDK](https://img.shields.io/badge/Agents_SDK-brightgreen) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB060: OpenAI Agent SDK

## Introduction

The OpenAI Agent SDK (`openai-agents`) provides a lightweight framework for building multi-agent systems. Agents are defined with a name, instructions, optional tools, and optional handoffs to other agents. The SDK handles the tool-call loop, agent routing, and guardrail enforcement, so you can focus on the agent design rather than the plumbing.

This lab walks through eight examples that progress from a single synchronous agent to a multi-agent security analysis pipeline. Along the way you will see handoffs, function tools, input/output guardrails, and a side-by-side comparison of the raw Responses API versus the Agent SDK.

| Step | Script | What it demonstrates |
|------|--------|---------------------|
| 1 | `agent_01.py` | Minimal synchronous agent (Runner.run_sync) |
| 2 | `agent_02.py` | Multi-agent handoff based on language detection |
| 3 | `agent_03.py` | Agent with a @function_tool (weather lookup) |
| 4 | `agent_04.py` | Output guardrail: block dangerous OS commands |
| 5 | `agent_05.py` | Input + output guardrails combined |
| 6 | `agent_06.py` | Responses API: security trace analysis (raw client, no SDK) |
| 7 | `agent_07.py` | Agent SDK: same analysis with structured JSON output |
| 8 | `agent_08.py` | Multi-agent pipeline: analyzer, summary writer, JSON formatter |

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

### Step 1: Minimal synchronous agent (`agent_01.py`)

A single agent with no tools and no handoffs, executed via `Runner.run_sync`. This is the smallest possible Agent SDK program.

```bash
python3 agent_01.py
```

**What to observe:**
- `Runner.run_sync` is a convenience wrapper around the async `Runner.run`. Use it for scripts; use the async version in production.
- The `result.final_output` is a plain string because no `output_type` was specified on the agent.

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
