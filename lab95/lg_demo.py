"""
LangGraph Demo: Agent with Tools
This module demonstrates how to create an agent using LangGraph with custom tools
for search and calculation functionality.
"""

# Standard library imports
import math
import os
from typing import Dict, List

# Third-party imports
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import create_react_agent

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass


# Mock tool functions
def mocked_google_search(query: str) -> str:
    """Mock Google search function for demonstration purposes."""
    print(f"CALLED GOOGLE_SEARCH with query={query}")
    return "Donald Trump is a president of USA and he's 78 years old"


def mocked_calculator(expression: str) -> float:
    """Mock calculator function for demonstration purposes."""
    print(f"CALLED CALCULATOR with expression={expression}")
    if "sqrt" in expression:
        return math.sqrt(78 * 132)
    return 78 * 132


# Tool definitions
calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Computes mathematical expressions",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "title": "expression",
                    "description": "A mathematical expression to be evaluated by a calculator"
                }
            },
            "required": ["expression"]
        }
    }
}

search_tool = {
    "type": "function",
    "function": {
        "name": "google_search",
        "description": "Returns about common facts, fresh events and news from Google Search engine based on a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "title": "search_query",
                    "description": "Search query to be sent to the search engine"
                }
            },
            "required": ["query"]
        }
    }
}

# System configuration
system_prompt = (
    "Always use a calculator for mathematical computations, and use Google Search "
    "for information about common facts, fresh events and news. Do not assume anything, keep in "
    "mind that things are changing and always "
    "check yourself with external sources if possible."
)

# LLM setup with environment variable support
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0")),
    api_key=os.getenv("OPENAI_API_KEY")  # This will be None if not set, which is fine for testing
)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

# LLM with tools binding
llm_with_tools = prompt | llm.bind_tools([search_tool, calculator_tool])


# Graph node functions
def invoke_llm(state: MessagesState) -> Dict[str, List]:
    """Invoke the LLM with the current state."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def call_tools(state: MessagesState) -> Dict[str, List]:
    """Execute the tools called by the LLM."""
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    new_messages = []

    for tool_call in tool_calls:
        if tool_call["name"] == "google_search":
            tool_result = mocked_google_search(**tool_call["args"])
            new_messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
        elif tool_call["name"] == "calculator":
            tool_result = mocked_calculator(**tool_call["args"])
            new_messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
        else:
            raise ValueError(f"Tool {tool_call['name']} is not defined!")
    
    return {"messages": new_messages}


def should_run_tools(state: MessagesState) -> str:
    """Determine whether to run tools or end the conversation."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tools"
    return END


# Graph construction
def create_agent_graph() -> StateGraph:
    """Create and compile the agent graph."""
    builder = StateGraph(MessagesState)
    builder.add_node("invoke_llm", invoke_llm)
    builder.add_node("call_tools", call_tools)

    builder.add_edge(START, "invoke_llm")
    builder.add_conditional_edges("invoke_llm", should_run_tools)
    builder.add_edge("call_tools", "invoke_llm")
    
    return builder.compile()


def main():
    """Main function to demonstrate the agent."""
    # Create the graph
    graph = create_agent_graph()
    
    # Test question
    question = "What is a square root of the current US president's age multiplied by 132?"
    
    # Run the graph
    result = graph.invoke({"messages": [HumanMessage(content=question)]})
    print("Custom Graph Result:")
    print(result["messages"][-1].content)
    
    # Alternative: Using the prebuilt ReAct agent
    print("\n" + "="*50)
    print("Prebuilt ReAct Agent:")
    agent = create_react_agent(model=llm, tools=[search_tool, calculator_tool], prompt=system_prompt)
    
    # Note: The prebuilt agent would be used similarly but with different invocation
    print("Prebuilt agent created successfully")


if __name__ == "__main__":
    main()
