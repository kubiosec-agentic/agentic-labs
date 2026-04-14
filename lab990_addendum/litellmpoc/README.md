![LiteLLM](https://img.shields.io/badge/LiteLLM-proxy-orange) ![OpenAI](https://img.shields.io/badge/OpenAI-Agents_SDK-lightblue) ![MCP](https://img.shields.io/badge/MCP-purple) ![Docker](https://img.shields.io/badge/Docker-Compose-blue) ![Security](https://img.shields.io/badge/Guardrails-red)

# LAB990 Addendum: LiteLLM Proxy + OpenAI Agents SDK + MCP

## Introduction

This lab builds a three-layer AI agent stack and deploys it with Docker
Compose. The goal is to see what happens when you put a proxy between your
agent and the LLM provider: you get a single observability point for
every LLM call, provider-agnostic routing, and a place to bolt on
guardrails without touching the agent code.

The three layers are:

1. **LiteLLM Proxy** (port 4000) -- an OpenAI-compatible gateway that
   routes LLM calls, applies moderation guardrails, and logs every
   request with model, tokens, cost, and latency.
2. **Agent App** (port 8080) -- a FastAPI service built with the OpenAI
   Agents SDK. It talks to the proxy as if it were OpenAI, adds its own
   input guardrail, and connects to a remote MCP server for tool use.
3. **Microsoft Learn MCP Server** -- a remote MCP endpoint at
   `https://learn.microsoft.com/api/mcp` that gives the agent search
   and fetch tools over Microsoft documentation.

```
+-----------+         +------------------------------+
|  Client   |--HTTP-->|  Agent App        :8080      |
|  (curl)   |         |  +- OpenAI Agents SDK        |
+-----------+         |  +- Moderation guardrail     |
                      |  +- Custom trace logger      |
                      |  +- MCP client --------------+--> learn.microsoft.com/api/mcp
                      +--------------+---------------+
                                     | OpenAI-compat API
                      +--------------v---------------+
                      |  LiteLLM Proxy    :4000      |
                      |  +- OpenAI backend           |
                      |  +- Moderation guardrail     |
                      |  +- Custom callback logger   |
                      +------------------------------+
```

### What you will cover

1. Deploying a LiteLLM proxy as an OpenAI-compatible gateway.
2. Wiring an OpenAI Agents SDK app to talk through the proxy instead of
   directly to OpenAI.
3. Dual-layer content moderation: guardrails at both the proxy and the
   agent level using the OpenAI Moderation API.
4. MCP tool integration: the agent calls Microsoft Learn search tools
   via the MCP streamable-HTTP transport.
5. Structured observability: JSON logs from both layers capturing model,
   tokens, cost, latency, guardrail results, and MCP tool calls.
6. (Optional) Kubernetes deployment with ConfigMaps and Secrets.

## Prerequisites

- Docker and Docker Compose
- An OpenAI API key (`sk-proj-...`)

## Set up your environment

```bash
cd lab990_addendum/litellmpoc
```

```bash
cp .env.example .env
```

Edit `.env` and paste your OpenAI key:

```
OPENAI_API_KEY=sk-proj-your-key-here
LITELLM_MASTER_KEY=sk-master-1234
```

The master key is used by the agent to authenticate to the proxy. The
default (`sk-master-1234`) is fine for a local lab.


## Step 1 -- Build and start

```bash
docker compose up --build -d
```

This builds two images (`litellmpoc-litellm-proxy` and
`litellmpoc-agent-app`) and starts both containers. The agent container
waits for the proxy health check to pass before starting, so the first
boot takes about 30 seconds.

## Step 2 -- Verify both services are healthy

```bash
docker compose ps
```

Both containers should show `Up (healthy)` / `running`.

```bash
# Proxy health
curl -s http://localhost:4000/health/readiness | jq .status
```

```bash
# Agent health (shows proxy + MCP URLs)
curl -s http://localhost:8080/health | jq
```

## Step 3 -- Talk to the general agent (LLM only)

This sends a prompt through the agent to the proxy to OpenAI. No MCP
tools involved.

```bash
curl -s http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is eBPF and why does it matter for Kubernetes?",
    "agent_type": "general"
  }' | jq
```

## Step 4 -- Talk to the learning agent (LLM + MCP tools)

The agent uses Microsoft Learn MCP tools to search documentation before
answering. Watch the agent logs to see the MCP tool calls.

```bash
curl -s http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search Microsoft docs for AKS networking best practices",
    "agent_type": "learning"
  }' | jq
```

## Step 5 -- List available MCP tools

```bash
curl -s http://localhost:8080/mcp/tools | jq
```

This returns the three tools from the Microsoft Learn MCP server:
`microsoft_docs_search`, `microsoft_code_sample_search`, and
`microsoft_docs_fetch`.

## Step 6 -- Call the proxy directly (bypass the agent)

Useful for testing the proxy in isolation. Note the `Authorization`
header carrying the master key.

```bash
curl -s http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-master-1234" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello"}]
  }' | jq .choices[0].message.content
```

## Step 7 -- Observe the logs

Both containers emit structured JSON logs. Open two terminals side by
side to see the full request flow.

Terminal 1, proxy logs (model, tokens, cost, latency):

```bash
docker logs -f litellm-proxy 2>&1 | grep "\[PROXY-LOG\]"
```

Terminal 2, agent logs (traces, guardrails, MCP tool calls):

```bash
docker logs -f agent-app 2>&1 | grep "\[AGENT-LOG\]\|\[MODERATION\]"
```

Now send a request from a third terminal and watch both log streams
light up. Example proxy log entry:

```json
{
  "ts": "2026-04-14T13:27:40Z",
  "event": "llm_success",
  "model": "gpt-4o",
  "usage": {"prompt_tokens": 33, "completion_tokens": 267, "total_tokens": 300},
  "cost_usd": 0.002753,
  "latency_ms": 5779.4
}
```

Example agent log entries:

```json
{"event": "span_end", "span_data": {"type": "function", "tool_name": "microsoft_docs_search"}}
{"event": "span_end", "span_data": {"type": "generation", "model": "gpt-4o"}}
```

## Step 8 -- Guardrails

Content moderation runs at two layers:

1. **LiteLLM proxy** -- `omni-moderation-latest` configured as
   `pre_call` (checks input) and `post_call` (checks output) in
   `proxy/config.yaml`.
2. **Agent app** -- `@input_guardrail` decorator calls the Moderation
   API before the agent runs, implemented in `agent/agent_app.py`.

When moderation triggers, the agent returns:

```json
{
  "agent": "GeneralAssistant",
  "response": "Your message was blocked by content moderation.",
  "guardrail_passed": false
}
```

## Step 9 -- Stop and clean up

```bash
docker compose down
```

Remove the images to reclaim disk space:

```bash
docker rmi $(docker compose images -q)
```


## File structure

```
litellmpoc/
+-- docker-compose.yaml          # Docker Compose orchestration
+-- .env.example                 # API key template
|
+-- proxy/                       # LiteLLM Proxy container
|   +-- Dockerfile
|   +-- config.yaml              # Models, guardrails, callback config
|   +-- custom_callbacks.py      # Structured JSON logger (PROXY-LOG)
|
+-- agent/                       # Agent App container
|   +-- Dockerfile
|   +-- requirements.txt
|   +-- agent_app.py             # FastAPI + Agents SDK + MCP + guardrails
|   +-- custom_logger.py         # Trace processor logger (AGENT-LOG)
|
+-- k8s/                         # Kubernetes manifests (optional)
    +-- namespace.yaml
    +-- secret.yaml              # Template, don't commit real keys!
    +-- proxy-configmap.yaml     # Config + callbacks mounted as volumes
    +-- proxy-deployment.yaml    # Proxy Deployment + Service
    +-- agent-deployment.yaml    # Agent Deployment + Service
```

## Key configuration

| Variable | Where | Purpose |
|----------|-------|---------|
| `OPENAI_API_KEY` | Both containers | OpenAI API access + moderation |
| `LITELLM_MASTER_KEY` | Both containers | Agent authenticates to proxy |
| `LITELLM_PROXY_URL` | Agent only | Proxy endpoint (auto-set in compose/k8s) |
| `MCP_SERVER_URL` | Agent only | Microsoft Learn MCP endpoint |


## Appendix: Kubernetes deployment

The `k8s/` directory contains manifests for deploying the same stack on
Kubernetes. This section is provided as reference; the lab focuses on
Docker Compose.

### Build and load the images

```bash
docker compose build
```

For **kind**:

```bash
kind load docker-image litellmpoc-litellm-proxy:latest
kind load docker-image litellmpoc-agent-app:latest
```

For **minikube**:

```bash
minikube image load litellmpoc-litellm-proxy:latest
minikube image load litellmpoc-agent-app:latest
```

For **Docker Desktop Kubernetes**, the images are already available.

### Create namespace and secret

```bash
kubectl apply -f k8s/namespace.yaml

kubectl -n litellm-poc create secret generic openai-credentials \
  --from-literal=OPENAI_API_KEY='sk-proj-your-key-here' \
  --from-literal=LITELLM_MASTER_KEY='sk-master-1234'
```

### Deploy

```bash
kubectl apply -f k8s/proxy-configmap.yaml
kubectl apply -f k8s/proxy-deployment.yaml
kubectl apply -f k8s/agent-deployment.yaml
```

### Verify

```bash
kubectl -n litellm-poc get pods -w
```

Both pods should reach `Running 1/1`.

### Port-forward

```bash
kubectl -n litellm-poc port-forward svc/agent-app 9080:8080 &
kubectl -n litellm-poc port-forward svc/litellm-proxy 9000:4000 &
```

The agent is now on `localhost:9080` and the proxy on `localhost:9000`.
Use the same curl commands from the Docker Compose steps, replacing port
8080 with 9080 and 4000 with 9000.

### View logs

```bash
POD=$(kubectl -n litellm-poc get pod -l app=litellm-proxy -o jsonpath='{.items[0].metadata.name}')
kubectl -n litellm-poc logs $POD | grep "\[PROXY-LOG\]"
```

```bash
POD=$(kubectl -n litellm-poc get pod -l app=agent-app -o jsonpath='{.items[0].metadata.name}')
kubectl -n litellm-poc logs $POD | grep "\[AGENT-LOG\]"
```

### Tear down

```bash
kubectl delete namespace litellm-poc
```

### Troubleshooting

**Proxy CrashLoopBackOff:** The locally-built image must be available to
the cluster. On Docker Desktop it is automatic. On kind/minikube you
must load the image first (see above).

**Port-forward dies after rollout restart:** The forward is tied to the
old pod. Kill and recreate it:

```bash
pkill -f "port-forward.*litellm-poc"
kubectl -n litellm-poc port-forward svc/agent-app 9080:8080 &
kubectl -n litellm-poc port-forward svc/litellm-proxy 9000:4000 &
```
