import os, pprint
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0",
        }
    },
    "llm": {
        "provider": "openai_structured",
        "config": {"model": "gpt-4o-2024-08-06", "temperature": 0.0}
    }
}

m = Memory.from_config(config)

print("HOME:", os.path.expanduser("~"))
pprint.pprint(m.__dict__.get("config", {}))  


all_memories = m.get_all(user_id="alice")
print("\nMemories for alice:")
print("-" * 50)
for memory in all_memories.get('results', []):
    print(f"• {memory['memory']}")
