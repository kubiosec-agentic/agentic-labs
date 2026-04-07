"""
Chroma v2 Python client example.

Connects to a running Chroma server, creates a collection with OpenAI
embeddings, upserts a document, and runs a similarity query.

Prerequisites:
    pip install chromadb openai
    export OPENAI_API_KEY="your-key-here"
    chroma run --path ./chroma_db --host 127.0.0.1 --port 8000
"""

import os
import chromadb
from chromadb.utils import embedding_functions

TENANT = "default_tenant"
DB = "default_database"

# ---------------------------------------------------------------
# 1. Connect to the Chroma HTTP server
# ---------------------------------------------------------------
client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    ssl=False,
    tenant=TENANT,
    database=DB,
)

print(f"Connected to Chroma server (tenant={TENANT}, database={DB})")
print(f"Server heartbeat: {client.heartbeat()}")

# ---------------------------------------------------------------
# 2. Set up OpenAI as the embedding function
# ---------------------------------------------------------------
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)

# ---------------------------------------------------------------
# 3. Create (or get) a collection with cosine similarity
# ---------------------------------------------------------------
col = client.get_or_create_collection(
    name="demo",
    metadata={"hnsw:space": "cosine"},
    embedding_function=openai_ef,
)

print(f"Collection: {col.name}  (count: {col.count()})")

# ---------------------------------------------------------------
# 4. Upsert documents
# ---------------------------------------------------------------
docs = [
    ("doc1", "Brussels is the capital of Belgium.",              {"source": "geography"}),
    ("doc2", "Belgium borders the Netherlands, Germany, Luxembourg, and France.", {"source": "geography"}),
    ("doc3", "Belgian chocolate is world-renowned.",             {"source": "culture"}),
]

col.upsert(
    ids=[d[0] for d in docs],
    documents=[d[1] for d in docs],
    metadatas=[d[2] for d in docs],
)

print(f"Upserted {len(docs)} documents  (collection count: {col.count()})")

# ---------------------------------------------------------------
# 5. Query by text (embedding happens automatically)
# ---------------------------------------------------------------
queries = [
    "What city is Belgium's capital?",
    "Which countries are Belgium's neighbors?",
]

for query in queries:
    print(f"\nQuery: {query}")
    results = col.query(
        query_texts=[query],
        n_results=2,
        include=["documents", "metadatas", "distances"],
    )
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        print(f"  [{i+1}] distance={dist:.4f}  source={meta['source']}")
        print(f"      {doc}")
