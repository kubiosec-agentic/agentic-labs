"""
Exercise 4: Persistent RAG pipeline.

THE PROBLEM WITH IN-MEMORY STORAGE
-----------------------------------
Exercises 1 through 3 use chromadb.Client() which is in-memory. Every
time the script exits, the data is gone. That is fine for demos, but
useless in production. You do not want to re-embed 100,000 documents
every time your service restarts.

THE FIX: PersistentClient
--------------------------
chromadb.PersistentClient(path="./chroma_storage") writes the HNSW
index and document data to disk. On the next run, the collection is
already populated, so we skip the embedding step entirely.

This is the pattern for a real deployment:
  - First run:  embed documents, store in persistent collection
  - Next runs:  skip embedding, go straight to queries
  - Updates:    add/delete individual documents without re-embedding

In production you would typically run ChromaDB as a separate Docker
container (chroma server mode) rather than embedded in your Python
process. The API is the same; only the client initialization changes.

IDEMPOTENT LOADING
------------------
The script checks collection.count() before adding documents. If the
collection already has data, it skips the add step. This makes the
script safe to run multiple times without creating duplicates.

After running this script, try verify_persistence.py to confirm the
data survived:
    python3 rag_metadata_04.py       # first run: embeds and stores
    python3 verify_persistence.py    # confirms data is still there
    python3 rag_metadata_04.py       # second run: skips embedding

Run:
    python3 rag_metadata_04.py
"""

from openai import OpenAI
import chromadb
import os

client_openai = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"

# -------------------------------------------------------------------------
# Persistent storage setup.
#
# PersistentClient writes data to a local directory. ChromaDB uses
# SQLite + HNSW under the hood. The directory contains:
#   - chroma.sqlite3       : document text, metadata, IDs
#   - index files          : the HNSW vector index for fast search
#
# On subsequent runs, data is loaded from disk automatically.
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(CURRENT_DIR, "chroma_storage")
os.makedirs(PERSIST_DIR, exist_ok=True)

print(f"ChromaDB version: {chromadb.__version__}")
print(f"Persistence directory: {PERSIST_DIR}")

client = chromadb.PersistentClient(path=PERSIST_DIR)

collection = client.get_or_create_collection(
    name="my_docs",
    embedding_function=None,    # we provide embeddings manually
    metadata={"hnsw:space": "cosine"},
)


# -------------------------------------------------------------------------
# Embedding helper.
#
# Sends texts to the OpenAI embeddings API in a single batch call.
# This is the expensive part: one API call per batch of documents.
# With persistent storage, you only pay this cost once.
# -------------------------------------------------------------------------
def get_embeddings(texts):
    response = client_openai.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [d.embedding for d in response.data]


