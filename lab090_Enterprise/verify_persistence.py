import os
import chromadb
from chromadb.config import Settings

# Print ChromaDB version
print(f"ChromaDB version: {chromadb.__version__}")

# Use the same absolute path for consistency
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(CURRENT_DIR, "chroma_storage")
print(f"Using persistence directory: {PERSIST_DIR}")

# Create a persistent client
try:
    # Try the newer API format if available
    client = chromadb.PersistentClient(path=PERSIST_DIR)
except AttributeError:
    # Fall back to the older API
    client = chromadb.Client(Settings(persist_directory=PERSIST_DIR))

# Access the existing collection
collection = client.get_collection(name="my_docs")

# Count the documents
doc_count = collection.count()
print(f"Found {doc_count} documents in the persistent storage")

# Retrieve a few documents to verify contents
if doc_count > 0:
    results = collection.get(
        include=["documents", "metadatas"],
        limit=3
    )
    print("\nSample documents from persistent storage:")
    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        print(f"ID: {doc_id}")
        print(f"Document: {doc}")
        print(f"Metadata: {meta}")
        print("-" * 50)
