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

#### Job Application Review System (LG_04)
Advanced workflow demonstrating AI-powered job application processing with conditional routing and state management:
```
python3 ./LG_04.py
```

**LG_05.py** showcases a sophisticated real-world application of LangGraph for automating job application reviews. This example demonstrates:

- **Multi-Node Workflow:** Complex pipeline with analysis, generation, and review phases
- **Conditional Routing:** Smart decision-making based on candidate suitability assessment
- **State Management:** Comprehensive state tracking with action logging using `add` reducers
- **LLM Integration:** Multiple OpenAI model calls for different specialized tasks
- **Error Handling:** Robust fallback mechanisms for offline or API failure scenarios
- **TypedDict States:** Strongly-typed state definitions for better code reliability

**Key Features:**
- 🔍 **Job Requirement Analysis:** AI-powered matching of candidate experience to job requirements
- ✍️ **Automated Letter Generation:** Personalized application letters based on candidate profile and job description
- 📊 **Application Scoring:** Intelligent review system with numerical scoring (1-10) and detailed feedback
- 🔀 **Smart Routing:** Conditional workflow that either processes suitable candidates or handles rejections
- 📈 **Action Tracking:** Complete audit trail of all workflow steps and decisions
- 🛡️ **Fallback Logic:** Graceful degradation with template responses when AI services are unavailable

**Workflow Steps:**
1. **analyze_job:** Evaluates candidate fit against job requirements
2. **Conditional Router:** Routes to application generation or rejection based on suitability
3. **generate_application:** Creates personalized cover letters for suitable candidates
4. **review_application:** Scores and provides feedback on generated applications
5. **reject_application:** Handles unsuitable candidates with appropriate messaging

**Demo Scenarios:**
The demo processes three different candidate profiles against a software engineering job posting:
- **Alice Johnson:** Highly qualified Python/Django expert (Expected: High score)
- **Bob Smith:** Java developer with limited Python experience (Expected: Lower score/rejection)
- **Carol Chen:** Well-matched Python/FastAPI specialist (Expected: High score)

This example perfectly illustrates how LangGraph can orchestrate complex business workflows that require multiple AI decisions, state persistence, and conditional logic - making it ideal for enterprise automation scenarios.

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
