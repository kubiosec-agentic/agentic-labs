"""
Exercise 1: Basic memory operations with Qdrant.

Adds a short conversation about movie preferences for user "alice",
then retrieves all stored memories.  Run mem_02.py next to see how
retrieval works in a separate script.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
        -v $PWD/qdrant_storage:/qdrant/storage qdrant/qdrant:latest

Run:
    python3 mem_01.py
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

# A sample conversation that Mem0 will distill into memories
messages = [
    {"role": "user", "content": "I'm planning to watch a movie tonight. Any recommendations?"},
    {"role": "assistant", "content": "How about a thriller? They can be quite engaging."},
    {"role": "user", "content": "I'm not a big fan of thrillers but I love sci-fi movies."},
    {"role": "assistant", "content": "Got it! I'll suggest sci-fi movies in the future."},
]

print("Adding conversation to memory for user 'alice'...")
m.add(messages, user_id="alice", metadata={"category": "movies"})

# Retrieve what Mem0 extracted
all_memories = m.get_all(filters={"user_id": "alice"})
print("\nMemories for alice:")
print("-" * 50)
for memory in all_memories.get("results", []):
    print(f"  - {memory['memory']}")
