![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Python](https://img.shields.io/badge/Python-blue) ![Docker](https://img.shields.io/badge/Docker-blue) ![Mem0](https://img.shields.io/badge/Mem0-pink)

# LAB087: Mem0, Intelligent Memory Layer for AI Agents

## Introduction

LLMs are stateless. Every API call starts fresh, with no memory of
previous interactions. If you want an agent to remember that a user
prefers sci-fi over thrillers, or that Bob is allergic to peanuts, you
have to build that memory layer yourself.

Mem0 solves this by sitting between your agent and a vector database.
When you call `m.add(messages, user_id="alice")`, Mem0 distills the
conversation into discrete facts ("Alice likes sci-fi movies") and
stores them as embeddings. When you later call `m.search("movie
recommendations", user_id="alice")`, it returns the relevant facts via
semantic search.

This lab has two tracks. The **self-hosted** track uses a local Qdrant
container as the vector store. The **SaaS** track uses Mem0's managed
API, which handles storage, indexing, and retrieval for you.

## Why does this matter?

In production agentic systems, long-term memory is what turns a
stateless chatbot into a personalized assistant:

- **Personalization**: the agent remembers user preferences across
  sessions without you having to replay the full conversation each
  time.
- **Token efficiency**: instead of stuffing the entire history into the
  prompt, the agent retrieves only the facts relevant to the current
  query.
- **Multi-user isolation**: each user_id gets its own memory scope.
  Alice's preferences never leak into Bob's session.
- **Collaboration**: a shared run_id lets multiple agents (or humans)
  contribute to and query a common knowledge base.

## Set up your environment

```bash
export OPENAI_API_KEY="sk-..."
```

```bash
./lab_setup.sh
source .lab087/bin/activate
```

## Part 1: Self-hosted with Qdrant

These exercises use a local Qdrant container as the vector store.
Start it before running anything:

```bash
docker run -d --name qdrant \
    -p 6333:6333 -p 6334:6334 \
    -v $PWD/qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest
```

| Exercise | File | What it covers |
|----------|------|----------------|
| 1 | `mem_01.py` | Add a conversation to memory, retrieve extracted facts |
| 2 | `mem_02.py` | Retrieve and semantically search stored memories |
| 3 | `mem_03.py` | OpenAI agent with memory tools (add/search/get_all) |
| 4 | `mem_04.py` | Interactive chat: agent stores and recalls facts across turns |
| 5 | `mem_05.py` | Collaborative memory: multiple participants share one context |

### Exercise 1: Basic memory operations

The simplest case. A short conversation about movie preferences is
passed to `m.add()`. Mem0 distills it into discrete facts and stores
them in Qdrant. The script then retrieves all memories for that user.

```bash
python3 mem_01.py
```

### Exercise 2: Retrieval and semantic search

Connects to the same Qdrant and retrieves the memories that exercise 1
stored. Also demonstrates semantic search: even if you never used the
word "genre", Mem0 finds the relevant memory because the embeddings
capture meaning, not just keywords.

```bash
python3 mem_02.py
```

### Exercise 3: Agent with memory tools

Combines the OpenAI Agents SDK with Mem0. Three `function_tool`
functions (add_to_memory, search_memory, get_all_memory) are exposed to
the agent. The agent decides when to call each tool based on the user's
message. This is a single-shot example: one prompt, one response.

```bash
python3 mem_03.py
```

### Exercise 4: Interactive chat with persistent memory

Same agent as exercise 3, but wrapped in an interactive loop. The
script asks for your name and uses it as the user_id. Share some facts,
quit, restart, and the agent still remembers everything because the
memories live in Qdrant.

```bash
python3 mem_04.py
```

Try this sequence:

1. Run with name "alice", tell the agent your favorite food.
2. Quit, restart with name "alice", ask "What's my favorite food?"
3. Restart with name "bob", ask the same question. Bob gets no answer.

### Exercise 5: Collaborative memory

Multiple participants (Alice, Bob, and an AI assistant) share a single
memory scope via a common `run_id`. Each participant adds messages,
and the assistant can brainstorm using the combined context. Useful for
multi-agent collaboration or shared project knowledge bases.

```bash
python3 mem_05.py
```

## Part 2: Managed SaaS

These exercises use Mem0's managed API. No Docker, no Qdrant. You
need an API key from [app.mem0.ai](https://app.mem0.ai).

```bash
export MEM0_API_KEY="your_key"
```

| Exercise | File | What it covers |
|----------|------|----------------|
| S1 | `mem0_managed/mem_01_saas.py` | Add memories, search with filters, retrieve all |
| S2 | `mem0_managed/mem_02_saas.py` | OpenAI agent with SaaS-backed memory tools (v2 API) |
| S3 | `mem0_managed/mem_03_agent.py` | Multi-turn agent test: add, search, get_all in sequence |

### Exercise S1: Basic SaaS operations

Same concept as exercise 1, but uses `MemoryClient()` instead of a
local `Memory.from_config()`. Demonstrates the v2 API with filters
for category-based search and paginated retrieval.

```bash
python3 mem0_managed/mem_01_saas.py
```

### Exercise S2: SaaS agent integration

Same agent pattern as exercise 3, but backed by `MemoryClient`. Uses
the v2 API with `output_format="v1.1"` to avoid deprecation warnings.

```bash
python3 mem0_managed/mem_02_saas.py
```

### Exercise S3: Multi-turn agent test

Imports the agent from S2 and runs a full sequence: store two facts,
search for one, then retrieve all. Good for verifying end-to-end
behavior of the SaaS integration.

```bash
python3 mem0_managed/mem_03_agent.py
```

## Part 3: OpenMemory, the MCP approach

OpenMemory is an open-source project from the Mem0 team that exposes
memory as an MCP server. Instead of importing `mem0` in your code, you
run OpenMemory as a local service and any MCP-compatible client (Claude
Desktop, Cursor, your own agent) can store and search memories over
the standard MCP protocol.

This is interesting because it decouples memory from your application
code entirely: any tool that speaks MCP gets persistent memory for free.

### Quick start

```bash
git clone https://github.com/mem0ai/mem0.git
cd mem0/openmemory
```

Configure the environment files:

```bash
cp api/.env.example api/.env
cp ui/.env.example ui/.env
```

Edit `api/.env` and set your keys:

```
OPENAI_API_KEY=sk-...
USER=philippe
```

Edit `ui/.env`:

```
NEXT_PUBLIC_API_URL=http://localhost:8765
NEXT_PUBLIC_USER_ID=philippe
```

Build and start the containers:

```bash
make build
make up
```

This starts three containers: an MCP backend (port 8765), a Qdrant
vector store, and a web UI (port 3000). Open http://localhost:3000 to
browse stored memories.

### Connecting a client

Register your client with the MCP server:

```bash
npx @openmemory/install local http://localhost:8765/mcp/<client-name>/sse/<user-id>
```

For example, to connect Claude Desktop:

```bash
npx @openmemory/install local http://localhost:8765/mcp/claude/sse/philippe
```

After registration, Claude Desktop (or any MCP client) can call memory
tools (add, search, get_all, delete) transparently.

### Why this matters

In Part 1 and Part 2, your Python code calls `m.add()` and
`m.search()` directly. With OpenMemory, the memory layer becomes a
standalone service that any agent can use via MCP, without importing a
single library. This is the difference between "memory as a library"
and "memory as infrastructure."

### Cleanup

```bash
cd mem0/openmemory
make down
```

For more details, see the
[OpenMemory repo](https://github.com/mem0ai/mem0/tree/main/openmemory).

## Self-hosted vs SaaS: what changes?

The core API is identical. The only difference is how you initialize
the memory client:

| | Self-hosted | SaaS |
|---|---|---|
| Import | `from mem0 import Memory` | `from mem0 import MemoryClient` |
| Init | `Memory.from_config(config)` | `MemoryClient()` |
| Vector store | You manage Qdrant/Chroma/etc. | Mem0 manages it |
| API key | `OPENAI_API_KEY` only | `OPENAI_API_KEY` + `MEM0_API_KEY` |
| Search/add/get_all | Same methods | Same methods (use `version="v2"`) |
| Infrastructure | Docker + Qdrant | None |

Switching between the two is a one-line change: swap the import and
constructor.

## How Mem0 works under the hood

```
m.add(messages, user_id="alice")
    |
    +--> LLM extracts discrete facts from the conversation
    |        "Alice likes sci-fi movies"
    |        "Alice dislikes thrillers"
    |
    +--> Facts are embedded (OpenAI embeddings)
    |
    +--> Embeddings stored in vector DB (Qdrant / Mem0 cloud)

m.search("movie recommendations", user_id="alice")
    |
    +--> Query is embedded
    |
    +--> Vector similarity search in user's scope
    |
    +--> Returns ranked facts
```

The key insight: Mem0 does not store raw messages. It distills
conversations into facts first, then embeds and indexes those facts.
This means searches return clean, discrete memories rather than chunks
of conversation text.

## Key concepts

- **Memory.from_config()**: creates a self-hosted memory client
  backed by a vector database you control.
- **MemoryClient()**: creates a SaaS client that talks to Mem0's
  managed API.
- **user_id**: scopes memories to a single user. Memories are fully
  isolated between user IDs.
- **run_id**: scopes memories to a shared context (collaborative
  memory). Multiple users/agents can read and write.
- **Semantic search**: queries are matched by meaning, not keywords.
  "What movies does she enjoy?" matches "Alice likes sci-fi."
- **function_tool**: the OpenAI Agents SDK decorator that exposes a
  Python function as a tool the agent can call.

## Cleanup

```bash
deactivate
```

```bash
./lab_cleanup.sh
```

Stop and remove the Qdrant container:

```bash
docker stop qdrant && docker rm qdrant
rm -rf qdrant_storage
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
