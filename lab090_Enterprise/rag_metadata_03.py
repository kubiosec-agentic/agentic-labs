"""
Exercise 3: Full RAG pipeline with access control.

WHAT IS RAG?
------------
Retrieval-Augmented Generation (RAG) is a two-step pattern:

  1. RETRIEVE: Find documents relevant to the user's question using
     vector similarity search (the "R" in RAG).
  2. GENERATE: Pass those documents as context to an LLM and ask it
     to answer the question using only that context (the "G" in RAG).

This grounds the LLM's response in your actual data instead of
letting it hallucinate. The LLM becomes a "reader" of your documents,
not a "knower" of everything.

WHAT THIS EXERCISE ADDS
------------------------
Exercises 1 and 2 only did retrieval. This exercise adds the
generation step: we take the top-k retrieved documents, assemble
them into a context string, and send them to GPT-4o with the
instruction "Answer using ONLY the context below."

The access control from exercise 1 still applies. If you pass
access_levels=["public"], confidential documents are never retrieved,
so the LLM never sees them. This is defense-in-depth: even if the
LLM tried to leak data, it literally does not have access to it.

WHY MANUAL EMBEDDINGS?
----------------------
In exercise 2 we let ChromaDB handle embeddings automatically via
OpenAIEmbeddingFunction. Here we manage embeddings manually using
the OpenAI client. This gives you full control over:
  - Which model to use (text-embedding-3-small vs 3-large)
  - Batching strategy (send all docs in one API call)
  - Caching (store embeddings and reuse them)
  - The similarity metric (cosine, configured via hnsw:space)

In production you would typically use the automatic approach (exercise 2)
for simplicity, and switch to manual embeddings only if you need the
extra control.

Run:
    python3 rag_metadata_03.py
"""

from openai import OpenAI
import chromadb
from chromadb.config import Settings

client_openai = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"

# -------------------------------------------------------------------------
# ChromaDB setup with manual embeddings.
#
# embedding_function=None tells ChromaDB "I will provide embeddings
# myself." metadata={"hnsw:space": "cosine"} sets the distance metric
# to cosine similarity (default is L2 / Euclidean).
# -------------------------------------------------------------------------
client = chromadb.Client(Settings())
collection = client.get_or_create_collection(
    name="my_docs",
    embedding_function=None,
    metadata={"hnsw:space": "cosine"},
)
collection.delete(ids=[f"doc{i}" for i in range(40)])


# Same documents as previous exercises
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


# -------------------------------------------------------------------------
# Embed all documents in a single API call.
#
# The OpenAI embeddings endpoint accepts a list of strings and returns
# one vector per string. Each vector has 1536 dimensions for
# text-embedding-3-small. This is more efficient than embedding one
# document at a time.
# -------------------------------------------------------------------------
def get_embeddings(texts):
    response = client_openai.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [d.embedding for d in response.data]


embeddings = get_embeddings(documents)

# Store documents WITH their pre-computed embeddings
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids,
    embeddings=embeddings,
)


def print_results(title, results):
    print(f"\n=== {title} ===")
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result #{i + 1}")
        print(f"  Document: {doc}")
        print(f"  Metadata: {results['metadatas'][0][i]}")
        print(f"  Distance: {results['distances'][0][i]:.4f}")
        print("-" * 60)


# -------------------------------------------------------------------------
# Retrieval queries (same as before, but with manual embeddings)
# -------------------------------------------------------------------------
results_public = collection.query(
    query_embeddings=[get_embeddings(["What are the chatbot's new features?"])[0]],
    n_results=3,
    where={"access": "public"},
)
print_results("Retrieval: Public docs only", results_public)

results_conf = collection.query(
    query_embeddings=[get_embeddings(["What internal issues exist with the chatbot?"])[0]],
    n_results=3,
    where={"access": "confidential"},
)
print_results("Retrieval: Confidential docs only", results_conf)


# -------------------------------------------------------------------------
# THE RAG FUNCTION
#
# This is the core pattern:
#   1. Embed the question
#   2. Retrieve top-k documents, filtered by access level
#   3. Build a prompt: "Answer using ONLY this context"
#   4. Send to GPT-4o
#
# The access_levels parameter is the authorization gate. In a real
# application, you would derive this from the user's JWT claims,
# RBAC role, or session attributes. Never let the user control
# this parameter directly.
# -------------------------------------------------------------------------
def query_rag(question, access_levels=None, n_results=5):
    # Step 1: Embed the question
    query_embedding = client_openai.embeddings.create(
        input=question, model=EMBEDDING_MODEL
    ).data[0].embedding

    # Step 2: Build the metadata filter from the user's access level
    where_filter = {}
    if access_levels:
        if isinstance(access_levels, list):
            where_filter = {"access": {"$in": access_levels}}
        else:
            where_filter = {"access": access_levels}

    # Step 3: Retrieve relevant documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
    )

    # Step 4: Assemble retrieved docs into a context string
    retrieved_docs = results.get("documents", [[]])[0]
    context = "\n\n".join(retrieved_docs)

    # Step 5: Ask GPT-4o to answer using ONLY the retrieved context.
    # The "ONLY" instruction reduces hallucination: if the answer
    # is not in the context, the model should say so.
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


# -------------------------------------------------------------------------
# Test the RAG pipeline.
#
# Notice: the public user gets an answer based only on public docs.
# The confidential docs about "budget cuts" or "security audits" are
# never included in the context, so the LLM cannot leak them.
# -------------------------------------------------------------------------
print("\n" + "=" * 60)
print("RAG: Public user asks about chatbot features")
print("=" * 60)
answer = query_rag("What are the chatbot's new features?", access_levels=["public"])
print(answer)
