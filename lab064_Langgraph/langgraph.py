"""
Clean LangGraph Agent with Real Tools
Simple example using DuckDuckGo search and Python eval for calculations.
"""

import os
import math
from typing import Dict, List

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END

# Try to import search functionality
from ddgs import DDGS


# Initialize search
search_engine = DDGS()

def search_web(query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = list(search_engine.text(query, max_results=3))
        if results:
            formatted = []
            for r in results:
                formatted.append(f"Title: {r.get('title', 'N/A')}\nContent: {r.get('body', 'N/A')}")
            return "\n\n".join(formatted)
        return "No results found"
    except Exception as e:
        return f"Search failed: {e}"

def calculate(expression: str) -> str:
    """Safely evaluate mathematical expressions."""
    try:
        # Allow only safe mathematical operations
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"

# Tool definitions for OpenAI function calling
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information and facts",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
                },
                "required": ["expression"]
            }
        }
    }
]

# System prompt
system_prompt = """You are a helpful assistant with access to web search and calculation tools.

For mathematical calculations, use the calculate tool.
For current information, use the search_web tool.

Always search for current information before making calculations with that data."""

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

# Bind tools to LLM
llm_with_tools = prompt | llm.bind_tools(tools_schema)


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
            result = search_web(args["query"])
        elif tool_name == "calculate":
            result = calculate(args["expression"])
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
    
    return workflow.compile()


def main():
    """Run the agent with a test question."""
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
