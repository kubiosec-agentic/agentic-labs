![A2A](https://img.shields.io/badge/A2A-green) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Gemini](https://img.shields.io/badge/Gemini-blue) ![Python](https://img.shields.io/badge/Python-blue)

# A2A: Microsoft Agent Framework + Google ADK Interoperability

## Introduction

This demo shows two agents from different vendors communicating via the Agent-to-Agent (A2A) protocol. A Microsoft Agent Framework client (backed by OpenAI) discovers and invokes a Google ADK server (backed by Gemini) without shared SDKs, runtimes, or models.

```
┌─────────────────────────────────────────┐
│  Microsoft Agent Framework (Python)     │
│                                         │
│  ChatAgent (OpenAI)                     │
│    └── A2AAgent (remote tool) ────────┐ │
│                                        │ │
└────────────────────────────────────────┼─┘
                                         │  A2A (HTTP + Agent Card)
┌────────────────────────────────────────┼─┐
│  Google ADK                            │ │
│                                        │ │
│  A2A API Server                        │ │
│    └── check_prime_agent              ◄┘ │
│        (Gemini + tool)                   │
│        agent-card.json                   │
└──────────────────────────────────────────┘
```

The ADK agent acts as an A2A server, the Microsoft agent consumes it as a remote tool. Communication happens via HTTP and agent card discovery. The two sides are fully decoupled.

## Repository Structure

```
a2a/
├── adk_server/
│   ├── setup.sh                         # Setup script
│   └── remote_a2a/
│       └── check_prime_agent/
│           ├── agent.py                 # ADK agent (Gemini + check_prime tool)
│           ├── agent.json               # Agent metadata
│           ├── agent-card.json          # A2A discovery card
│           └── __init__.py
│
├── MicrosoftAgentFramework/
│   ├── ms_client/
│   │   ├── setup.sh                     # Setup script
│   │   ├── demo.py                      # Single-shot demo (is 97 prime?)
│   │   └── demo_conversation.py         # Multi-turn bidirectional demo
│   ├── test.py                          # Quick agent card connectivity check
│   └── README.md                        # This file
│
└── test_agent_cards.sh                  # Curl-based agent card verification
```

## Step 1: Setup the ADK Server (A2A Provider)

```bash
cd adk_server
./setup.sh
source .venv/bin/activate
```

Configure authentication (choose one):

```bash
# Option A: Gemini API (simplest)
export GOOGLE_API_KEY="your-gemini-api-key"

# Option B: Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="europe-west1"
gcloud auth application-default login
```

Start the A2A server:

```bash
adk api_server --a2a --port 8001 remote_a2a
```

## Step 2: Verify the Agent Card

From a separate terminal, test that the agent card is discoverable:

```bash
# Quick curl check
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json | python3 -m json.tool

# Full verification suite (checks fields, skills, and sends a test task)
cd a2a
./test_agent_cards.sh
```

Expected output from the curl test:

```json
{
    "name": "check_prime_agent",
    "description": "An agent specialized in checking whether numbers are prime.",
    "version": "1.0.0",
    "url": "http://localhost:8001/a2a/check_prime_agent",
    "skills": [
        {
            "id": "prime_checking",
            "name": "Prime Number Checking",
            "description": "Check if numbers in a list are prime",
            "tags": ["math", "prime", "numbers"]
        }
    ]
}
```

The `test_agent_cards.sh` script runs five checks: server reachability, card retrieval, field validation, skills inspection, and a test A2A task.

## Step 3: Setup the Microsoft Agent Framework Client

```bash
cd MicrosoftAgentFramework/ms_client
./setup.sh
source .venv/bin/activate
```

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_CHAT_MODEL_ID="gpt-4o-mini"
```

## Step 4: Run the Single-Shot Demo

```bash
python demo.py
```

This sends a single request ("Is 97 prime?") through the MS agent, which discovers the ADK agent via its agent card, wraps it as a tool, and calls it via A2A.

## Step 5: Run the Multi-Turn Conversation Demo

```bash
python demo_conversation.py
```

This demonstrates a **bidirectional multi-turn conversation** across the A2A boundary:

| Turn | What happens | A2A calls |
|------|-------------|-----------|
| 1 | MS agent asks ADK to check primes 101-110 | prime_checker called with 10 numbers |
| 2 | Follow-up: check twin prime pairs from results | prime_checker called based on turn 1 results |
| 3 | Check Mersenne candidates (3, 7, 31, 127, 2047, 8191) | prime_checker called with 6 numbers |
| 4 | Synthesize all results across turns | No tool call; agent summarizes from memory |

Each `prime_checker` call crosses the A2A protocol boundary: the MS agent (OpenAI) sends an HTTP request to the ADK agent (Gemini), which runs the `check_prime` tool and returns the result. The MS agent maintains conversational context across turns and builds on previous results.

```
   Turn 1: User --> MS Agent (OpenAI) --[A2A]--> ADK Agent (Gemini) --> check_prime([101..110])
   Turn 2: User --> MS Agent (OpenAI) --[A2A]--> ADK Agent (Gemini) --> check_prime(twin pairs)
   Turn 3: User --> MS Agent (OpenAI) --[A2A]--> ADK Agent (Gemini) --> check_prime(Mersenne)
   Turn 4: User --> MS Agent (OpenAI) --> synthesize (no A2A call needed)
```

## Quick Connectivity Test

Before running the demos, you can verify agent card connectivity:

```bash
cd MicrosoftAgentFramework
python test.py
```

Expected output:

```
Agent: check_prime_agent
Description: An agent specialized in checking whether numbers are prime.
Skills: ['Prime Number Checking']
Agent card OK.
```

## What This Proves

The Microsoft agent can discover an external agent via an agent card, wrap it as an `A2AAgent`, and expose it as a tool to an OpenAI-backed `ChatAgent`. The Google ADK agent acts as a fully compliant A2A server, serves metadata, and executes logic on behalf of remote agents. No shared SDK, runtime, or model is required.

## Common Pitfalls

**Missing Gemini/Vertex credentials:** If you see `ValueError: Missing key inputs argument!`, configure authentication for the ADK server (Step 1).

**Python 3.14 dependency conflicts:** Don't install the full `agent-framework` meta-package on Python 3.14. Install only the required sub-packages (`core`, `a2a`), as the setup script does.

**ADK server not running:** If `demo.py` hangs or errors with a connection refused, make sure the ADK server is running in another terminal (Step 1).

## Next Steps

Ideas to extend this demo:

Replace the prime checker with a CVE lookup agent, a Kubernetes manifest linter, or a policy evaluation agent. Add mTLS between agents, request signing, audit logging, or OpenTelemetry observability. Deploy both sides on Kubernetes.

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
