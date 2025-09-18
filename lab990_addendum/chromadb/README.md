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
# Chroma v2 RAG risks ↔ OWASP LLM Top-10
OWASP risk	How it shows up with a Chroma v2 server	Quick mitigations you can apply now

## LLM01 Prompt Injection	
Retrieved chunks can contain hidden instructions that steer the model, because similarity search optimizes for semantic proximity, not safety.	Retrieval-time content filtering, instruction firewalls, strict output schemas, “reader” prompts that treat retrieved text as untrusted data, allowlist tool use on the answering step. 
OWASP

## LLM02 Insecure Output Handling	
Your app may act on model output derived from Chroma without sanitizing it, leading to command/SQL/HTTP calls based on attacker-planted text.	Treat model output as data. Escape, validate, and sandbox. Never pipe model text to shells or drivers without validation. 
OWASP

## LLM03 Training Data Poisoning	
Poisoned docs upserted to Chroma skew retrieval or teach the system wrong patterns. Even “read-only” inference gets poisoned at the retrieval layer.	Write-path controls. Moderation on upsert. Provenance and signer metadata on docs. Periodic audits for indicators of poisoning. 
OWASP

## LLM04 Model Denial of Service	
Large vectors, massive upsert batches, unbounded n_results, or many concurrent query calls can starve the app or the embedder.	Rate limits per tenant and API key. Cap payload sizes and n_results. Add timeouts and circuit breakers. Back-pressure on ingestion workers. 
OWASP

## LLM05 Supply Chain Vulnerabilities	
Chroma Docker image, client SDKs, and embedding libs are dependencies. A compromised image or lib exposes the data path.	Pin versions and SBOMs, scan images, verify signatures, restrict egress from the DB host. 
OWASP

## LLM06 Sensitive Information Disclosure
Embeddings and stored documents may contain secrets or personal data. Cross-tenant or cross-database exposure is catastrophic.	Use Chroma v2 tenants and databases for isolation, enforce auth at the gateway, encrypt in transit, consider encrypting at rest, avoid returning raw embeddings to untrusted callers. 
cookbook.chromadb.dev

## LLM07 Insecure Plugin Design	
In an agentic app, the “vector store” is effectively a tool. If the model has write or delete via the HTTP client, you hand it mutation power.	Split read vs write identities. Give the model a read-only client. Human-in-the-loop or policy checks for mutations. Tool schemas that disallow destructive ops by default. 
OWASP

## LLM08 Excessive Agency	
The model can autonomously create collections, exfiltrate hits, or chain queries to enumerate your corpus.	Capability minimization: only expose query on a scoped collection. No list-collections. No admin routes. Require approvals for broadened scopes. 
OWASP

## LLM09 Overreliance	
Treating nearest neighbors as ground truth leads to confident but wrong answers when the neighborhood is weak.	Calibrate with similarity thresholds, cross-encoders or re-rankers, retrieval provenance in the answer, abstention paths when confidence is low. 
OWASP

## LLM10 Model Theft	
Systematic scraping of embeddings or documents lets attackers reconstruct proprietary data or shadow your knowledge base.	Throttle queries, watermark content outside the DB, per-tenant keys, anomaly detection on query patterns, never return embeddings to untrusted users. 
OWASP



## Chroma v2 specifics worth leaning on

Tenants and databases are first-class in v2. Use them to segment customers, teams, and environments, then place network and identity boundaries on top. 
cookbook.chromadb.dev
+1

Expose the server only behind a gateway with TLS and auth. Treat the /collections/*/upsert, /query, and any list endpoints as sensitive surfaces.

Minimal hardening checklist (actionable)

Network: bind Chroma to localhost, expose via a reverse proxy with TLS, WAF rules, and per-route auth.

AuthZ: read-only token for the model’s retrieval tool, separate write token for ingestion workers.

Abuse limits: cap n_results, payload size, and QPS per tenant. Set timeouts.

Poisoning guardrails: validate and scan docs on ingestion, attach source provenance in metadatas, and audit collections.

Privacy: avoid returning include=["embeddings"] to frontends. Keep PII out of embeddings when possible.

Observability: log retrieval prompts, top-k hits, and decisions. Alert on spikes in miss rates or strange query vectors.

Supply chain: pin and scan the Chroma image and clients. Track with SBOMs.

If you want, I can turn this into a one-page slide or a short policy YAML you can drop into your gateway to enforce the caps and route scopes.
