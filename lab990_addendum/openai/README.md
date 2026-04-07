# OpenAI SDK Addendum: Extended Examples

Three standalone demos that build on concepts from the main labs. Each one uses a different part of the OpenAI platform:

| File | API | Related lab | What it demonstrates |
|------|-----|-------------|---------------------|
| [fireside_chat_with_kubernetes.py](./fireside_chat_with_kubernetes.py) | Chat Completions + tools | [lab050](../../lab050_OpenAI_Tools/) | Interactive kubectl agent with audit logging |
| [sec_agent.py](./sec_agent.py) | OpenAI Agent SDK (`openai-agents`) | [lab060](../../lab060_OpenAI_Agents/) | Multi-agent handoffs: triage, red team, blue team, compliance |
| [Response_Context.ipynb](./Response_Context.ipynb) | Responses API | [lab032](../../lab032_PythonFrameworks/) | Server-side conversation threading with `previous_response_id` |

## Prerequisites

Each script needs its own dependencies. Run inside the virtual environment of the related lab.

**fireside_chat_with_kubernetes.py** (uses lab050 venv):

```bash
cd ../../lab050_OpenAI_Tools
source .lab050/bin/activate
cd ../lab990_addendum/openai
```

You also need `kubectl` configured and pointing at a running cluster.

**sec_agent.py** (uses lab060 venv):

```bash
cd ../../lab060_OpenAI_Agents
source .lab060/bin/activate
cd ../lab990_addendum/openai
```

**Response_Context.ipynb** (Google Colab):

Open the notebook in Google Colab. It reads the API key from Colab's `userdata` store. No local venv needed.

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
```

## Walkthrough

### 1. Kubernetes assistant (`fireside_chat_with_kubernetes.py`)

An interactive chat loop that turns natural-language questions into kubectl commands. The model picks from four tools: `get_kubernetes_pods`, `get_pod_logs`, `describe_pod`, and a catch-all `execute_kubectl_command` that requires manual confirmation before running.

```bash
python3 fireside_chat_with_kubernetes.py
```

The script creates an audit log under `kubectl_audit_logs/` with every command executed, including whether the user approved or denied it.

**What to observe:**

- The model handles parallel tool calls when a single question requires multiple kubectl commands.
- The `execute_kubectl_command` tool includes a human-in-the-loop confirmation step. Compare this with the blind execution pattern in lab050's OA_02.py exercise: here the catch-all tool asks before running, but the three specific tools (get pods, logs, describe) execute without confirmation. Is that distinction safe?
- Check the audit log after a session. Every kubectl invocation is recorded with timestamp, user, command, and success/failure status.

**Security note:** This script executes real shell commands via `subprocess`. In a production setting, you would restrict which kubectl verbs and namespaces the tool can access, validate arguments against an allowlist, and run the agent with a least-privilege kubeconfig. The current version trusts whatever the model decides to run.

### 2. Security triage agent (`sec_agent.py`)

A multi-agent system built on the OpenAI Agent SDK. A triage agent inspects the user's request and hands off to one of four specialists:

- **Red Team Planner:** safe recon plans, nmap commands, HTTP fingerprinting
- **Blue Team Remediator:** patching, hardening, SIEM detections
- **Compliance Mapper:** OWASP ASVS, CIS Benchmarks, ISO 27001 control mapping
- **File Reader:** reads a local file and analyzes its contents

```bash
python3 sec_agent.py
```

The script runs four canned examples (one per specialist) and prints each result. Example 4 tries to read `result.json` from the current directory; create a sample file to see the file reader in action:

```bash
echo '{"scan": "nmap", "hosts_up": 3, "open_ports": [22, 80, 443]}' > result.json
python3 sec_agent.py
```

**What to observe:**

- The `handoffs` parameter on the triage agent controls which specialists it can delegate to. The triage agent itself has no tools; it only routes.
- Each specialist has a structured output format defined in its `instructions`. The Agent SDK enforces the handoff at the framework level, not through prompt engineering alone.
- The `@function_tool` decorator turns a plain Python function into a tool the agent can call. Compare this with the manual JSON schema approach in lab050.

### 3. Responses API with conversation threading (`Response_Context.ipynb`)

A Colab notebook that demonstrates the OpenAI Responses API, which is distinct from the Chat Completions API. The key difference: conversation history is stored server-side. Instead of resending all previous messages on every request, you pass `previous_response_id` and the server reconstructs the thread.

The notebook walks through three chained responses (joke, explanation, summary) and uses `client.responses.retrieve()` to recall any stored response by its ID.

**What to observe:**

- The `input` parameter accepts either a plain string (first call) or a list of message objects (follow-up calls).
- `previous_response_id` chains responses without resending history. This reduces token usage on multi-turn conversations.
- `client.responses.retrieve(response_id)` returns the full response object, including token counts and model metadata. Useful for cost tracking and debugging.
- The `store=True` field in the response confirms that OpenAI stored this response for later retrieval. Consider the privacy implications: your conversation data lives on OpenAI's servers until explicitly deleted.

## Cleanup

When done, deactivate whichever venv you activated:

```bash
deactivate
```

Remove the kubectl audit logs if you no longer need them:

```bash
rm -rf kubectl_audit_logs/
rm -f result.json
```
