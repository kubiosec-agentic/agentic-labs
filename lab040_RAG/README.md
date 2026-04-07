![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![Responses_API](https://img.shields.io/badge/Responses_API-brightgreen) ![RAG](https://img.shields.io/badge/RAG-pink) ![LlamaIndex](https://img.shields.io/badge/LlamaIndex-pink) ![Chroma](https://img.shields.io/badge/Chroma-pink)

# LAB040: Retrieval-Augmented Generation (RAG)

## Introduction

LLMs are powerful, but they only know what was in their training data. If you ask about your company's internal docs, last week's security advisory, or a PDF you just downloaded, the model can only guess.

**RAG** (Retrieval-Augmented Generation) solves this by adding a retrieval step before generation: find the most relevant chunks of your data, inject them into the prompt, and let the model answer grounded in real context.

This lab walks through five approaches to RAG, each using a different framework or API:

| Step | Script | Framework | What it demonstrates |
|------|--------|-----------|---------------------|
| 1 | `RAG_01.py` | **LlamaIndex** | Vector index with persistent storage, retrieval vs. LLM synthesis |
| 2 | `RAG_02.py` | **LangChain + Chroma** | Document chunking, embedding, similarity search |
| 3 | `RAG_03.py` | **LangChain + Chroma** | Full RAG pipeline with custom prompt and LLM synthesis |
| 4 | `RAG_04.py` + curl | **OpenAI Responses API** | Managed vector store with file_search (no local DB needed) |
| 5 | `RAG_05_agentic.py` | **OpenAI SDK** | Agentic RAG: the LLM decides when and what to retrieve |

The progression matters: Steps 1-3 show you the mechanics (chunking, embedding, retrieval, synthesis). Step 4 shows how OpenAI can handle the entire pipeline for you. Step 5 is where it gets interesting for agentic systems: the model itself decides whether it needs to retrieve, making RAG part of an autonomous reasoning loop.

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
```

### Option A: Virtual environment (local)

```bash
./lab_setup.sh
source .lab040/bin/activate
```

### Option B: Docker

```bash
docker compose up -d --build
docker exec -it lab040_rag bash
```

From inside the container, run any script as described below. The volume mount means edits on your host are immediately available inside the container.

When done:
```bash
docker compose down
```

## Lab instructions

### Step 1: RAG with LlamaIndex (`RAG_01.py`)

This script builds a persistent vector index over the documents in `data/` using LlamaIndex. On first run it creates embeddings and stores them in `./storage/`. On subsequent runs it loads from cache (fast).

The script has a toggle: `USE_LLM = True` uses GPT-4o to synthesize a natural-language answer from the retrieved chunks. Set it to `False` to see only the raw vector search results with similarity scores.

```bash
python3 ./RAG_01.py
```

**What to observe:**
- The difference between retrieval-only output (raw chunks + scores) and LLM-synthesized answers
- The `similarity_top_k=2` parameter: try changing it to 1 or 5 and see how the answer quality changes
- The `./storage/` directory created on first run (persistent index)

**Framework:** LlamaIndex handles chunking, embedding, storage, and retrieval in one pipeline. Under the hood it uses `text-embedding-3-small` for embeddings and `gpt-4o` for synthesis.

### Step 2: Vector search with Chroma (`RAG_02.py`)

This script uses LangChain + Chroma to load a text file, split it into chunks, embed them, and perform both similarity search and vector search.

```bash
python3 ./RAG_02.py
```

**What to observe:**
- Two search modes: `similarity_search` (text query in, matching chunks out) vs. `similarity_search_by_vector` (raw embedding vector in). Same results, different entry points.
- The chunking parameters: `chunk_size=1000, chunk_overlap=0`. No overlap means chunks are independent. Compare with Step 3 which uses overlap.

**Framework:** LangChain provides the document loading and text splitting. Chroma is an in-memory/persistent vector database. OpenAI provides the embeddings.

### Step 3: Full RAG pipeline with LLM synthesis (`RAG_03.py`)

Builds on Step 2 by adding an LLM that reads the retrieved chunks and generates a coherent answer. This is a complete RAG pipeline: load, chunk, embed, retrieve, synthesize.

```bash
python3 ./RAG_03.py
```

**What to observe:**
- `RecursiveCharacterTextSplitter` with `chunk_overlap=200`: chunks share 200 characters of context at boundaries, which helps the model understand content that spans chunk boundaries
- The custom prompt template that explicitly tells the model to use only the retrieved context
- The chunk count and sizes printed at the start: this helps you understand how your document gets split

**Framework:** LangChain orchestrates the full pipeline. The prompt template is where you control how the model uses the retrieved context, which is key for preventing hallucination.

### Step 4: OpenAI managed vector store with Responses API (`RAG_04.py`)

Instead of running your own vector database, OpenAI can host it for you. The Python SDK handles all the setup: create a vector store, upload your file, wait for indexing, and query with `file_search`. No curl commands, no manual IDs to copy.

```bash
python3 ./RAG_04.py
```

The script does everything in one run:
1. Creates a managed vector store on OpenAI's servers
2. Uploads `data/llms-full.txt`
3. Waits for indexing to complete
4. Queries with `file_search` via the Responses API
5. Cleans up (deletes the vector store and file)

**What to observe:**
- No local vector database needed. OpenAI handles chunking, embedding, storage, and retrieval.
- The response includes `file_citation` annotations pointing back to source documents.
- Compare the answer quality with Steps 1-3: same data, different retrieval infrastructure.
- The cleanup step at the end is important: managed vector stores have storage costs.

> **Note:** The vector stores API is part of the Assistants infrastructure, which is scheduled for deprecation in August 2026. OpenAI is migrating these capabilities to the Responses API. The Python SDK handles the required `OpenAI-Beta: assistants=v2` header automatically, so your code will keep working until the migration is complete.

<details>
<summary>Optional: try it with curl to see the raw API</summary>

The Python SDK abstracts the HTTP calls. If you want to see what happens under the hood, you can do it with curl. Note that vector store management currently requires the `OpenAI-Beta: assistants=v2` header (the SDK handles this automatically).

```bash
# Create a vector store
VS_ID=$(curl https://api.openai.com/v1/vector_stores \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{"name": "MCP documentation"}' | jq -r .id)

# Upload and link a file
FILE_ID=$(curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="assistants" \
  -F file="@data/llms-full.txt" | jq -r .id)

curl https://api.openai.com/v1/vector_stores/$VS_ID/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{"file_id": "'$FILE_ID'"}'

# Query via Responses API (no beta header needed here)
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "tools": [{"type": "file_search", "vector_store_ids": ["'$VS_ID'"]}],
    "input": "What are the differentiating features of MCP?"
  }' | jq -r '.output[].content[0].text'
```
</details>

### Step 5: Agentic RAG (`RAG_05_agentic.py`)

This is the most important step for understanding agentic systems. In Steps 1-4, the retrieval step is hardcoded: you always search, then always synthesize. In agentic RAG, **the model decides** whether it needs to retrieve at all.

The script creates a tiny in-memory vector store (5 documents), registers a `vector_search` tool, and runs an agent loop. The LLM receives the user question and autonomously decides: do I need to search, or can I answer directly? If it searches, it gets the results and can search again or answer.

```bash
python3 ./RAG_05_agentic.py
```

**What to observe:**
- The agent loop: `retrieve -> reason -> respond` (or skip retrieval if the model is confident)
- The tool spec registered with OpenAI: the model sees `vector_search` as a callable function
- Cosine similarity scores in the results: the model gets relevance information, not just text
- Try changing the query to something the vector store doesn't cover and watch the model handle it

For a detailed walkthrough of how this works, see [ARAG/AgenticRAG.md](./ARAG/AgenticRAG.md).

| Feature | Standard RAG (Steps 1-3) | Agentic RAG (Step 5) |
|---------|--------------------------|----------------------|
| Retrieval | Always runs, hardcoded | Model decides dynamically |
| Reasoning | Single pass | Multi-turn decision loop |
| Tool use | External, static | Invoked via tool calls |
| Autonomy | None | Model controls the flow |

## Framework comparison

| Aspect | LlamaIndex (Step 1) | LangChain + Chroma (Steps 2-3) | OpenAI file_search (Step 4) |
|--------|---------------------|--------------------------------|----------------------------|
| Setup complexity | Low (one pipeline) | Medium (separate components) | Lowest (fully managed) |
| Persistence | Local filesystem | Local or server | Cloud (OpenAI hosted) |
| Customization | High | Highest (mix and match) | Limited to API parameters |
| Cost | Embedding API calls only | Embedding API calls only | Embedding + storage fees |
| Offline capable | Yes (after embedding) | Yes (after embedding) | No |
| Best for | Quick prototyping | Production pipelines | Managed deployments |

## Going further

The [lab990_addendum/chromadb](../lab990_addendum/chromadb/) folder covers running Chroma as a standalone server (v2 API), including curl-based operations and OWASP LLM Top-10 risk mapping for vector databases.

## Cleanup environment

```bash
deactivate
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
