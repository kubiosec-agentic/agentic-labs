"""
Exercise 1: Metadata-based access control in ChromaDB.

THE PROBLEM
-----------
An AI agent that retrieves documents to answer questions (RAG) will
happily return confidential data if you don't stop it. "Tell me about
the project" should return different results for a public user vs an
internal engineer. The content is the same database; the difference is
who is asking.

THE SOLUTION: METADATA FILTERING
---------------------------------
Every document stored in the vector database gets a metadata dict
alongside its text. In this example, the metadata is:

    {"access": "public"}       for press releases, docs, blog posts
    {"access": "confidential"} for internal issues, security findings

When querying, we pass a `where` filter:

    collection.query(
        query_texts=["..."],
        where={"access": "public"}    # <-- only public docs returned
    )

ChromaDB applies this filter BEFORE ranking by similarity. That means
confidential documents are never even considered, no matter how
semantically relevant they are. This is the simplest form of
authorization in a RAG pipeline.

HOW CHROMADB WORKS HERE
-----------------------
ChromaDB is an in-memory vector database. When you call collection.add()
with documents (plain text), ChromaDB:
  1. Generates embeddings internally (default: a small local model)
  2. Stores the text, metadata, and embedding together
  3. Builds an HNSW index for fast approximate nearest-neighbor search

When you call collection.query() with query_texts:
  1. The query is embedded using the same model
  2. The metadata filter (where=...) removes non-matching docs
  3. The remaining docs are ranked by cosine distance to the query

The "distance" in the output tells you how close the match is.
Lower = more similar. A distance of 0 would be an exact match.

Run:
    python3 rag_metadata_01.py
"""

import chromadb
from chromadb.config import Settings

# In-memory client: data lives only while the script runs.
# Exercise 4 shows how to make it persistent.
client = chromadb.Client(Settings())

# A "collection" in ChromaDB is like a table: it holds documents,
# their embeddings, and their metadata under one name.
collection = client.get_or_create_collection(name="my_docs")

# Clear any leftover data from previous runs
collection.delete(ids=[f"doc{i}" for i in range(40)])


# -------------------------------------------------------------------------
# Documents: 20 public, 20 confidential
#
# In a real system these would come from your document store, CMS, or
# knowledge base. The key point is that EVERY document gets a metadata
# tag indicating its access level.
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# Build the metadata list.
#
# Each document gets a dict: {"access": "public"} or {"access": "confidential"}.
# You can add as many fields as you want: department, author, date,
# classification level, project name, etc. More fields = more granular
# filtering.
# -------------------------------------------------------------------------
documents = public_docs + conf_docs
metadatas = (
    [{"access": "public"} for _ in public_docs]
    + [{"access": "confidential"} for _ in conf_docs]
)
ids = [f"doc{i}" for i in range(40)]

# Add everything to ChromaDB. Embeddings are generated automatically
# using ChromaDB's default embedding model (a small local model).
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
# Query 1: Public user asks about chatbot features.
#
# The where filter ensures that ONLY public documents are searched.
# Even though some confidential docs are semantically relevant to
# "chatbot features", they are excluded before ranking.
# -------------------------------------------------------------------------
results_public = collection.query(
    query_texts=["What are the chatbot's new features?"],
    n_results=3,
    where={"access": "public"},
)
print_results("Query: Public user (only public docs)", results_public)


# -------------------------------------------------------------------------
# Query 2: Internal engineer asks about issues.
#
# Now we filter for confidential only. The public marketing docs are
# excluded even though they mention the chatbot.
# -------------------------------------------------------------------------
results_conf = collection.query(
    query_texts=["What internal issues exist with the chatbot?"],
    n_results=3,
    where={"access": "confidential"},
)
print_results("Query: Internal user (only confidential docs)", results_conf)


# -------------------------------------------------------------------------
# Query 3: Admin with full access.
#
# The $or operator combines multiple access levels. This is how you
# would implement role-based access: map the user's role to a list
# of allowed access levels, then build the where filter dynamically.
# -------------------------------------------------------------------------
results_all = collection.query(
    query_texts=["Tell me about the project."],
    n_results=5,
    where={"$or": [{"access": "public"}, {"access": "confidential"}]},
)
print_results("Query: Admin (all docs)", results_all)
