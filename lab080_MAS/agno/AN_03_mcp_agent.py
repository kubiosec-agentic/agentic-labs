"""
Exercise 3: Agno agent with MCP tool and persistent history.

Connects to the Agno documentation MCP server so the agent can
search and answer questions about the Agno framework. Chat history
is stored in a local SQLite database.

The AgentOS wrapper exposes the agent as a FastAPI app that can be
served with `uvicorn` or used in the Agno playground.

Prerequisites:
    export OPENAI_API_KEY="sk-..."

Run (interactive):
    python3 AN_03_mcp_agent.py

Run (as API server):
    uvicorn AN_03_mcp_agent:app --reload --port 8501
"""

import asyncio
import os
import sys

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.mcp import MCPTools

# --- Agent definition ---
agno_assist = Agent(
    name="Agno Assist",
    model=OpenAIChat(id="gpt-4o"),
    db=SqliteDb(db_file="tmp/agno.db"),
    tools=[MCPTools(url="https://docs.agno.com/mcp")],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
    instructions=(
        "You are a helpful assistant that answers questions about "
        "the Agno framework. Use the MCP tool to search the Agno "
        "documentation before answering."
    ),
)

# --- AgentOS exposes the agent as a FastAPI app ---
agent_os = AgentOS(agents=[agno_assist])
app = agent_os.get_app()

# --- Interactive mode when run directly ---
if __name__ == "__main__":
    agno_assist.print_response(
        "How do I create a multi-agent team in Agno?",
        stream=True,
    )
    print()
    agno_assist.print_response(
        "Show me an example with tool use.",
        stream=True,
    )