# -------------------------------------------------------------------------
# Idempotent document loading.
#
# If the collection is empty (first run), embed and store everything.
# If it already has data (subsequent runs), skip straight to queries.
# This is what makes the script safe to run repeatedly.
# -------------------------------------------------------------------------
if collection.count() == 0:
    print("\nCollection is empty. Embedding and storing documents...")

    public_docs = [
        "Product roadmap for Q2 includes chatbot enhancements and UI redesign.",
        "Our chatbot now supports voice input for better accessibility.",
        "The new pricing tier will be announced during the June webinar.",
        "Customer satisfaction with support automation increased by 15%.",
        "Public API documentation is now live at api.company.com/docs.",
        "The chatbot handled 12,000 customer interactions last month.",
        "Open beta of our chatbot plugin for Slack starts next week.",
        "New training dataset improves greeting intent accuracy by 9%.",
        "Public case study: Retail chatbot saves 300 hours/month.",
        "Updated terms of service for chatbot usage are now available.",
        "Blog post: How we scaled our chatbot infrastructure in 3 weeks.",
        "Launch recap: Over 2,000 users tested the chatbot on day one.",
        "We're partnering with universities to provide chatbot access.",
        "Survey results: Most requested feature is order tracking.",
        "The chatbot now speaks Dutch and German.",
        "Public changelog updated with March 2025 improvements.",
        "New tutorial video covers chatbot integration in React apps.",
        "Webinar next week: Building inclusive AI for customer service.",
        "We open-sourced our fallback handling module on GitHub.",
        "Customer support chatbot wins industry design award.",
    ]

    conf_docs = [
        "Chatbot error logs revealed edge-case crashes in voice-to-text module. (CONFIDENTIAL)",
        "Internal Slack thread discussed delays in chatbot release. (CONFIDENTIAL)",
        "Legal team flagged GDPR issue in session retention. (CONFIDENTIAL)",
        "The chatbot budget was reduced by 20% last quarter. (CONFIDENTIAL)",
        "Employee IDs were accidentally included in test dataset. (CONFIDENTIAL)",
        "Internal note: chatbot project team facing burnout concerns. (CONFIDENTIAL)",
        "Staging server credentials exposed during CI pipeline. (CONFIDENTIAL)",
        "Meeting notes: execs debated removing chatbot from roadmap. (CONFIDENTIAL)",
        "Strategy pivot: chatbot may be merged into support hub. (CONFIDENTIAL)",
        "Voice data collection policy under legal review. (CONFIDENTIAL)",
        "Security audit uncovered SSO bypass in chatbot admin panel. (CONFIDENTIAL)",
        "Jira ticket shows hardcoded tokens in chatbot training script. (CONFIDENTIAL)",
        "User feedback labeled as toxic was misclassified. (CONFIDENTIAL)",
        "Team leads propose moving chatbot team to Paris office. (CONFIDENTIAL)",
        "Private alpha testing revealed 17% fail rate in routing logic. (CONFIDENTIAL)",
        "AWS costs spiked due to misconfigured chatbot autoscaling. (CONFIDENTIAL)",
        "Confidential roadmap includes HR chatbot for internal onboarding. (CONFIDENTIAL)",
        "Budget request for chatbot training GPU cluster denied. (CONFIDENTIAL)",
        "Chatbot vendor contract ends December 2025. (CONFIDENTIAL)",
        "Pilot with legal chatbot red-flagged by compliance. (CONFIDENTIAL)",
    ]

    documents = public_docs + conf_docs
    metadatas = (
        [{"access": "public"} for _ in public_docs]
        + [{"access": "confidential"} for _ in conf_docs]
    )
    ids = [f"doc{i}" for i in range(40)]

    embeddings = get_embeddings(documents)
    collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)

    print(f"Stored {len(documents)} documents.")
    print(f"Storage contents: {os.listdir(PERSIST_DIR)}")
else:
    print(f"\nCollection already has {collection.count()} documents. Skipping embedding.")


# -------------------------------------------------------------------------
# List all stored entries (paginated).
#
# ChromaDB does not have a "SELECT *" equivalent, so we retrieve in
# batches using offset/limit. This is useful for debugging and
# verifying what is actually in the database.
# -------------------------------------------------------------------------
def print_all_entries(coll, batch_size=100):
    total = coll.count()
    print(f"\nTotal entries in collection: {total}\n")
    if total == 0:
        print("Collection is empty.")
        return

    for i in range(0, total, batch_size):
        results = coll.get(include=["documents", "metadatas"], offset=i, limit=batch_size)
        for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
            print(f"  [{doc_id}] ({meta['access']}) {doc[:80]}...")
    print()


print_all_entries(collection)


# -------------------------------------------------------------------------
# Queries and RAG (same as exercise 3)
# -------------------------------------------------------------------------
def get_query_embedding(text):
    return client_openai.embeddings.create(input=text, model=EMBEDDING_MODEL).data[0].embedding


def print_results(title, results):
    print(f"\n=== {title} ===")
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result #{i + 1}")
        print(f"  Document: {doc}")
        print(f"  Metadata: {results['metadatas'][0][i]}")
        print(f"  Distance: {results['distances'][0][i]:.4f}")
        print("-" * 60)


results_public = collection.query(
    query_embeddings=[get_query_embedding("What are the chatbot's new features?")],
    n_results=3,
    where={"access": "public"},
)
print_results("Retrieval: Public docs only", results_public)

results_conf = collection.query(
    query_embeddings=[get_query_embedding("What internal issues exist with the chatbot?")],
    n_results=3,
    where={"access": "confidential"},
)
print_results("Retrieval: Confidential docs only", results_conf)


def query_rag(question, access_levels=None, n_results=5):
    """Full RAG: embed question, retrieve with access filter, generate answer."""
    query_embedding = get_query_embedding(question)

    where_filter = {}
    if access_levels:
        where_filter = (
            {"access": {"$in": access_levels}}
            if isinstance(access_levels, list)
            else {"access": access_levels}
        )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
    )
    context = "\n\n".join(results.get("documents", [[]])[0])

    prompt = f"""Answer the question using ONLY the context below.
If the context does not contain enough information, say so.

Context:
{context}

Question:
{question}
"""
    response = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


print("\n" + "=" * 60)
print("RAG: Public user asks about chatbot features (persistent storage)")
print("=" * 60)
answer = query_rag("What are the chatbot's new features?", access_levels=["public"])
print(answer)
