# 0) Prereqs
```
# Python 3.10+ recommended
pip install -U chromadb openai jq
```
```
export OPENAI_API_KEY=sk-...    # for embeddings
export BASE="http://localhost:8000/api/v2"
export TENANT="default_tenant"
export DB="default_database"
```
# 1) Start a local Chroma server
```
# persists to ./chroma_db (change path as you like)
chroma run --path ./chroma_db --host 127.0.0.1 --port 8000

```
# 2) Ensure tenant & database exist (v2)
```
# 2a) Create tenant (idempotent; server may return 409 if it already exists)
curl -s -X POST "$BASE/tenants" \
  -H "Content-Type: application/json" \
  -d '{"name":"'"$TENANT"'"}' | jq .

# 2b) Create database within the tenant
curl -s -X POST "$BASE/tenants/$TENANT/databases" \
  -H "Content-Type: application/json" \
  -d '{"name":"'"$DB"'"}' | jq .
```
# 3) Create a collection
```
COLL_RESP=$(curl -s -X POST "$BASE/tenants/$TENANT/databases/$DB/collections" \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","metadata":{"hnsw:space":"cosine"}}')

echo "$COLL_RESP" | jq .
COLL_ID=$(echo "$COLL_RESP" | jq -r '.id')
echo "Collection ID: $COLL_ID"
```
# 4) Add a document (client-side OpenAI embedding)
```
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
# 5) Similarity search via the API (curl)
```
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
# 6) Simple Python client that talks to the server (v2)
```
# pip install chromadb openai
import os, chromadb
from chromadb.utils import embedding_functions

TENANT = "default_tenant"
DB = "default_database"

# Connect to HTTP server; v2 is the default path in recent clients
client = chromadb.HttpClient(host="localhost", port=8000, ssl=False, tenant=TENANT, database=DB)

# Use OpenAI as a client-side embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)

col = client.get_or_create_collection(
    name="demo",
    metadata={"hnsw:space": "cosine"},
    embedding_function=openai_ef
)

# Upsert & query
col.upsert(
    ids=["py1"],
    documents=["Belgium borders the Netherlands, Germany, Luxembourg, and France."],
    metadatas=[{"source": "py"}],
)
res = col.query(
    query_texts=["Which countries neighbor Belgium?"],
    n_results=2,
    include=["documents","metadatas","distances"]
)
print(res)
```

