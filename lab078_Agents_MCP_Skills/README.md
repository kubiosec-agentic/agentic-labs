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
| 4 | The same skill, native: OpenAI upload (curl) and Anthropic SDK | `native/` |

The skill folders use the layout both vendors use natively, `SKILL.md` at the
root with `scripts/` and `references/` beside it, so the exact folder you build
in Exercises 1 to 3 is the one you upload in Exercise 4.

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

Written against `openai-agents` 0.22.x and `fastmcp` 4.x. The agent model
defaults to `gpt-4o-mini`; override with `OPENAI_AGENTS_MODEL`. (The native
examples in Exercise 4 use their own `OPENAI_SKILL_MODEL` /
`ANTHROPIC_SKILL_MODEL`.) All OpenAI traffic is plain HTTPS, so lab050's
mitmproxy setup works here too. The
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
  SKILL.md                     the procedure: fetch, grade, explain, report
  scripts/audit_headers.py     the script: grades headers, deterministic and offline
  references/grading.md        the knowledge: per-header rubric, read on demand
```

The division of labour is the lesson:

- **MCP `http_get(url)`** does the network fetch (the side effect).
- **`scripts/audit_headers.py`** grades the headers. It is a pure function of
  its input (headers as JSON on stdin), so it is deterministic and unit-tested.
  The agent runs it with `run_skill_script(...)`, level-three disclosure.
- **`references/grading.md`** holds the per-header detail, read with
  `read_reference(...)` only when the agent needs to explain a header.

Expected tool sequence:

```
http_get (MCP)  ->  read_skill('http-header-audit')  ->
run_skill_script('scripts/audit_headers.py')  ->  read_reference('grading.md')  ->
read_skill('incident-note')
```

Four files, one agent: fetch, grade, explain, report. Swap the skill folder and
the same agent does a different job, without touching `agent_03_power_skill.py`.
That separation is the whole reason skills exist.

**Same agent as Exercise 2, only the prompt differs.** `agent_02` and
`agent_03` are the same code: same skill loader, same tools, and both see both
skills on the menu at startup. What changed is the prompt. Exercise 2's prompt
is an incident-note task, so the model judges its way to the instruction-only
skill; Exercise 3's prompt is a header-audit task, so it opens the skill that
ships a script and a reference and runs the full sequence (and then chains into
incident-note for the write-up). The agent never decides to be "advanced"; the
prompt selects the skill, and the skill's contents decide how much happens. If
you gave `agent_02` the header-audit prompt, it would behave exactly like
`agent_03`.

To see the grader on its own, feed it headers directly:

```bash
echo '{"Strict-Transport-Security":"max-age=0"}' | python3 skills/http-header-audit/scripts/audit_headers.py
```

### 4. The same skill, native: OpenAI upload (curl) and Anthropic SDK (`native/`)

Exercises 1 to 3 ran the skill locally with a loader you wrote. Both OpenAI and
Anthropic now support skills natively, using the same `SKILL.md` folder format.
The difference that matters is where the scripts run, which is where the blast
radius lives.

| Where | How | Scripts run | You get |
|---|---|---|---|
| Local, DIY (this lab, ex. 1-3) | your loader + function tools | your machine | model-agnostic, portable, works offline |
| OpenAI Responses, uploaded | `POST /v1/skills`, then `skill_reference` | OpenAI's sandbox | managed, versioned, data leaves your box |
| OpenAI Responses, local shell | `shell` tool `type: local`, skill by path | your machine | native loop, but a remote model drives your shell |
| Anthropic Messages, uploaded | `client.skills.create`, then `container.skills` | Anthropic's sandbox | managed, versioned, data leaves your box |

The `openai-agents` SDK itself has no native skills, which is why Exercises 1 to
3 exist. Exercise 4 shows the two managed paths.

#### 4a. OpenAI, uploaded, with curl (`native/openai_uploaded_skill.sh`)

curl because this is the shape you script in CI or a Makefile. It uploads
`skills/http-header-audit/` (multipart, preserving the folder tree), reads back
the `skill_id`, then calls `/v1/responses` with the skill attached:

```
tools: [ { type: "shell", environment: {
  type: "container_auto",
  skills: [ { type: "skill_reference", skill_id: "<id>", version: "latest" } ]
} } ]
```

```bash
export OPENAI_API_KEY=...
export OPENAI_SKILL_MODEL=<a current model that supports the Responses shell tool>
./native/openai_uploaded_skill.sh          # upload + run, end to end
```

`openai_uploaded_skill.sh` builds the request body with `jq` so the header JSON
is escaped correctly. Once a skill is uploaded you usually want to run it again
without re-uploading, so `native/openai_run_skill.sh` is just the run half, as a
plain literal curl you can copy:

```bash
export SKILL_ID=skill_...     # from the upload step's output
./native/openai_run_skill.sh
```

which is this call (the skill is attached to the shell tool's environment; the
model reads it and runs its script in OpenAI's sandbox on the headers in
`input`):

```bash
curl -sS -L 'https://api.openai.com/v1/responses' \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "'"$OPENAI_SKILL_MODEL"'",
    "tools": [ { "type": "shell", "environment": {
      "type": "container_auto",
      "skills": [ { "type": "skill_reference", "skill_id": "'"$SKILL_ID"'" } ]
    } } ],
    "input": "Use the http-header-audit skill to grade these headers and give the letter grade: {\"Strict-Transport-Security\":\"max-age=0\",\"Server\":\"nginx/1.18.0\"}"
  }'
