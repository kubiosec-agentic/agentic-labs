"""
Clean LangGraph Agent with Real Tools (Refactored with @tool decorators)
Simple example using DuckDuckGo search and Python eval for calculations.
"""

import os
import math
from typing import Dict, List

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END

from ddgs import DDGS


# Initialize DuckDuckGo search
search_engine = DDGS()


@tool
def search_web(query: str) -> str:
    """Search the web for current information and facts."""
    try:
        results = list(search_engine.text(query, max_results=3))
        if results:
            return "\n\n".join(
                f"Title: {r.get('title', 'N/A')}\nContent: {r.get('body', 'N/A')}"
                for r in results
            )
        return "No results found"
    except Exception as e:
        return f"Search failed: {e}"


@tool
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


# System prompt
system_prompt = """You are a helpful assistant with access to web search and calculation tools.

For mathematical calculations, use the calculate tool.
For current information, use the search_web tool.

Always search for current information before making calculations with that data.
"""


# LLM setup
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

# Bind tools using decorated functions (schema auto-extracted)
llm_with_tools = prompt | llm.bind_tools([search_web, calculate])


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

        if tool_name == "search_web":
            result = search_web.invoke(args)
        elif tool_name == "calculate":
            result = calculate.invoke(args)
        else:
            result = f"Unknown tool: {tool_name}"

        new_messages.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )

    return {"messages": new_messages}


def should_continue(state: MessagesState) -> str:
    """Decide whether to continue with tools or end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END


def create_agent():
    """Create the LangGraph agent."""
    workflow = StateGraph(MessagesState)

    # Add nodes
    workflow.add_node("agent", invoke_llm)
    workflow.add_node("tools", call_tools)

    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile(), workflow




def main():
    """Run the agent with a test question."""
    agent, workflow = create_agent()

    question = "How many people live in France? How many live in Belgium? What is the difference?"

    print(f"Question: {question}\n")

    result = agent.invoke({
        "messages": [HumanMessage(content=question)]
    })

    print(f"\n{'='*60}")
    print("Final Answer:")
    print(result["messages"][-1].content)

    # Save the graph as Mermaid diagram
    try:
        graph_data = agent.get_graph()
        mermaid_code = graph_data.draw_mermaid()
        
        # Save Mermaid diagram to file
        with open("graph.mermaid", "w") as f:
            f.write(mermaid_code)
        print("Graph saved as Mermaid diagram: graph.mermaid")
        
        # Also print the diagram to console
        print("\nMermaid diagram:")
        print(mermaid_code)
        
    except Exception as e:
        print(f"Could not generate Mermaid diagram: {e}")
        # Fallback to ASCII representation
        try:
            print("\nGraph structure (ASCII):")
            graph_data.print_ascii()
        except Exception as e2:
            print(f"Could not print ASCII graph: {e2}")

if __name__ == "__main__":
    main()
