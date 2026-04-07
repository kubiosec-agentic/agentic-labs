"""
RAG with OpenAI's managed vector store and Responses API.
Self-contained: creates a vector store, uploads a file, waits for indexing,
queries with file_search, and cleans up. No curl commands needed.
"""
import time
from openai import OpenAI

client = OpenAI()

DATA_FILE = "data/llms-full.txt"

# ------------------------------------------------------------------
# 1. Create a managed vector store
# ------------------------------------------------------------------
print("[1/5] Creating vector store ...")
vs = client.vector_stores.create(name="lab040_mcp_docs")
print(f"      Vector store ID: {vs.id}")

# ------------------------------------------------------------------
# 2. Upload the file
# ------------------------------------------------------------------
print(f"[2/5] Uploading {DATA_FILE} ...")
with open(DATA_FILE, "rb") as f:
    uploaded = client.files.create(file=f, purpose="assistants")
print(f"      File ID: {uploaded.id}")

# ------------------------------------------------------------------
# 3. Link the file to the vector store and wait for indexing
# ------------------------------------------------------------------
print("[3/5] Indexing (this may take a few seconds) ...")
client.vector_stores.files.create(vector_store_id=vs.id, file_id=uploaded.id)

# Poll until the file is indexed
for _ in range(30):
    vs_file = client.vector_stores.files.retrieve(vector_store_id=vs.id, file_id=uploaded.id)
    if vs_file.status == "completed":
        break
    time.sleep(1)
else:
    print("      Warning: indexing did not complete within 30 seconds")

print(f"      Status: {vs_file.status}")

# ------------------------------------------------------------------
# 4. Query with file_search via the Responses API
# ------------------------------------------------------------------
query = "What are the differentiating features of MCP?"
print(f"[4/5] Querying: {query}")

response = client.responses.create(
    model="gpt-4o",
    input=query,
    tools=[{
        "type": "file_search",
        "vector_store_ids": [vs.id],
    }],
)

print("\n" + "=" * 60)
print("ANSWER:")
print("=" * 60)
print(response.output_text)

# ------------------------------------------------------------------
# 5. Cleanup: delete vector store and uploaded file
# ------------------------------------------------------------------
print(f"\n[5/5] Cleaning up ...")
client.vector_stores.delete(vector_store_id=vs.id)
client.files.delete(file_id=uploaded.id)
print("      Done. Vector store and file deleted.")
