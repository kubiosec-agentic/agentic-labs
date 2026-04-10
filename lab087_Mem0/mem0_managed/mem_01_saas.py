"""
Exercise S1: Basic memory operations with Mem0 SaaS.

Uses MemoryClient (managed service) instead of a local Qdrant
instance.  No Docker required; you only need a MEM0_API_KEY from
https://app.mem0.ai.

Run:
    export MEM0_API_KEY="your_key"
    python3 mem0_managed/mem_01_saas.py
"""

import warnings
from mem0 import MemoryClient

warnings.filterwarnings("ignore", category=DeprecationWarning, module="mem0")

client = MemoryClient()

# --- Add memories ---
messages = [
    {"role": "user", "content": "Thinking of making a sandwich. What do you recommend?"},
    {"role": "assistant", "content": "How about adding some cheese for extra flavor?"},
    {"role": "user", "content": "Actually, I don't like cheese."},
    {"role": "assistant", "content": "I'll remember that for future recommendations."},
    {"role": "user", "content": "Actually, I don't like salami either."},
    {"role": "user", "content": "I love Python."},
    {"role": "user", "content": "I love AI."},
]

print("Adding conversation for user 'alex'...")
result = client.add(messages, user_id="alex")
print("Add result:", result)

# --- Search with filters ---
print("\n--- Search: technology-related memories ---")
filters = {
    "AND": [
        {"user_id": "alex"},
        {"categories": {"contains": "technology"}},
    ]
}
search_results = client.search(query="What do I like?", version="v2", filters=filters, top_k=2)
for r in search_results:
    print(f"  - {r['memory']}")

# --- Retrieve all memories ---
print("\n--- All memories for alex ---")
filters = {"AND": [{"user_id": "alex"}]}
all_memories = client.get_all(version="v2", filters=filters, page=1, page_size=50)
for memory in all_memories.get("results", []):
    print(f"  - {memory['memory']}")
