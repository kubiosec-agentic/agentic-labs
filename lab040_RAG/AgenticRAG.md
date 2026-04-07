# Agentic RAG: How RAG_05_agentic.py Works

This document walks through the internals of `RAG_05_agentic.py`, the agentic RAG demo from Step 5 of lab040. In standard RAG (Steps 1-4), retrieval is hardcoded: every query always searches, always retrieves, always synthesizes. In agentic RAG, the LLM decides whether it needs to retrieve at all, and can retrieve multiple times if needed.

## 1. In-memory vector store

The script creates a tiny vector store from a dictionary of short documents. Each document is embedded using `text-embedding-3-small`, and the resulting vectors are L2-normalized for cosine similarity:

```python
doc_vecs /= np.linalg.norm(doc_vecs, axis=1, keepdims=True)
```

This is deliberately minimal: five documents, no database, no persistence. The point is to isolate the agentic behavior from infrastructure concerns.

## 2. The vector_search tool

A `vector_search` function computes cosine similarity between a query embedding and the document embeddings, returning the top-k most relevant documents with their scores.

This function is registered as an OpenAI function-callable tool via a JSON spec (`tool_spec`). The LLM sees it as a tool it can choose to invoke, not something that runs automatically.

## 3. The agent loop

The core of agentic RAG is the `agentic_query` function, which runs a loop:

1. The LLM receives the user question.
2. It decides whether it needs more context. If so, it emits a `tool_calls` response requesting `vector_search` with a query string.
3. The script executes the tool call and feeds the results back as a tool message.
4. The LLM reasons over the retrieved chunks and either requests another search or produces a final answer.

This loop continues until the LLM responds with a regular message (no tool calls), meaning it has enough information to answer.

```
User question
    |
    v
LLM: Do I need to search? --yes--> vector_search(query)
    |                                      |
    no                                     v
    |                              Return top-k chunks
    v                                      |
Final answer <-------- LLM reasons over chunks
```

## 4. What makes this "agentic"

In standard RAG, the retrieval step is a fixed part of the pipeline. The developer decides when and what to retrieve. In agentic RAG:

- The model chooses whether to retrieve (it might answer directly if the question is within its training data)
- The model formulates the search query (it might rephrase the user's question for better retrieval)
- The model can retrieve multiple times (first search informs a more targeted second search)
- The model decides when it has enough context to answer

This is the same pattern used in production agent systems where the LLM orchestrates multiple tools. RAG becomes one tool among many, invoked when the model judges it useful.

| Feature | Standard RAG (Steps 1-4) | Agentic RAG (Step 5) |
|---------|--------------------------|----------------------|
| Retrieval | Always runs, hardcoded | Model decides dynamically |
| Reasoning | Single pass | Multi-turn decision loop |
| Tool use | External, static | Invoked via tool calls |
| Autonomy | None | Model controls the flow |
| Search query | User's original question | Model may rephrase |

## Running the demo

```bash
python3 RAG_05_agentic.py
```

Watch the output for lines like `Tool call: vector_search(...)`, which show the model deciding to retrieve. Try changing the query to something outside the vector store's content and observe whether the model skips retrieval entirely.
