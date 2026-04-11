![A2A](https://img.shields.io/badge/A2A-green) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Gemini](https://img.shields.io/badge/Gemini-blue) ![Python](https://img.shields.io/badge/Python-blue)

# LAB110: Agent-to-Agent Communication (A2A)

## Introduction

The A2A (Agent-to-Agent) protocol enables autonomous AI agents to discover, communicate, and collaborate across vendor boundaries. No shared SDK, runtime, or model is required. Agents publish an **agent card** at a well-known endpoint, and any compliant client can discover and invoke them.

This lab has two parts:

- **Part 1** uses the official `a2a-samples` hello world to introduce the protocol basics: agent cards, discovery, message exchange, and the A2A Inspector.
- **Part 2** demonstrates real cross-vendor interoperability: a Microsoft Agent Framework client (OpenAI) discovers and invokes a Google ADK server (Gemini) via A2A, with a multi-turn bidirectional conversation.

```
A2A Protocol Overview

  Agent A                                        Agent B
  ┌──────────────┐                              ┌──────────────┐
  │ Any framework │  ── discover ──────────────> │ agent-card   │
  │ Any model     │  <── card JSON ──────────── │ .json        │
  │               │                              │              │
  │               │  ── tasks/send ────────────> │ Any framework│
  │               │  <── result ─────────────── │ Any model    │
  └──────────────┘                              └──────────────┘
       HTTP + JSON-RPC                              HTTP + JSON-RPC
```

## Set up your environment

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## Part 1: A2A Hello World

This part uses the official a2a-samples repository to introduce the protocol fundamentals.

### Step 1: Setup Hello World Agent (Terminal 1)

```bash
git clone https://github.com/a2aproject/a2a-samples.git
cd a2a-samples/samples/python/agents/helloworld
uv run .
```

This starts a simple A2A agent that listens for incoming messages and exposes an agent card for discovery.

### Step 2: Setup Hello World Client (Terminal 2)

```bash
cd a2a-samples/samples/python/agents/helloworld
uv run test_client.py
```

This demonstrates basic agent discovery, message exchange, and response handling.

### Step 3: Agent Discovery

Query the agent's self-description using the standard discovery endpoint:

```bash
curl http://127.0.0.1:9999/.well-known/agent-card.json | jq -r .
```

The agent card contains: agent metadata, available skills, supported input/output modes, and the service URL.

## Part 2: Cross-Vendor Interoperability (Microsoft + Google)

This part demonstrates a Microsoft Agent Framework client (OpenAI) communicating with a Google ADK server (Gemini) via A2A. Neither side knows what framework or model the other uses.

```
┌──────────────────────────────────────────┐
│  Microsoft Agent Framework (Python)      │
│                                          │
│  ChatAgent (OpenAI)                      │
│    └── A2AAgent (remote tool) ─────────┐ │
│                                         │ │
└─────────────────────────────────────────┼─┘
                                          │  A2A (HTTP + Agent Card)
┌─────────────────────────────────────────┼─┐
│  Google ADK                             │ │
│                                         │ │
│  A2A API Server                         │ │
│    └── check_prime_agent               ◄┘ │
│        (Gemini + tool)                    │
│        agent-card.json                    │
└───────────────────────────────────────────┘
```

| File | What it does |
|------|-------------|
| `adk_server/setup.sh` | Setup the ADK server virtual environment |
| `adk_server/remote_a2a/check_prime_agent/agent.py` | ADK agent: prime number checker (Gemini) |
| `MicrosoftAgentFramework/ms_client/setup.sh` | Setup the MS client virtual environment |
| `MicrosoftAgentFramework/ms_client/demo.py` | Single-shot demo: "Is 97 prime?" |
| `MicrosoftAgentFramework/ms_client/demo_conversation.py` | Multi-turn bidirectional conversation |
| `MicrosoftAgentFramework/test.py` | Quick agent card connectivity check |
| `test_agent_cards.sh` | Curl-based agent card verification (5 tests) |

### Step 5: Setup the ADK Server (Terminal 1)

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

### Step 6: Verify the Agent Card

From a separate terminal:

```bash
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json | python3 -m json.tool
```

Or run the full verification suite:

```bash
./test_agent_cards.sh
```

This runs 5 checks: server reachability, card retrieval, field validation, skills inspection, and a test A2A task via JSON-RPC.

### Step 7: Setup the Microsoft Agent Framework Client (Terminal 2)

```bash
cd MicrosoftAgentFramework/ms_client
./setup.sh
source .venv/bin/activate
```

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_CHAT_MODEL_ID="gpt-4o-mini"
```

### Step 8: Single-Shot Demo

```bash
python demo.py
```

The MS agent discovers the ADK agent via its agent card, wraps it as an `A2AAgent` tool, and asks "Is 97 prime?" The request crosses the A2A boundary: OpenAI reasons about the question, calls the remote Gemini agent, and returns the result.

### Step 9: Multi-Turn Bidirectional Conversation

```bash
python demo_conversation.py
```

A 4-turn conversation where the MS agent calls the ADK agent multiple times, building on previous results:

| Turn | What happens | A2A calls |
|------|-------------|-----------|
| 1 | Check primes 101-110 | prime_checker with 10 numbers |
| 2 | Check twin prime pairs from turn 1 results | prime_checker based on previous output |
| 3 | Check Mersenne candidates (3, 7, 31, 127, 2047, 8191) | prime_checker with 6 numbers |
| 4 | Synthesize all results across turns | No A2A call; agent summarizes from memory |

```
  Turn 1: User --> MS Agent (OpenAI) --[A2A]--> ADK Agent (Gemini) --> check_prime
  Turn 2: User --> MS Agent (OpenAI) --[A2A]--> ADK Agent (Gemini) --> check_prime
  Turn 3: User --> MS Agent (OpenAI) --[A2A]--> ADK Agent (Gemini) --> check_prime
  Turn 4: User --> MS Agent (OpenAI) --> synthesize (no A2A call)
```

Each `prime_checker` call crosses the A2A protocol boundary. The MS agent maintains conversational context across turns and builds on previous results. Two different LLM vendors collaborate seamlessly.

## Key Concepts

**Agent Cards** are the foundation of A2A. Each agent publishes a JSON document at `/.well-known/agent-card.json` describing its name, capabilities, skills, and URL. Any compliant client can discover and invoke the agent without prior configuration.

**Service Discovery** follows a standard pattern: resolve the agent's base URL, fetch the card, parse the skills, and wrap the agent as a callable tool or direct A2A endpoint.

**A2A Tasks** use JSON-RPC over HTTP. A client sends `tasks/send` with a message, and the server responds with the agent's output. Tasks can be single-turn or multi-turn.

## Common Pitfalls

**Missing Gemini/Vertex credentials:** If you see `ValueError: Missing key inputs argument!`, configure authentication for the ADK server (Step 5).

**Python 3.14 dependency conflicts:** Don't install the full `agent-framework` meta-package on Python 3.14. Install only the required sub-packages (`core`, `a2a`), as the setup script does.

**ADK server not running:** If the demo hangs or errors with connection refused, make sure the ADK server is running in Terminal 1.

## Cleanup environment

```bash
deactivate
```

To remove virtual environments:

```bash
rm -rf adk_server/.venv MicrosoftAgentFramework/ms_client/.venv
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
