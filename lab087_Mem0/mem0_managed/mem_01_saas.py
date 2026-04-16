"""
Exercise S1: Basic memory operations with Mem0 SaaS.

Uses MemoryClient (managed service) instead of a local Qdrant
instance.  No Docker required; you only need a MEM0_API_KEY from
https://app.mem0.ai.

Run:
    export MEM0_API_KEY="your_key"
    python3 mem0_managed/mem_01_saas.py
"""

import time
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

# The SaaS backend processes memories asynchronously.
# Give it a few seconds before searching.
print("\nWaiting for memories to be processed...")
time.sleep(5)

# --- Search with filters ---
print("\n--- Search: what does alex like? ---")
search_results = client.search(
    query="What do I like?", version="v2", filters={"user_id": "alex"}, top_k=2
)

# Handle both possible response formats (list of dicts or list of strings)
if isinstance(search_results, list):
    for r in search_results:
        if isinstance(r, dict):
            print(f"  - {r.get('memory', r)}")
        else:
            print(f"  - {r}")
elif isinstance(search_results, dict):
    for r in search_results.get("results", []):
        print(f"  - {r.get('memory', r) if isinstance(r, dict) else r}")
else:
    print("  (no results)")

# --- Retrieve all memories ---
print("\n--- All memories for alex ---")
all_memories = client.get_all(version="v2", filters={"user_id": "alex"}, page=1, page_size=50)

if isinstance(all_memories, dict):
    for memory in all_memories.get("results", []):
        if isinstance(memory, dict):
            print(f"  - {memory.get('memory', memory)}")
        else:
            print(f"  - {memory}")
elif isinstance(all_memories, list):
    for memory in all_memories:
        if isinstance(memory, dict):
            print(f"  - {memory.get('memory', memory)}")
        else:
            print(f"  - {memory}")
