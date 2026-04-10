"""
Exercise 2: Retrieve and search stored memories.

Connects to the same Qdrant instance and retrieves the memories that
mem_01.py stored for user "alice".  Also demonstrates semantic search:
even if you never said the word "genre", Mem0 can find the relevant
memory.

Run mem_01.py first, then:
    python3 mem_02.py
"""

from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0",
        },
    },
    "llm": {
        "provider": "openai_structured",
        "config": {"model": "gpt-4o-2024-08-06", "temperature": 0.0},
    },
}

m = Memory.from_config(config)

# --- Retrieve all memories ---
all_memories = m.get_all(user_id="alice")
print("All memories for alice:")
print("-" * 50)
for memory in all_memories.get("results", []):
    print(f"  - {memory['memory']}")

# --- Semantic search ---
print("\nSearch: 'What kind of movies does she like?'")
print("-" * 50)
results = m.search("What kind of movies does she like?", user_id="alice")
items = results if isinstance(results, list) else results.get("results", [])
for item in items:
    print(f"  - {item['memory']}")
