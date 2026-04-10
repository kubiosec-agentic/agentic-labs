"""
Verify that ChromaDB persistent storage works.

Run rag_metadata_04.py first to populate the database, then run this
script in a separate process. If the data survived, persistence works.

    python3 rag_metadata_04.py       # populate
    python3 verify_persistence.py    # verify (separate process)

The key thing to observe: this script never calls add(). It only reads
data that was written by rag_metadata_04.py in a previous process.
If you see documents, the HNSW index and metadata were persisted to
disk and reloaded successfully.

Run:
    python3 verify_persistence.py
"""

import os
import chromadb

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(CURRENT_DIR, "chroma_storage")

print(f"ChromaDB version: {chromadb.__version__}")
print(f"Persistence directory: {PERSIST_DIR}")

if not os.path.exists(PERSIST_DIR):
    print("\nStorage directory does not exist. Run rag_metadata_04.py first.")
    exit(1)

# Connect to the existing persistent storage
client = chromadb.PersistentClient(path=PERSIST_DIR)

# Access the collection (do NOT use get_or_create: we want to fail
# if it does not exist, because that means persistence is broken)
try:
    collection = client.get_collection(name="my_docs")
except Exception as e:
    print(f"\nCollection 'my_docs' not found: {e}")
    print("Run rag_metadata_04.py first to create it.")
    exit(1)

doc_count = collection.count()
print(f"\nFound {doc_count} documents in persistent storage.")

if doc_count > 0:
    results = collection.get(include=["documents", "metadatas"], limit=5)
    print("\nSample documents:")
    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        print(f"  [{doc_id}] ({meta['access']}) {doc[:70]}...")
    print(f"\nPersistence verified: {doc_count} documents survived between processes.")
else:
    print("Collection is empty. Something went wrong with rag_metadata_04.py.")
