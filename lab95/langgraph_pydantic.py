"""
Clean LangGraph Agent with Real Tools (Pydantic + LangGraph Compatible)
"""

import os
import math
from typing import Dict, List

from pydantic import BaseModel
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END

from ddgs import DDGS  # DuckDuckGo search wrapper

# Initialize search engine
search_engine = DDGS()

# ==========================
# Define Tools (Pydantic)
# ==========================

class SearchWebInput(BaseModel):
    query: str

@tool("search_web", args_schema=SearchWebInput)
def search_web(query: str) -> str:
    """Search the web for current information and facts."""
    try:
        results = list(search_engine.text(query, max_results=3))
        if results:
            return "\n\n".join(
                f"Title: {r.get('title', 'N/A')}\nContent: {r.get('body', 'N/A')}" for r in results
            )
        return "No results found"
    except Exception as e:
        return f"Search failed: {e}"


class CalculateInput(BaseModel):
    expression: str

@tool("calculate", args_schema=CalculateInput)
def calculate(expression: str) -> str:
    """Perform mathematical calculations."""
    try:
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


# ==========================
# System Prompt + LLM
# ==========================

system_prompt = """You are a helpful assistant with access to web search and calculation tools.

For mathematical calculations, use the calculate tool.
For current information, use the search_web tool.

Always search for current information before making calculations with that data."""

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

llm_with_tools = prompt | llm.bind_tools([search_web, calculate])

# Registry for dispatch
tool_registry = {
    "search_web": search_web,
    "calculate": calculate,
}

# ==========================
# LangGraph Node Functions
# ==========================

def invoke_llm(state: MessagesState) -> Dict[str, List]:
    """Call the LLM with current messages."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def call_tools(state: MessagesState) -> Dict[str, List]:
    """Execute the tools requested by the LLM."""
    last_message = state["messages"][-1]
    new_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        args = tool_call["args"]

        print(f"🔧 Calling {tool_name} with args: {args}")

        tool = tool_registry.get(tool_name)
        if tool:
            result = tool.invoke(args)
        else:
            result = f"Unknown tool: {tool_name}"

        new_messages.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )

    return {"messages": new_messages}


def should_continue(state: MessagesState) -> str:
    """Decide whether to continue with tools or end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ==========================
# Build LangGraph Agent
# ==========================

def create_agent():
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", invoke_llm)
    workflow.add_node("tools", call_tools)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    return workflow.compile()


# ==========================
# Run it!
# ==========================

def main():
    agent = create_agent()
    question = "What is the current US president's age multiplied by 2 and then square rooted? we are in the year 2025"
    print(f"Question: {question}\n")

    result = agent.invoke({
        "messages": [HumanMessage(content=question)]
    })

    print(f"\n{'='*60}")
    print("Final Answer:")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
