import os
import warnings
from mem0 import MemoryClient

# Suppress the deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="mem0")

# os.environ["MEM0_API_KEY"] = "xxxxxx"

client = MemoryClient()

messages = [
    {"role": "user", "content": "Thinking of making a sandwich. What do you recommend?"},
    {"role": "assistant", "content": "How about adding some cheese for extra flavor?"},
    {"role": "user", "content": "Actually, I don't like cheese."},
    {"role": "assistant", "content": "I'll remember that you don't like cheese for future recommendations."},
    {"role": "user", "content": "Actually, I don't like salami neither."},
    {"role": "user", "content": "I love Python"},
    {"role": "user", "content": "I love AI"},


]

result = client.add(messages, user_id="alex")
print("Add result:", result)



print("----------------SEARCH RESULTS-----------------------------")

query = "What do I like?"
filters = {
    "AND": [
        {
            "user_id": "alex",
        },
        {
            "categories": {"contains": "technology"}
        }
    ]
}

search_results = client.search(
    query=query, 
    version="v2", 
    filters=filters,
    top_k=2
)

print("Search results:", search_results)
print("---------------------------------------------")
for result in search_results:
    print(result['memory'])
print("---------------------------------------------")














print("-------------------ALL MEMORIES--------------------------")

filters = {
   "AND": [
      {
         "user_id": "alex"
      }
   ]
}

all_memories = client.get_all(version="v2", filters=filters, page=1, page_size=50)
print("All memories:", all_memories)
print("---------------------------------------------")
for memory in all_memories['results']:
    print(memory['memory'])
print("---------------------------------------------")