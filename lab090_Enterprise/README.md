![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Python](https://img.shields.io/badge/Python-blue) ![Security](https://img.shields.io/badge/Security-red) ![RAG](https://img.shields.io/badge/RAG-pink) ![Docker](https://img.shields.io/badge/Docker-blue)

# LAB090: Enterprise-Ready Agent Systems

## Introduction

Building an agent that works on your laptop is one thing. Running it
in production is something else entirely. This lab covers the gap
between a prototype and an enterprise-grade deployment:

- **Authentication and authorization**: OAuth 2.0 flows (M2M and
  web app) for securing agent APIs.
- **Observability**: tracing agent calls with Traceloop and OpenAI's
  built-in tracing so you can see what your agents are doing (and why
  they fail).
- **Access-controlled RAG**: metadata-based filtering in ChromaDB to
  enforce who can see what when an agent retrieves documents.
- **Dockerized agents**: packaging an OpenAI agent as a containerized
  FastAPI service with health checks, structured logging, correlation
  IDs, and resource limits.

## Set up your environment

```bash
export OPENAI_API_KEY="sk-..."
```

```bash
./lab_setup.sh
source .lab090/bin/activate
```

## Part 1: Authentication and Authorization

### OAuth 2.0 M2M (Machine-to-Machine)

The M2M flow is what you use when one service calls another, with no
human in the loop. A `client.py` authenticates with Amazon Cognito
using the OAuth 2.0 client credentials flow, then calls a protected
FastAPI server that verifies the JWT and forwards the request to
OpenAI.

Instructions and code:
[OAuth 2.0 M2M API Server with OpenAI Integration](https://github.com/kubiosec-ai/openai-oauth-demo/)

### OAuth 2.0 Web Application

The web app flow handles human users logging in via a browser. A Flask
app uses Authlib to implement the OAuth Authorization Code Flow with
Amazon Cognito, including token inspection, session management, and an
admin-only route that calls OpenAI.

Instructions and code:
[OAuth Web Application Demo](https://github.com/kubiosec-codecamp/oauth-web-app.git)

## Part 2: Observability and Tracing

### Traceloop integration

Traceloop wraps your OpenAI calls with OpenTelemetry traces. The
`@workflow` decorator captures latency, token usage, and errors for
every call, and ships the data to the Traceloop dashboard.

```bash
export TRACELOOP_API_KEY="tl_..."
python3 traceloop_01.py
```

Check [traceloop.com](https://www.traceloop.com/) for the dashboard.

### OpenAI Agents SDK built-in tracing

The OpenAI Agents SDK has built-in tracing that is enabled by default.
Every agent run automatically logs LLM generations, tool calls,
handoffs, and guardrail decisions. No extra code needed: just run your
agent and the traces appear in the OpenAI dashboard.

**Exercise 1: Guardrails + tracing**

Builds a triage agent with a homework guardrail that blocks off-topic
questions, then routes accepted inputs to a math or history tutor.
Every guardrail decision and handoff is visible in the trace.

```bash
python3 openai_trace_01.py
```

**Exercise 2: Custom traces, spans, and sensitive data control**

Goes deeper into the tracing API:

- `trace()` context manager to group multiple agent runs into one
  workflow trace
- `custom_span()` to add your own application-level spans (input
  validation, database calls, etc.)
- `RunConfig(trace_include_sensitive_data=False)` to redact LLM
  inputs/outputs from traces (useful for compliance)

```bash
python3 openai_trace_02.py
```

After running either exercise, view the full traces at:
https://platform.openai.com/traces

The traces show a timeline of every step the agent took, how long each
step lasted, which tools were called, and what the LLM generated at
each point. This is what you use for debugging and performance
analysis in production.

## Part 3: Access-Controlled RAG

These exercises build up a RAG pipeline with metadata-based access
control. The idea: documents are tagged as `public` or
`confidential`, and the retrieval query filters by access level.
This is how you prevent an agent from leaking internal data to
unauthorized users.

| Exercise | File | What it adds |
|----------|------|-------------|
| 1 | `rag_metadata_01.py` | ChromaDB basics: add docs with metadata, query with access filters |
| 2 | `rag_metadata_02.py` | Automatic OpenAI embeddings via ChromaDB's embedding function |
| 3 | `rag_metadata_03.py` | Full RAG pipeline: embed, retrieve, generate with GPT-4o |
| 4 | `rag_metadata_04.py` | Persistent storage: data survives restarts |
| - | `verify_persistence.py` | Verify that persistent storage works |

### Exercise 1: Metadata-based access control

Stores 20 public and 20 confidential documents in ChromaDB, then
queries with `where={"access": "public"}` to demonstrate that
confidential docs are excluded from results.

```bash
python3 rag_metadata_01.py
```

### Exercise 2: OpenAI embeddings

Same documents, but uses ChromaDB's `OpenAIEmbeddingFunction` to
automatically compute embeddings with `text-embedding-3-small`. No
manual embedding management needed.

```bash
export CHROMA_OPENAI_API_KEY=$OPENAI_API_KEY
python3 rag_metadata_02.py
```

### Exercise 3: Full RAG with GPT-4o

Adds the generation step: retrieved documents are assembled into a
context string, passed to GPT-4o, and the model answers grounded in
the retrieved evidence. Access filtering still applies.

```bash
python3 rag_metadata_03.py
```

### Exercise 4: Persistent storage

Uses `chromadb.PersistentClient` so data survives between script runs.
Run it once to populate, then run `verify_persistence.py` to confirm
the data is still there.

```bash
python3 rag_metadata_04.py
python3 verify_persistence.py
```

## Part 4: Dockerized Agent Service

This is the "how do I ship this to production" part. The `docker_agent/`
directory packages an OpenAI agent as a containerized FastAPI service
with enterprise patterns baked in.

### What is in the box

```
docker_agent/
  agent_service.py     # FastAPI app with the agent
  Dockerfile           # Multi-stage build, non-root user
  docker-compose.yml   # Orchestration with resource limits
  .env.example         # Template for secrets
```

The service exposes two endpoints:

- `POST /chat` : send a message, get the agent's response
- `GET /health` : health check for K8s / ECS / any orchestrator

### Enterprise patterns demonstrated

**Structured JSON logging.** Every log line is a JSON object with
timestamp, level, message, and correlation ID. This is what log
aggregators (ELK, Datadog, CloudWatch) expect.

**Correlation IDs.** Every request gets a UUID that flows through
logs and the response header (`X-Correlation-ID`). When a user
reports an issue, you can trace the full request lifecycle.

**Health checks.** The `/health` endpoint returns the service status
and configuration checks. The Dockerfile and docker-compose both
define health checks so the orchestrator knows when the container is
ready to serve traffic.

**Non-root execution.** The Dockerfile creates and switches to a
non-root user. Containers should never run as root in production.

**Resource limits.** docker-compose sets memory (512M) and CPU (1.0)
limits. Without these, a single runaway request can starve the host.

**Environment-based secrets.** The API key comes from `.env` or
environment variables, never from the image. The `.env` file is in
`.gitignore` by default.

### Run it

```bash
cd docker_agent
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

```bash
docker compose up --build
```

Test it:

```bash
curl -s http://localhost:8000/health | jq .
```

```bash
curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What is the weather in Brussels?", "user_id": "demo"}' | jq .
```

You should see structured JSON logs in the Docker output with
correlation IDs matching the response headers.

### Run without Docker (local dev)

```bash
cd docker_agent
pip install -r requirements.txt
python3 agent_service.py
```

### Stop it

```bash
docker compose down
```

## Making agents enterprise-ready: checklist

Here is a summary of what separates a prototype from a production
agent deployment:

| Concern | Prototype | Production |
|---------|-----------|------------|
| Secrets | Hardcoded in code | Environment variables, vault, or secrets manager |
| Logging | `print()` | Structured JSON, shipped to a log aggregator |
| Tracing | None | Correlation IDs, OpenTelemetry, Traceloop |
| Auth | None | OAuth 2.0, JWT validation, API keys with scopes |
| Access control | All data visible | Metadata filtering in RAG, role-based access |
| Packaging | `python script.py` | Docker image, health checks, resource limits |
| Orchestration | Manual | K8s Deployment, ECS Task, or similar |
| Error handling | Stacktrace in terminal | Structured error responses, retry logic, circuit breakers |
| Scaling | Single process | Multiple replicas behind a load balancer |
| Monitoring | Check terminal | Dashboards, alerts on latency/error rate |

The exercises in this lab cover the first six rows. The last four are
infrastructure-level concerns that depend on your cloud provider and
deployment platform, but the Docker example gives you a starting point
that works with any orchestrator.

## Cleanup

```bash
deactivate
./lab_cleanup.sh
```

For the Docker example:

```bash
cd docker_agent && docker compose down
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
