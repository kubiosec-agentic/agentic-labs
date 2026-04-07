# LlamaIndex Addendum: RAG over a GitHub Repository

This addendum extends [lab040_RAG](../../lab040_RAG/) by showing how LlamaIndex can ingest content directly from a GitHub repository (not just local files) and make it queryable through the same vector-search-plus-LLM pipeline.

In lab040 Step 1 (`RAG_01.py`), you indexed local text files. Here, the LlamaIndex GitHub reader pulls source code and documentation from a public repo via the GitHub API, builds a vector index in memory, and lets you ask questions about the project.

| File | Description |
|------|-------------|
| [rag_github.py](./rag_github.py) | Load a GitHub repo into LlamaIndex, build a vector index, query with GPT-4o |
| [requirements.txt](./requirements.txt) | Python dependencies (LlamaIndex + GitHub reader + OpenAI LLM) |

## Prerequisites

You need two API keys:

```bash
export OPENAI_API_KEY="your-key-here"
export GITHUB_TOKEN="your-github-token"
```

Get a GitHub personal access token at [github.com/settings/tokens](https://github.com/settings/tokens). No special scopes are needed for public repositories.

Install dependencies:

```bash
pip install -r requirements.txt --break-system-packages
```

## Run

```bash
python3 rag_github.py
```

The script targets the [mcp-guardian/mcp-guardian](https://github.com/mcp-guardian/mcp-guardian) repo by default. To query a different repo, edit the `OWNER`, `REPO`, and `BRANCH` variables at the top of the script.

**What to observe:**
- The GitHub reader fetches files via the GitHub API (no local git clone needed). It filters by directory and file extension to skip images, notebooks, and lock files.
- The vector index is built in memory, just like lab040 Step 1, using OpenAI embeddings under the hood.
- Each query goes through the full RAG pipeline: embed the question, retrieve relevant chunks from the index, send chunks + question to GPT-4o for synthesis.
- Try changing the questions list or pointing at a repo you work on to see how well the retrieval handles different codebases.

**How this relates to lab040:**
- Step 1 (`RAG_01.py`) loads from local files with `SimpleDirectoryReader`; this script loads from GitHub with `GithubRepositoryReader`. The rest of the pipeline (embedding, indexing, querying) is identical.
- This is one of LlamaIndex's strengths: pluggable data loaders (called "readers") that feed into the same indexing and query infrastructure.

## Cleanup

No local state is created (the index lives in memory). Just unset your environment variables if needed.

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
