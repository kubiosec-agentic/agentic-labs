"""
Exercise 5: Collaborative memory across multiple agents/actors.

Multiple participants (Alice, Bob, and an AI assistant) share a single
memory scope identified by a run_id.  Each participant can add
messages and search the shared context.  The assistant can brainstorm
using the combined knowledge of all participants.

This pattern is useful for multi-agent collaboration, meeting
summarization, or shared project context.

Run:
    python3 mem_05.py
"""

from openai import OpenAI
from mem0 import Memory
from collections import defaultdict
from datetime import datetime

# Shared project context: all participants use the same run_id
RUN_ID = "project-demo"

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0_collab",
        },
    },
    "llm": {
        "provider": "openai_structured",
        "config": {"model": "gpt-4o-2024-08-06", "temperature": 0.0},
    },
}

mem = Memory.from_config(config)


class CollaborativeAgent:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.mem = mem

    def add_message(self, role: str, name: str, content: str):
        """Store a message from any participant."""
        msg = {"role": role, "name": name, "content": content}
        self.mem.add([msg], run_id=self.run_id, infer=False)

    def brainstorm(self, prompt: str) -> str:
        """Use shared context to generate a response."""
        memories = self.mem.search(prompt, filters={"run_id": self.run_id}, limit=5)
        items = memories if isinstance(memories, list) else memories.get("results", [])
        context = "\n".join(
            f"- {m['memory']} (by {m.get('actor_id', 'Unknown')})" for m in items
        )

        client = OpenAI()
        reply = (
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful project assistant."},
                    {"role": "user", "content": f"Prompt: {prompt}\nContext:\n{context}"},
                ],
            )
            .choices[0]
            .message.content.strip()
        )
        self.add_message("assistant", "assistant", reply)
        return reply

    def get_all_messages(self):
        res = self.mem.get_all(filters={"run_id": self.run_id})
        return res if isinstance(res, list) else res.get("results", [])

    def print_grouped_by_actor(self):
        messages = self.get_all_messages()
        grouped = defaultdict(list)
        for m in messages:
            grouped[m.get("actor_id") or "Unknown"].append(m)
        print("\n--- Messages grouped by actor ---")
        for actor, mems in grouped.items():
            print(f"\n=== {actor} ===")
            for m in mems:
                print(f"  {m['memory']}")


def main():
    agent = CollaborativeAgent(RUN_ID)

    # Simulate a multi-participant conversation
    print("Adding messages from Alice and Bob...\n")
    agent.add_message("user", "alice", "We should use FastAPI for the backend.")
    agent.add_message("user", "bob", "I think we also need a Redis cache for sessions.")
    agent.add_message("user", "alice", "Good idea. Let's also add rate limiting.")

    # The assistant brainstorms using shared context
    print("Assistant brainstorming...\n")
    reply = agent.brainstorm("Summarize the project decisions so far and suggest next steps.")
    print(f"Assistant: {reply}\n")

    # Show all messages grouped by participant
    agent.print_grouped_by_actor()


if __name__ == "__main__":
    main()
