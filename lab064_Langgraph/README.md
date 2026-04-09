![LangGraph](https://img.shields.io/badge/LangGraph-blue) ![Python](https://img.shields.io/badge/Python-blue) ![StateGraph](https://img.shields.io/badge/StateGraph-green) ![Workflows](https://img.shields.io/badge/Workflows-orange)

# LAB064: LangGraph - Stateful Workflow Orchestration

## Introduction
This lab demonstrates how to build stateful, multi-step workflows and intelligent agents using LangGraph. LangGraph is a powerful framework for creating stateful, graph-based workflows that can handle complex decision-making, conditional routing, and multi-agent coordination. It builds on top of LangChain to provide stateful graphs, conditional routing, agent orchestration, memory management, and tool integration. With LangGraph, you can build sophisticated AI systems that go beyond simple request-response patterns to create intelligent, adaptive workflows.

## Set up your environment

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
export ANTHROPIC_API_KEY="xxxxxxxxx"
export GOOGLE_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab064/bin/activate
```
## Lab instructions

#### Example 1: Basic LangGraph Workflow
Introduction to StateGraph with simple nodes and edges:
```bash
python3 ./LG_01.py
```

#### Example 2: Agent with Tools
Demonstrates agent creation with web search and calculation tools:
```bash
python3 ./LG_02.py
```

#### Example 3: Graph Visualization
Shows how to visualize and save workflow graphs:
```bash
python3 ./LG_03.py
```

#### Example 4: Job Application Review System
Advanced workflow demonstrating AI-powered job application processing with conditional routing and state management:
```bash
python3 ./LG_04.py
```

#### Example 5: CTF - Attacking and Hardening a Vulnerable Agent
A staged security exercise built on the LangGraph pattern. A deliberately-weak agent with a Python code execution tool is exposed as an OpenAI-compatible `/v1/chat/completions` endpoint with multi-turn sessions (server-side via `MemorySaver`). You attack the same agent four times, each time against a stronger set of defenses: no guardrails, regex output filter, hardened system prompt, and `RestrictedPython` sandbox. Each layer has a bypass, and the point is to internalize the attack and defense patterns.

```bash
cd ctf
python3 stage1_no_guardrails.py   # then stage2, stage3, stage4
```

See [ctf/README.md](./ctf/README.md) for the full walkthrough and discussion questions.

#### Example 6: Job Application Review Workflow
This example showcases a sophisticated real-world application of LangGraph for automating job application reviews with:

- **Multi-Node Workflow:** Complex pipeline with analysis, generation, and review phases
- **Conditional Routing:** Smart decision-making based on candidate suitability assessment
- **State Management:** Comprehensive state tracking with action logging using `add` reducers
- **LLM Integration:** Multiple OpenAI model calls for different specialized tasks
- **Error Handling:** Robust fallback mechanisms for offline or API failure scenarios
- **TypedDict States:** Strongly-typed state definitions for better code reliability

**Key Features:**
- **Job Requirement Analysis:** AI-powered matching of candidate experience to job requirements
- **Automated Letter Generation:** Personalized application letters based on candidate profile and job description
- **Application Scoring:** Intelligent review system with numerical scoring (1-10) and detailed feedback
- **Smart Routing:** Conditional workflow that either processes suitable candidates or handles rejections
- **Action Tracking:** Complete audit trail of all workflow steps and decisions
- **Fallback Logic:** Graceful degradation with template responses when AI services are unavailable

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
```bash
config = {"configurable": {"model_provider": "OpenAI", "model_name": "gpt-4o"}}
result = graph.invoke(input_data, config=config)
```

### Streaming and Real-time Updates
Monitor workflow execution in real-time:
```bash
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
