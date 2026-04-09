![Google](https://img.shields.io/badge/Google-green) ![ADK](https://img.shields.io/badge/ADK-brightgreen) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB061: Google Agent Development Kit (ADK)

## Introduction

Google's Agent Development Kit (ADK) is a framework for building agents powered by Gemini models. An ADK agent is a Python module that defines a `root_agent` with a model, instructions, and optional tools. The `adk` CLI discovers agents automatically and serves them through a web UI and a REST API.

This lab contains two security-focused agents that demonstrate different agentic patterns, plus a standalone script that runs an agent programmatically without the `adk` CLI.

| Directory | Agent | Pattern | Model |
|-----------|-------|---------|-------|
| `adk/llm_red_team_agent/` | AI safety red team | 3 sub-agents as tools (attack, target, evaluate) | gemini-2.0-flash |
| `adk/cyber_guardian/` | Incident response | Orchestrator with 6 direct tool functions | gemini-2.0-flash |
| `adk_standalone/cyber_guardian/` | Incident response (standalone) | Runner API without `adk` CLI | gemini-2.0-flash |

## Set up your environment

```bash
export GOOGLE_API_KEY="your-google-api-key"
```

```bash
./lab_setup.sh
source .lab061/bin/activate
```

### API key

Get a **Google API Key** from [Google AI Studio](https://aistudio.google.com/). Click "Get API Key" and create a new key. Google AI Studio offers free quotas for Gemini models.

### Environment file

Create `adk/.env` with your credentials:

```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here
```

Never commit this file to version control.

## Lab instructions

### Step 1: LLM Red Team agent (`adk/llm_red_team_agent/`)

An automated adversarial testing pipeline with three sub-agents working as tools. The orchestrator chains them in sequence: generate attack, simulate target response, evaluate.

```bash
cd adk
adk web
```

Open `http://localhost:8000`, select **security_orchestrator** from the agent picker, and ask:

> "Test the target for Prompt Injection vulnerabilities."

Or try other risk categories: "PII Leakage", "Financial Advice", "AML", "Toxicity".

**What to observe:**

- The pipeline has three stages, each running a separate sub-agent: a Red Team agent (temperature 0.9, creative attacks), a Target banking chatbot (temperature 0.1, strict safety rules), and an Evaluator (temperature 0.0, deterministic JSON verdict).
- Each sub-agent runs in an isolated session via `ThreadPoolExecutor` to prevent context leakage between attacker and target. This mimics a real-world stateless API call.
- The safety constitution in `safety_rules.py` defines the rules the target must follow. The evaluator grades against these same rules. Try modifying the constitution and observe how the verdicts change.
- The orchestrator uses temperature 0.0 for reliable tool chaining. Compare with the red team agent's 0.9 for creative diversity.
- Retry logic (`tenacity`) handles 429 rate limits automatically.
- Read `config.py` to see how different models can be assigned to different roles. In production, you might use a stronger model for evaluation and a cheaper one for the target.

Based on [google/adk-samples/ai-security-agent](https://github.com/google/adk-samples/tree/main/python/agents/ai-security-agent) (Apache 2.0).

### Step 2: Cyber Guardian (`adk/cyber_guardian/`)

An incident response orchestrator with 6 tool functions covering the full IR workflow: triage, threat intel enrichment, investigation, playbook lookup, action execution, and incident creation.

Select **cyber_guardian_orchestrator** in the web UI and paste this alert:

> "ALERT: IOC_MATCH detected on host srv-web-prod-01 by user svc-apache. Outbound connection to 185.220.101.42:443 flagged by network IDS. Process: certutil.exe downloading from 185.220.101.42."

**What to observe:**

- The orchestrator has 6 tools representing the stages of incident response. It chains them based on alert classification (IOC_MATCH vs EDR_DETECTION) following the workflow in its instruction.
- The mock tools in `tools.py` return realistic incident data: Cobalt Strike C2 beacons, certutil abuse for payload download, encoded PowerShell commands, and lateral movement indicators. In production, these would query BigQuery, a SIEM, or a SOAR platform.
- The response playbook flags actions that `RequiresApproval: true` (e.g., host isolation, credential reset), demonstrating the Human-In-The-Loop (HITL) pattern for high-impact actions. Actions that don't need approval (block-ip, collect-forensics) are executed automatically.
- Try submitting the same alert twice. The triage tool should detect the duplicate and stop processing.
- Compare the agent instruction (workflow steps) with how the model actually chains the tools. The model decides the sequence; it is not hardcoded.

Based on [google/adk-samples/cyber-guardian-agent](https://github.com/google/adk-samples/tree/main/python/agents/cyber-guardian-agent) (Apache 2.0).

### Step 3: Standalone Cyber Guardian (`adk_standalone/cyber_guardian/`)

Same incident response pipeline as Step 2, but running from the command line without `adk web`. Everything is in a single file: mock tools, agent definition, and the Runner loop.

```bash
cd ../adk_standalone/cyber_guardian
python3 agent.py
```

The script ships with a sample IOC_MATCH alert (Cobalt Strike C2 via certutil on srv-web-prod-01). You can override it with the `ALERT_TEXT` environment variable:

```bash
ALERT_TEXT="ALERT: EDR_DETECTION on ws-dev-042. Process tree: w3wp.exe -> powershell.exe -> cmd.exe. Suspicious encoded command detected." python3 agent.py
```

**What to observe:**

- The Runner API gives you programmatic control: create sessions, inject messages, and process events in a loop.
- `runner.run_async` yields events with `content.parts` (text or function calls). This is the Gemini content format (`google.genai.types`).
- Compare with `adk web`: the CLI handles all the session management for you, but you lose control over the conversation flow.
- The standalone version lets you inject follow-up messages, branch on tool results, or feed the output into another system.
- No external dependencies needed beyond `google-adk` and `python-dotenv`.
- If you hit a 429 RESOURCE_EXHAUSTED error, wait a minute. The free Google AI Studio tier has per-minute rate limits that reset quickly.

### API server

`adk web` also starts a REST API on the same port. Open `http://localhost:8000/docs` for the Swagger UI.

You can interact with agents via curl:

```bash
# Create a session
curl -X POST http://localhost:8000/apps/cyber_guardian/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"name": "demo"}}'

# Send a message
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "cyber_guardian",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [{"text": "ALERT: IOC_MATCH on srv-web-prod-01. Outbound to 185.220.101.42:443."}]
    }
  }'
```

This is useful for integrating ADK agents into other systems, testing from CI, or building custom frontends.

## ADK agent structure

Every agent directory follows the same convention:

```
agent_name/
  __init__.py     # from . import agent
  agent.py        # defines root_agent at module level
```

`adk web` scans subdirectories for modules that export a `root_agent`. See `adk/instructions.md` for a template when creating your own agents.

## Resources

- [Google ADK documentation](https://google.github.io/adk-docs/)
- [ADK quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [ADK sample agents](https://github.com/google/adk-samples)
- [ADK Python source](https://github.com/google/adk-python)
- [Google AI Studio](https://aistudio.google.com/)

## Cleanup environment

```bash
deactivate
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
