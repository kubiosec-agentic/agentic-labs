![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI_Agents_SDK-lightblue) ![MCP](https://img.shields.io/badge/MCP-purple) ![Skills](https://img.shields.io/badge/Skills-green) ![Security](https://img.shields.io/badge/Security-red) ![Python](https://img.shields.io/badge/Python-blue)

# LAB078: OpenAI Agents SDK, MCP and skills

## Introduction

In lab060 you drove the OpenAI Agents SDK, and in lab070 you built MCP
servers. This lab puts them together and adds a third idea: **skills**.

The Agents SDK has no built-in notion of a skill. A batteries-included harness
like `deepagents` (lab066) hides the machinery; here you build the same
progressive-disclosure skill pattern by hand, in about 30 lines, so you can
see every moving part. The point of the lab is how three things compose in one
agent:

- **MCP** provides the side-effecting capability (an `http_get` tool over a
  stdio MCP server the agent spawns).
- **A skill** is a folder with a `SKILL.md`. A simple skill is pure
  instructions; a powerful one also carries a script and a reference file.
- **The agent** orchestrates them by reading the skill and following it:
  fetch with MCP, compute with the script, explain with the reference, report.

The theme is security, so the powerful skill audits a site's HTTP security
headers.

| Exercise | Adds | File |
|---|---|---|
| 1 | Agents SDK agent + stdio MCP server | `agent_01_mcp.py` |
| 2 | A simple skill (instructions only) | `agent_02_simple_skill.py` |
| 3 | A powerful skill (SKILL.md + script + reference) | `agent_03_power_skill.py` |

## Set up your environment

```bash
export OPENAI_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab078/bin/activate
```

Sanity check:

```bash
python3 -c "from importlib.metadata import version as v; print('openai-agents', v('openai-agents'), '| fastmcp', v('fastmcp'))"
```

Written against `openai-agents` 0.22.x and `fastmcp` 4.x. The model defaults to
`gpt-4o-mini`; override with `DA_MODEL` (the same knob as the other labs). All
OpenAI traffic is plain HTTPS, so lab050's mitmproxy setup works here too. The
SDK's telemetry tracing is disabled in `common.py` so a run makes no surprise
network calls beyond the model and the fetch.

You do not start the MCP server yourself. The agent spawns `mcp_server.py` over
stdio via `MCPServerStdio`. To poke the server by hand, run
`python3 mcp_server.py` and send it MCP JSON-RPC on stdin (Ctrl+D to exit).

## Lab instructions

### 1. Agent + MCP over stdio (`agent_01_mcp.py`)

```bash
python3 agent_01_mcp.py
```

`MCPServerStdio(params={"command": python, "args": ["mcp_server.py"]})` spawns
the server as a subprocess and speaks MCP over stdio. Before the agent runs,
the script calls `list_tools()` (this needs no API key) and prints:

```
MCP tools discovered: ['add', 'http_get']
```

Then the agent adds `21 + 21` with the `add` tool and fetches
`https://example.com` with `http_get`, reporting the status code and
Content-Type. Watch that both tool calls are served by the MCP subprocess, not
by code in `agent_01_mcp.py`.

Things to notice in the code:

- The server object is an async context manager: `async with MCPServerStdio(...) as server:`. It connects on enter and cleans up the subprocess on exit.
- `params` is a dict (a TypedDict), not keyword arguments. `command` + `args` is a command and an argument list, not a Python module path.
- `Agent(mcp_servers=[server])` merges the server's tools into the agent's tool set.

### 2. A simple skill: instructions only (`agent_02_simple_skill.py`)

```bash
python3 agent_02_simple_skill.py
```

A skill does not have to be code. `skills/incident-note/SKILL.md` is front
matter (name, description) plus a procedure for formatting a finding as
Title / Severity / Evidence / Impact / Recommendation.

`skills_runtime.py` is the whole "skills runtime", and it is worth reading:

- `build_instructions()` scans `skills/*/SKILL.md` and injects only each
  skill's name and description into the system prompt. The model sees the menu,
  not the cookbook. That is progressive disclosure, level one.
- `read_skill(dir)` is a function tool that returns the full `SKILL.md` body,
  pulled only when a task matches. Level two.

Ask the agent to record a finding and it should call
`read_skill('incident-note')` first, then emit the exact fields the skill
specifies rather than a freeform paragraph. Compare with lab066, where
`deepagents` did all of this for you: here it is thirty lines you can read.

### 3. A powerful skill: SKILL.md + script + reference (`agent_03_power_skill.py`)

```bash
python3 agent_03_power_skill.py
python3 agent_03_power_skill.py https://github.com
```

`skills/http-header-audit/` is the interesting case. It composes all three
building blocks:

```
skills/http-header-audit/
  SKILL.md              the procedure: fetch, grade, explain, report
  audit_headers.py      the script: grades headers, deterministic and offline
  reference/grading.md  the knowledge: per-header rubric, read on demand
```

The division of labour is the lesson:

- **MCP `http_get(url)`** does the network fetch (the side effect).
- **`audit_headers.py`** grades the headers. It is a pure function of its
  input (headers as JSON on stdin), so it is deterministic and unit-tested.
  The agent runs it with `run_skill_script(...)`, level-three disclosure.
- **`reference/grading.md`** holds the per-header detail, read with
  `read_reference(...)` only when the agent needs to explain a header.

Expected tool sequence:

```
http_get (MCP)  ->  read_skill('http-header-audit')  ->
run_skill_script('audit_headers.py')  ->  read_reference('grading.md')  ->
read_skill('incident-note')
```

Four files, one agent: fetch, grade, explain, report. Swap the skill folder and
the same agent does a different job, without touching `agent_03_power_skill.py`.
That separation is the whole reason skills exist.

To see the grader on its own, feed it headers directly:

```bash
echo '{"Strict-Transport-Security":"max-age=0"}' | python3 skills/http-header-audit/audit_headers.py
```

## Security notes

This is a security course, so the sharp edges are deliberate.

`http_get` is an SSRF primitive. The agent will fetch whatever URL it is told
to, including `http://169.254.169.254/` (cloud metadata) or an internal
`10.x` address. A prompt injection that reaches this agent can turn it into a
request forwarder from inside your network. A real deployment allow-lists
destinations at the MCP tool; this lab leaves it open so you can see the
exposure. Try pointing it at an internal address and watch it comply.

`run_skill_script` executes code that a `SKILL.md` points at. If an attacker
can write to `skills/`, that is remote code execution, the same trust boundary
as lab066 Exercise 3, made explicit because you wrote the loader. `_safe()` in
`skills_runtime.py` keeps paths inside the skill folder; it is the minimum, not
a sandbox. Who can write to `skills/` is the question that matters, and on a
real system that is "anyone who can land a pull request".

Skills are instructions the model is built to obey, loaded by name from disk. A
poisoned `SKILL.md` (or a poisoned `reference/`) is prompt injection you asked
for. The same discipline from lab070's tool-description poisoning applies one
layer up.

## Cleanup environment

```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
