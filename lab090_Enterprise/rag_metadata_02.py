"""
Exercise 2: OpenAI embeddings via ChromaDB's embedding function.

WHAT CHANGES FROM EXERCISE 1
-----------------------------
Exercise 1 used ChromaDB's default embedding model (a small local
model). It works, but the embeddings are not very good for semantic
search. In production you want a stronger model.

Here we swap in OpenAI's text-embedding-3-small by passing an
OpenAIEmbeddingFunction to the collection. Now ChromaDB will call the
OpenAI API automatically every time you add or query documents.

WHY THIS MATTERS
----------------
The embedding model determines how well "What are the chatbot's new
features?" matches "Our chatbot now supports voice input." A better
embedding model produces vectors that capture meaning more accurately,
which means your RAG pipeline retrieves more relevant documents.

text-embedding-3-small is a good trade-off between quality and cost.
For higher accuracy at 6x the cost, use text-embedding-3-large.

HOW THE EMBEDDING FUNCTION WORKS
---------------------------------
When you call collection.add(documents=[...]):
  1. ChromaDB passes each document to the embedding function
  2. The function calls OpenAI's embeddings API
  3. The returned vectors (1536 dimensions) are stored in the HNSW index

When you call collection.query(query_texts=[...]):
  1. The query text is embedded using the same function
  2. ChromaDB searches for nearest neighbors in vector space
  3. The where filter is applied to remove unauthorized docs

You never see the embeddings directly; ChromaDB handles it all.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export CHROMA_OPENAI_API_KEY=$OPENAI_API_KEY

Run:
    python3 rag_metadata_02.py
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# -------------------------------------------------------------------------
# Configure the embedding function.
#
# ChromaDB will call this for every add() and query() operation.
# The CHROMA_OPENAI_API_KEY env var is read automatically.
# -------------------------------------------------------------------------
EMBEDDING_MODEL = "text-embedding-3-small"
embedding_fn = OpenAIEmbeddingFunction(model_name=EMBEDDING_MODEL)

client = chromadb.Client(Settings())

# Pass the embedding function when creating the collection.
# All documents added to this collection will be embedded with OpenAI.
collection = client.get_or_create_collection(
    name="my_docs",
    embedding_function=embedding_fn,
)

collection.delete(ids=[f"doc{i}" for i in range(40)])


# Same documents as exercise 1
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

# When we call add(), ChromaDB sends each document to the OpenAI
# embeddings API and stores the resulting vectors. This is the only
# step that costs money (a few cents for 40 short documents).
collection.add(documents=documents, metadatas=metadatas, ids=ids)


def print_results(title, results):
    print(f"\n=== {title} ===")
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result #{i + 1}")
        print(f"  Document: {doc}")
        print(f"  Metadata: {results['metadatas'][0][i]}")
        print(f"  Distance: {results['distances'][0][i]:.4f}")
        print("-" * 60)


# -------------------------------------------------------------------------
# Compare the distances with exercise 1. OpenAI embeddings should
# produce lower distances (better matches) for semantically similar
# queries, because the model understands meaning better than the
# default local model.
# -------------------------------------------------------------------------

results_public = collection.query(
    query_texts=["What are the chatbot's new features?"],
    n_results=3,
    where={"access": "public"},
)
print_results("Query: Public user (OpenAI embeddings)", results_public)

results_conf = collection.query(
    query_texts=["What internal issues exist with the chatbot?"],
    n_results=3,
    where={"access": "confidential"},
)
print_results("Query: Internal user (OpenAI embeddings)", results_conf)

# $in is a shorthand for $or on a single field
results_all = collection.query(
    query_texts=["Tell me about the project."],
    n_results=5,
    where={"access": {"$in": ["public", "confidential"]}},
)
print_results("Query: Admin (all docs, OpenAI embeddings)", results_all)
