# Simple Agentic-RAG Demo with OpenAI SDK

This Python script demonstrates **Agentic Retrieval-Augmented Generation (Agentic-RAG)** — an advanced form of RAG where the **LLM itself actively decides when to use tools like retrieval** in order to produce better, grounded answers.

> ✅ Unlike traditional RAG systems where the retrieval step is pre-programmed and static, Agentic-RAG empowers the model to **think, decide, retrieve, and respond** — making it more autonomous and adaptive.

---

## What This Code Does

### 1. Tiny In-Memory Vector Store

A dictionary of short documents (`docs`) is embedded using the `text-embedding-3-small` model. The result is a small vector store where document embeddings are normalized:

```python
doc_vecs /= np.linalg.norm(doc_vecs, axis=1, keepdims=True)  # Row-wise L2-normalization
```

This prepares the data for efficient **cosine similarity** search.

---

### 2. Tool: `vector_search`

A function `vector_search` performs similarity search by comparing the query embedding with document embeddings, returning the `top‑k` most relevant documents.

The tool is defined as a JSON spec (`tool_spec`) and registered as an OpenAI **function-callable tool**. The LLM can invoke this tool when it thinks it needs additional context.

---

### 3. Agent Loop: retrieve ↔ reason ↔ respond

The heart of **Agentic-RAG** is in this loop:

```python
def agentic_query(user_query: str) -> str:
```

Here's what happens:

1. **The LLM receives the user query.**
2. It considers whether it needs more information.
3. If so, it **decides on its own** to call the `vector_search` tool.
4. It receives the results and **continues reasoning** using the retrieved knowledge.
5. Finally, it returns a grounded, context-aware answer.

This flow enables **agent-like behavior**: the model can dynamically decide to retrieve, process new info, and adapt its answer accordingly.

---

## Why This is *Agentic* RAG

| Feature                        | Standard RAG       | Agentic RAG (This Code)      |
|-------------------------------|--------------------|------------------------------|
| Retrieval                     | Pre-programmed     | Chosen dynamically by LLM    |
| Reasoning steps               | One-shot           | Multi-turn decision loop     |
| Tool use                      | External, static   | Invoked via tool calls       |
| Autonomy                      | No                 | Yes — the model decides flow |
| Flexibility                   | Limited            | Adaptive to query complexity |

---

## Example Output

Running the script:

```bash
python agentic_rag.py
```

May result in output like:

> **"Chunking is important because it breaks large texts into semantically meaningful units that improve retrieval relevance. A local expert in Belgium is Philippe Bogaerts, known for his work in continuous learning and AI."**

Notice how the agent retrieved multiple passages and used them to form a complete, factual response, grounded in the vector store.

---


## 📎 Summary

This demo shows how **LLMs can be given decision-making power** through the use of tools like `vector_search`, forming an **agentic loop** of "retrieve → reason → respond". This paradigm makes RAG systems smarter, more flexible, and better suited for complex, real-world tasks.
