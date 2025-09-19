![LangGraph](https://img.shields.io/badge/LangGraph-blue) ![StateGraph](https://img.shields.io/badge/StateGraph-green) ![Workflows](https://img.shields.io/badge/Workflows-orange)
# LAB064: LangGraph - Stateful Workflow Orchestration
This lab demonstrates how to build stateful, multi-step workflows and intelligent agents using LangGraph.<br>

**LangGraph** is a powerful framework for creating stateful, graph-based workflows that can handle complex decision-making, conditional routing, and multi-agent coordination. It builds on top of LangChain to provide:

- **Stateful Graphs:** Maintain state across multiple steps and nodes
- **Conditional Routing:** Dynamic workflow paths based on runtime conditions  
- **Agent Orchestration:** Coordinate multiple LLMs and tools in complex workflows
- **Memory Management:** Persistent state and conversation history
- **Tool Integration:** Seamlessly integrate external APIs and functions

With LangGraph, you can build sophisticated AI systems that go beyond simple request-response patterns to create intelligent, adaptive workflows.

## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
export ANTHROPIC_API_KEY="xxxxxxxxx" 
export GOOGLE_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab064/bin/activate
```
## Lab instructions

#### Basic LangGraph Workflow (LG_01)
Introduction to StateGraph with simple nodes and edges:
```
python3 ./LG_01.py
```

#### Agent with Tools (LG_02)  
Demonstrates agent creation with web search and calculation tools:
```
python3 ./LG_02.py
```

#### Graph Visualization (LG_03)
Shows how to visualize and save workflow graphs:
```
python3 ./LG_03.py
```

#### LangGraph Fundamentals (LG_04)
Comprehensive examples covering state management, reducers, and configuration:
```
python3 ./LG_04.py
```

## Key Concepts Demonstrated

### State Management
- **Default Reducers:** Simple value replacement
- **Add Reducers:** List accumulation across nodes
- **Custom Reducers:** Flexible state handling for complex data types

### Workflow Patterns
- **Linear Workflows:** Sequential node execution
- **Conditional Routing:** Dynamic paths based on state conditions
- **Parallel Execution:** Concurrent node processing
- **Loops and Cycles:** Iterative workflows with feedback

### Agent Architecture
- **Tool Integration:** Web search, calculations, external APIs
- **Multi-Agent Coordination:** Multiple LLMs working together
- **Human-in-the-Loop:** Interactive decision points
- **Memory and Context:** Persistent conversation state

### Visualization and Debugging
- **Mermaid Diagrams:** Visual workflow representation
- **Streaming Execution:** Real-time workflow monitoring
- **State Inspection:** Debug state changes across nodes

## Advanced Features

### Configuration Management
Runtime customization of models, tools, and parameters:
```python
config = {"configurable": {"model_provider": "OpenAI", "model_name": "gpt-4o"}}
result = graph.invoke(input_data, config=config)
```

### Streaming and Real-time Updates
Monitor workflow execution in real-time:
```python
async for chunk in graph.astream(input_data, stream_mode="values"):
    print(f"Update: {chunk}")
```

### Error Handling and Recovery
Built-in error handling with retry and fallback mechanisms.

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
