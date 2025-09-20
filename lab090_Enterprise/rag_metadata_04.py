import openai
import chromadb
from chromadb.config import Settings
import os

# Print ChromaDB version
print(f"ChromaDB version: {chromadb.__version__}")

# Set your OpenAI API key

# Use OpenAI's text-embedding-3-small (1536 dimensions)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

# Use an absolute path for persistence
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(CURRENT_DIR, "chroma_storage")
print(f"Using persistence directory: {PERSIST_DIR}")

# Make sure the directory exists
os.makedirs(PERSIST_DIR, exist_ok=True)

# Initialize ChromaDB client with persistence - use this instead
print("Creating a new ChromaDB client with persistent storage...")
try:
    # Try the newer API format if available
    client = chromadb.PersistentClient(path=PERSIST_DIR)
except AttributeError:
    # Fall back to the older API if PersistentClient is not available
    client = chromadb.Client(Settings(persist_directory=PERSIST_DIR, 
                                     chroma_db_impl="duckdb+parquet"))

# Create or get collection
collection = client.get_or_create_collection(
    name="my_docs",
    embedding_function=None,
    metadata={"hnsw:space": "cosine"}
)

# Only add documents if not already present
if collection.count() == 0:
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

    # Generate embeddings for all documents
    def get_embeddings(texts):
        response = openai.embeddings.create(input=texts, model=EMBEDDING_MODEL)
        return [d.embedding for d in response.data]

    embeddings = get_embeddings(documents)

    # Add documents to ChromaDB
    collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
    
    # Verification code - check if data was stored
    print(f"Added {len(documents)} documents to ChromaDB collection")
    print(f"Collection count after adding: {collection.count()}")
    print(f"Check if storage directory exists: {os.path.exists(PERSIST_DIR)}")
    storage_files = os.listdir(PERSIST_DIR) if os.path.exists(PERSIST_DIR) else []
    print(f"Storage directory contents: {storage_files}")
    # Removed client.persist() as persistence is automatic with persist_directory

# Print all entries in the collection
def print_all_entries(collection, batch_size=100):
    total = collection.count()
    print(f"\n📦 Total entries in collection: {total}\n")

    if total == 0:
        print("Collection is empty.")
        return

    # ChromaDB doesn't have a native way to "list all", so we retrieve by slicing IDs
    for i in range(0, total, batch_size):
        results = collection.get(
            include=["documents", "metadatas"],  # Removed "ids" from include
            offset=i,
            limit=batch_size
        )
        for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
            print(f"🆔 ID: {doc_id}")
            print(f"📄 Document: {doc}")
            print(f"🏷️ Metadata: {meta}")
            print("-" * 50)

# Call the function
print_all_entries(collection)




# Function to print query results
def print_results(title, results):
    print(f"\n=== {title} ===")
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result #{i + 1}")
        print(f"📄 Document: {doc}")
        print(f"🏷️  Metadata: {results['metadatas'][0][i]}")
        print(f"📏 Distance: {results['distances'][0][i]:.4f}")
        print("-" * 50)

# Function to get embedding for query
def get_query_embedding(text):
    return openai.embeddings.create(input=text, model=EMBEDDING_MODEL).data[0].embedding

# Query 1: Public documents
results_public = collection.query(
    query_embeddings=[get_query_embedding("What are the chatbot's new features?")],
    n_results=3,
    where={"access": "public"}
)
print_results("Query: Only Public Documents", results_public)

# Query 2: Confidential documents
results_conf = collection.query(
    query_embeddings=[get_query_embedding("What internal issues exist with the chatbot?")],
    n_results=3,
    where={"access": "confidential"}
)
print_results("Query: Only Confidential Documents", results_conf)

# Query 3: All documents
results_all = collection.query(
    query_embeddings=[get_query_embedding("Tell me about the project.")],
    n_results=5,
    where={"access": {"$in": ["public", "confidential"]}}
)
print_results("Query: All Documents", results_all)

# Function to perform RAG using OpenAI GPT-4
def query_rag(question, access_levels=None, n_results=5):
    query_embedding = get_query_embedding(question)
    where_filter = {}
    if access_levels:
        where_filter = {"access": {"$in": access_levels}} if isinstance(access_levels, list) else {"access": access_levels}

    results = collection.query(query_embeddings=[query_embedding], n_results=n_results, where=where_filter)
    context = "\n\n".join(results.get("documents", [[]])[0])
    prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}
"""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Example usage
answer = query_rag("What are the chatbot's new features?", access_levels=["public"])
print(f"\n=== GPT-4 Response ===\n{answer}")

