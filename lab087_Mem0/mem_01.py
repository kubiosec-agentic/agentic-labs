import os, pprint
from mem0 import Memory


# config = {
#     "vector_store": {
#         "provider": "qdrant",
#         "config": {
#             "collection_name": "mem0",                # pick a stable name
#             "path": "/Users/xxradar/.mem0/qdrant",    # your desired folder
#             "on_disk": True                           # persist between runs
#         }
#     },
#     "llm": {"provider": "openai_structured",
#             "config": {"model": "gpt-4o-2024-08-06", "temperature": 0.0}}
# }

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            # either host/port:
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0",
            # if you set an API key in Docker env:
            # "api_key": "super-secret",
        }
    },
    "llm": {
        "provider": "openai_structured",
        "config": {"model": "gpt-4o-2024-08-06", "temperature": 0.0}
    }
}

m = Memory.from_config(config)

messages = [
    {"role": "user", "content": "I'm planning to watch a movie tonight. Any recommendations?"},
    {"role": "assistant", "content": "How about a thriller movies? They can be quite engaging."},
    {"role": "user", "content": "I’m not a big fan of thriller movies but I love sci-fi movies."},
    {"role": "assistant", "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future."}
]
m.add(messages, user_id="alice", metadata={"category": "movies"})


print("HOME:", os.path.expanduser("~"))
pprint.pprint(m.__dict__.get("config", {}))  # shows vector_store, history path if present


all_memories = m.get_all(user_id="alice")
print(all_memories)
