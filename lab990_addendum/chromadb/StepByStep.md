# Chroma v2 Server: Step-by-Step Walkthrough

This walkthrough runs a local Chroma server, creates a collection, adds a document with an OpenAI embedding, and queries it, all via curl and a short Python script. It pairs with the security discussion in [README.md](./README.md).

## Prerequisites

```bash
pip install chromadb openai --break-system-packages
```

You also need `jq` (command-line JSON processor). Install it with your system package manager:

```bash
# macOS
brew install jq

# Ubuntu / Debian
sudo apt-get install -y jq
```

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
export BASE="http://localhost:8000/api/v2"
export TENANT="default_tenant"
export DB="default_database"
```

## Step 1: Start a local Chroma server (Terminal 1)

```bash
chroma run --path ./chroma_db --host 127.0.0.1 --port 8000
```

Data persists in `./chroma_db`. Leave this terminal running and open a second one for the remaining steps.

## Step 2: Create tenant and database (Terminal 2)

Chroma v2 uses tenants and databases for multi-tenant isolation. The default tenant and database may already exist; a 409 response is fine.

```bash
# Create tenant (409 = already exists, that's OK)
curl -s -X POST "$BASE/tenants" \
  -H "Content-Type: application/json" \
  -d '{"name":"'"$TENANT"'"}' | jq .

# Create database within the tenant
curl -s -X POST "$BASE/tenants/$TENANT/databases" \
  -H "Content-Type: application/json" \
  -d '{"name":"'"$DB"'"}' | jq .
```

## Step 3: Create a collection

```bash
COLL_RESP=$(curl -s -X POST "$BASE/tenants/$TENANT/databases/$DB/collections" \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","metadata":{"hnsw:space":"cosine"}}')

echo "$COLL_RESP" | jq .
COLL_ID=$(echo "$COLL_RESP" | jq -r '.id')
echo "Collection ID: $COLL_ID"
```

**What to observe:** The `hnsw:space` metadata sets the distance function. Cosine is standard for text embeddings.

## Step 4: Add a document (client-side OpenAI embedding)

```bash
DOC='Brussels is the capital of Belgium.'

EMBED=$(curl -s https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-3-small","input":"'"$DOC"'"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$BASE/tenants/$TENANT/databases/$DB/collections/$COLL_ID/upsert" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg id "doc1" --arg doc "$DOC" --argjson emb "$EMBED" \
        '{ids:[$id], documents:[$doc], embeddings:[$emb], metadatas:[{source:"demo"}]}')" \
  | jq .
```

**What to observe:** The embedding is created client-side via the OpenAI API, then sent to Chroma with the document text and metadata. Chroma stores the vector; it does not call OpenAI itself.

## Step 5: Similarity search via curl

```bash
QUERY="What city is Belgium's capital?"

QEMBED=$(curl -s https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-3-small","input":"'"$QUERY"'"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$BASE/tenants/$TENANT/databases/$DB/collections/$COLL_ID/query" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --argjson q "$QEMBED" \
        '{query_embeddings:[$q], n_results:3, include:["documents","metadatas","distances"]}')" \
  | jq .
```

**What to observe:** The query embedding is computed the same way as the document embedding. Chroma returns the closest matches with distances. Lower distance = more similar.

## Step 6: Python client (v2)

The same operations in Python, using the Chroma HTTP client and OpenAI embedding function:

```python
# pip install chromadb openai
import os
import chromadb
from chromadb.utils import embedding_functions

TENANT = "default_tenant"
DB = "default_database"

# Connect to the HTTP server
client = chromadb.HttpClient(
    host="localhost", port=8000, ssl=False,
    tenant=TENANT, database=DB,
)

# Use OpenAI as a client-side embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)

col = client.get_or_create_collection(
    name="demo",
    metadata={"hnsw:space": "cosine"},
    embedding_function=openai_ef,
)

# Upsert a document
col.upsert(
    ids=["py1"],
    documents=["Belgium borders the Netherlands, Germany, Luxembourg, and France."],
    metadatas=[{"source": "python-client"}],
)

# Query
res = col.query(
    query_texts=["Which countries neighbor Belgium?"],
    n_results=2,
    include=["documents", "metadatas", "distances"],
)
print(res)
```

**What to observe:** The Python client handles embedding automatically via the `embedding_function`. You pass plain text; it calls OpenAI, gets the vector, and sends it to Chroma. Compare this with Step 4 where you did the embedding manually with curl.

## Cleanup

Stop the Chroma server (Ctrl+C in Terminal 1). To remove persisted data:

```bash
rm -rf ./chroma_db
```