```

The `skill_reference` omits `version`, so the skill's `default_version` is used.
Passing `version: "latest"` was rejected by the live API ("Skill version '1'
not found"); to pin a version, use the integer, e.g. `"version": 1` (or
`SKILL_VERSION=1 ./native/openai_run_skill.sh`). A freshly uploaded version can
also take a second to become resolvable, which is why the upload script sleeps
briefly before the run.

The example model strings in the docs move, so the scripts read the model from
`OPENAI_SKILL_MODEL` rather than hardcoding one. Get a current value from the
[OpenAI skills guide](https://developers.openai.com/api/docs/guides/tools-skills).
Needs `jq` and skills access on your account.

#### 4b. Anthropic, uploaded, with the SDK (`native/anthropic_skill_example.py`)

Anthropic's skills mirror OpenAI's hosted mode. Upload the same folder with
`client.skills.create(files=files_from_dir(...))`, then reference it in a
Messages call alongside the code execution tool:

```python
container={"skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]},
tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
```

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
export ANTHROPIC_SKILL_MODEL=<a current model that supports code execution>
python3 native/anthropic_skill_example.py
```

The Skills API is GA (no beta header). For a built-in skill instead of an
upload, pass `{"type": "anthropic", "skill_id": "pptx", "version": "latest"}`
and skip the upload step. Model strings move here too; set
`ANTHROPIC_SKILL_MODEL` from the
[Anthropic skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

Both 4a and 4b hand the headers to the skill inline, so the sandbox needs no
network. In these managed modes the fetch would be a separate hosted tool, not
this lab's MCP server.

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
poisoned `SKILL.md` (or a poisoned `references/` file) is prompt injection you
asked for. The same discipline from lab070's tool-description poisoning applies
one layer up.

The native modes (Exercise 4) move the trust boundary but do not remove it. An
uploaded skill runs in the vendor's sandbox, so the RCE blast radius is theirs,
but the sandbox can still reach whatever it is allowed to (network, connected
tools) and your data still leaves your box. And versioning is a new attack
surface: an unpinned `version: "latest"` means whoever can push a new version
changes what every caller runs, silently. Pin versions in production, and treat
"who can publish a skill version" as the same class of question as "who can
merge to main". OpenAI's local-shell mode is the sharp one: a remote model
driving a shell on your own machine, which is the lab's local RCE lesson with a
vendor's model at the wheel.

## Cleanup environment

```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
