"""
RAG over a GitHub repository using LlamaIndex.

This script clones a public GitHub repo via the LlamaIndex GitHub reader,
builds a vector index over its contents, and queries it with GPT-4o.
It demonstrates how LlamaIndex can ingest structured sources (not just
local files) and make them queryable through the same RAG pipeline used
in lab040_RAG.

Prerequisites:
    pip install -r requirements.txt
    export OPENAI_API_KEY="your-key-here"
    export GITHUB_TOKEN="your-github-token"

Get a GitHub token at: https://github.com/settings/tokens
(no special scopes needed for public repos)
"""

import os
import sys

from llama_index.core import VectorStoreIndex, Settings
from llama_index.readers.github import GithubRepositoryReader, GithubClient
from llama_index.llms.openai import OpenAI

# ---------------------------------------------------------------
# 1. Check environment
# ---------------------------------------------------------------
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    print("Error: GITHUB_TOKEN not set.")
    print("Get one at https://github.com/settings/tokens (no scopes needed for public repos)")
    sys.exit(1)

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY not set.")
    sys.exit(1)

# ---------------------------------------------------------------
# 2. Configure the target repository
# ---------------------------------------------------------------
# Change these to point at any public GitHub repo you want to query.
OWNER = "mcp-guardian"
REPO = "mcp-guardian"
BRANCH = "main"

print(f"[1/3] Loading documents from github.com/{OWNER}/{REPO} (branch: {BRANCH}) ...")

github_client = GithubClient(github_token=github_token, verbose=False)

documents = GithubRepositoryReader(
    github_client=github_client,
    owner=OWNER,
    repo=REPO,
    use_parser=False,
    verbose=False,
    filter_directories=(
        ["docs", "README", "readme", "src"],
        GithubRepositoryReader.FilterType.INCLUDE,
    ),
    filter_file_extensions=(
        [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json", ".ipynb", ".lock"],
        GithubRepositoryReader.FilterType.EXCLUDE,
    ),
).load_data(branch=BRANCH)

print(f"      Loaded {len(documents)} documents")

# ---------------------------------------------------------------
# 3. Build vector index
# ---------------------------------------------------------------
print("[2/3] Creating vector index ...")

Settings.llm = OpenAI(model="gpt-4o", temperature=0.1)

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# ---------------------------------------------------------------
# 4. Query
# ---------------------------------------------------------------
questions = [
    "What is this project about?",
    "What are the main features or components?",
    "How do you install and run this project?",
    "What security mechanisms does it provide?",
]

print(f"[3/3] Querying ({len(questions)} questions) ...\n")

for i, question in enumerate(questions, 1):
    print(f"{'=' * 60}")
    print(f"Q{i}: {question}")
    print("=" * 60)
    response = query_engine.query(question)
    print(response)
    print()

print("Done.")
