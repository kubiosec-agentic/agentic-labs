import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# Define OpenAI embedding model
EMBEDDING_MODEL = "text-embedding-3-small"

# Set up embedding function using OpenAI
embedding_fn = OpenAIEmbeddingFunction(model_name=EMBEDDING_MODEL)

# Initialize ChromaDB client
client = chromadb.Client(Settings())

# Create or get collection with embedding function
collection = client.get_or_create_collection(
    name="my_docs",
    embedding_function=embedding_fn
)

# Clear existing documents
collection.delete(ids=[f"doc{i}" for i in range(40)])

# Sample public documents
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
    "Customer support chatbot wins industry design award."
]

# Sample confidential documents
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
    "Pilot with legal chatbot red-flagged by compliance. (CONFIDENTIAL)"
]

# Combine documents and metadata
documents = public_docs + conf_docs
metadatas = [{"access": "public"} for _ in public_docs] + [{"access": "confidential"} for _ in conf_docs]
ids = [f"doc{i}" for i in range(40)]

# Add documents to Chroma (embedding is handled automatically)
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

# Helper to print results
def print_results(title, results):
    print(f"\n=== {title} ===")
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result #{i + 1}")
        print(f"📄 Document: {doc}")
        print(f"🏷️  Metadata: {results['metadatas'][0][i]}")
        print(f"📏 Distance: {results['distances'][0][i]:.4f}")
        print("-" * 50)

# Query 1: Public only
results_public = collection.query(
    query_texts=["What are the chatbot's new features?"],
    n_results=3,
    where={"access": "public"}
)
print_results("Query: Only Public Documents", results_public)

# Query 2: Confidential only
results_conf = collection.query(
    query_texts=["What internal issues exist with the chatbot?"],
    n_results=3,
    where={"access": "confidential"}
)
print_results("Query: Only Confidential Documents", results_conf)

# Query 3: All documents
results_all = collection.query(
    query_texts=["Tell me about the project."],
    n_results=5,
    where={"access": {"$in": ["public", "confidential"]}}
)
print_results("Query: All Documents", results_all)
