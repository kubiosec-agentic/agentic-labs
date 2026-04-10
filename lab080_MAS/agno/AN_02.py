"""
Exercise 2: Agno agent with chat history.

Demonstrates multi-turn conversation with history stored in a local
SQLite database. The agent remembers previous messages and can refer
back to them.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from rich.pretty import pprint

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    # Store session history in a local SQLite file.
    db=SqliteDb(db_file="tmp/agent.db"),
    # Add the previous chat history to the context sent to the model.
    add_history_to_context=True,
    # Number of historical runs to include in the context.
    num_history_runs=3,
    description="You are a helpful assistant that always responds in a polite, upbeat and positive manner.",
)

# --- First message ---
agent.print_response("Share a 2 sentence horror story", stream=True)

# Print the messages stored in the session
pprint(
    [
        m.model_dump(include={"role", "content"})
        for m in agent.get_messages_for_session()
    ]
)

# --- Follow-up that relies on history ---
agent.print_response("What was my first message?", stream=True)

# Print updated session messages
pprint(
    [
        m.model_dump(include={"role", "content"})
        for m in agent.get_messages_for_session()
    ]
)
