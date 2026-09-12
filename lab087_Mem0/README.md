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

### Cleanup: stop the Qdrant container

The self-hosted exercises are done. Stop the Qdrant container before
moving on to the SaaS track (or skip straight to cleanup at the bottom
if you are finished).

```bash
docker stop qdrant && docker rm qdrant
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

## Part 3: Memory over MCP (hosted Mem0 MCP)

Parts 1 and 2 import `mem0` and call `m.add()` / `m.search()` from your
own code. The MCP approach decouples memory from the application
entirely: memory runs as a service, and any MCP-compatible client
(Claude Desktop, Cursor, your own agent) stores and searches memories
over the standard MCP protocol without importing a single library. This
is the difference between "memory as a library" and "memory as
infrastructure."

> **What changed (2026).** This part used to run *OpenMemory*, a
> self-hosted MCP server plus dashboard that lived in `mem0ai/mem0`
> under `openmemory/`. That project has been **archived and removed**
> from the repo. A read-only snapshot survives at
> [`mem0ai/openmemory` → `openmemory-archive/`](https://github.com/mem0ai/openmemory/tree/main/openmemory-archive),
> and the `mem0ai/openmemory` repo name now hosts an unrelated
> session-sync tool. The maintained "memory over MCP" path today is the
> **hosted Mem0 MCP** described below. If you specifically need
> local/self-hosted memory, mem0 now ships a self-hosted **REST** server
> plus dashboard (`cd server && make bootstrap` in `mem0ai/mem0`, see
> the [self-hosted docs](https://docs.mem0.ai/open-source/overview)),
> but that one is REST, not MCP. There is no longer a maintained mem0
> server that is both self-hosted *and* MCP.

### The hosted endpoint

Mem0 runs a hosted MCP server at:

```
https://mcp.mem0.ai/mcp
```

It speaks streamable **HTTP** (not SSE) and exposes eleven memory tools:
`add_memory`, `search_memories`, `get_memories`, `get_memory`,
`update_memory`, `delete_memory`, `delete_all_memories`,
`delete_entities`, `list_entities`, `list_events`, and
`get_event_status`.

### Authentication

Two options. Browser sign-in is the default: the first time a client
calls a Mem0 tool it opens a browser window to authorize access to your
Mem0 account. For headless clients and CI, send your Mem0 API key from
[app.mem0.ai](https://app.mem0.ai) as an HTTP
`Authorization: Bearer <MEM0_API_KEY>` header. This is the same key
used in Part 2:

```bash
export MEM0_API_KEY="your_key"
```

### Register a client

For most clients the `mcp-add` helper writes the config for you:

```bash
npx mcp-add \
    --name mem0-mcp \
    --type http \
    --url "https://mcp.mem0.ai/mcp" \
    --clients "claude code,cursor,windsurf,vscode,opencode"
```

Claude Desktop does not support `mcp-add`; add it manually under
Settings > Connectors > Add custom connector, name `mem0-mcp`, URL
`https://mcp.mem0.ai/mcp`, then restart.

### Test with the MCP Inspector

Verify connectivity before wiring a full client. Note `--transport
http` (the hosted endpoint is streamable HTTP; the old OpenMemory
endpoint used `sse`) and pass the key as a bearer header:

```bash
npx -y @modelcontextprotocol/inspector --cli \
    https://mcp.mem0.ai/mcp \
    --transport http \
    --header "Authorization: Bearer $MEM0_API_KEY" \
    --method tools/list
```

Now a write/read round-trip. Two things about the tool schema matter,
and skipping either is why a search comes back empty:

- `add_memory` **requires a scope**: at least one of `user_id`,
  `agent_id`, or `run_id`. It is also **asynchronous**, it returns an
  `event_id`, and the memory is not searchable for a second or two.
- `search_memories` has no `user_id` argument; it scopes through
  `filters`. If you omit `filters`, it searches only the account's
  default scope. So you must search the **same** scope you wrote to.

Write a memory under an explicit `user_id`:

```bash
npx -y @modelcontextprotocol/inspector --cli \
    https://mcp.mem0.ai/mcp \
    --transport http \
    --header "Authorization: Bearer $MEM0_API_KEY" \
    --method tools/call \
    --tool-name add_memory \
    --tool-arg text="I work at RadarSec in Belgium" \
    --tool-arg user_id="philippe"
```

Read that same scope back (note the `filters` clause; give the async
write a moment first):

```bash
npx -y @modelcontextprotocol/inspector --cli \
    https://mcp.mem0.ai/mcp \
    --transport http \
    --header "Authorization: Bearer $MEM0_API_KEY" \
    --method tools/call \
    --tool-name search_memories \
    --tool-arg query="where do I work" \
    --tool-arg filters='{"AND":[{"user_id":"philippe"}]}'
```

To see which scopes currently hold anything, use `list_entities`:

```bash
npx -y @modelcontextprotocol/inspector --cli \
    https://mcp.mem0.ai/mcp \
    --transport http \
    --header "Authorization: Bearer $MEM0_API_KEY" \
    --method tools/call \
    --tool-name list_entities
```

> **Scoping gotcha.** Memories are partitioned by `user_id` (and
> optionally `agent_id` / `run_id`). When you don't pass a scope, the
> hosted MCP defaults to a user named after the connector itself,
> `mem0-mcp`, which starts out empty. So a filter-less `search_memories`
> looks only at the `mem0-mcp` scope and returns nothing, even though
> memories you created in Part 2 under `user_id="demo-user"` (or `alex`,
> etc.) are sitting right there in other buckets. An empty `results`
> list almost always means wrong scope, not a broken endpoint. Run
> `list_entities` to see every scope that holds memories, then pass the
> matching `filters` (e.g. `{"AND":[{"user_id":"demo-user"}]}`) to
> `search_memories` or `get_memories`.

Once the Inspector confirms connectivity, any MCP-compatible client can
call the same memory tools transparently.

### Why this matters (and the security angle)

Memory-as-infrastructure means any MCP client gets persistent,
cross-session memory without shipping a library. But moving from the old
local OpenMemory server to a hosted endpoint changes the threat model,
which is the interesting part for this course:

- **Data residency.** Memories now leave your machine and live in mem0's
  cloud. For the local-only guarantee that Part 1 (the self-hosted
  Qdrant track) makes, use the self-hosted REST server instead; the
  maintained local option is no longer MCP.
- **The bearer token is a memory credential.** Anyone holding
  `MEM0_API_KEY` can read and write the entire memory store over MCP.
  Treat it like any secret: keep it in an env var, never in source,
  rotate it, and scope it per environment.
- **Destructive tools are exposed.** The endpoint includes
  `delete_all_memories` and `delete_entities`. An agent, or a prompt
  injection that reaches it, can wipe the store, not just read it.
  Revisit lab070 and lab073 with this endpoint sitting on the server
  side of the MCP trust boundary.

### Cleanup

Nothing to tear down; the server is hosted. To disconnect, remove the
`mem0-mcp` entry from your client's MCP config (or delete the custom
connector in Claude Desktop).

For the current MCP docs, see
[docs.mem0.ai/platform/mem0-mcp](https://docs.mem0.ai/platform/mem0-mcp).

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
