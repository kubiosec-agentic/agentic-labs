# Example 6: Memory & State Transfer

This example demonstrates FastAgent's advanced memory management and state transfer capabilities, showing how to maintain conversation context across multiple agents and sessions.

## Code Overview

**Files**: `agent.py:1-65`, `memory_demo.py:1-92`

### Basic Memory Demo (`agent.py`)

Creates multiple agents with different memory configurations:

```python
@fast.agent(
    name="primary",
    instruction="You are a primary assistant...",
    use_history=True
)
@fast.agent(
    name="analyst", 
    instruction="You are a data analyst...",
    model="haiku",
    use_history=True
)
@fast.agent(
    name="summarizer",
    instruction="You are a summarizer...",
    model="gpt-4o-mini", 
    use_history=True
)
```

### Advanced Memory Demo (`memory_demo.py`)

Includes a custom `MemoryManager` class for persistent storage:

```python
class MemoryManager:
    def save_conversation(self, agent_name, messages):
        """Save conversation history to file"""
        
    def load_conversation(self, agent_name):
        """Load conversation history from file"""
```

## Key Features Demonstrated

### 1. Conversation Memory Management
- **History Enabled**: `use_history=True` maintains conversation context
- **Multi-Agent Memory**: Different agents maintain separate conversation histories
- **Memory Transfer**: Share conversation context between agents using message history

### 2. State Transfer Between Agents

**Pattern**: `agent.py:45-51`
```python
# Transfer conversation history to analyst
analyst_response = await agent.analyst.send([
    "Please analyze the conversation history...",
    *agent.primary.message_history
])
```

### 3. Persistent Memory Across Sessions

**Implementation**: `memory_demo.py:15-35`
- Save conversations to JSON files
- Restore conversation history on startup
- Manage multiple agent memories independently

### 4. Multi-Model Collaboration
- **Primary Agent**: Default model with full conversation context
- **Analyst Agent**: Haiku model for pattern analysis
- **Summarizer Agent**: GPT-4o-mini for concise summaries

## Files Included

- **`agent.py`**: Basic memory and state transfer demonstration
- **`memory_demo.py`**: Advanced persistent memory management
- **`pyproject.toml`**: Project dependencies

## Memory Features

### Built-in Memory Management
1. **Automatic History**: Conversations remembered by default
2. **History Disable**: Use `use_history=False` to disable memory
3. **State Transfer**: Pass `message_history` between agents
4. **Model Independence**: Different models maintain separate contexts

### Advanced Memory Patterns
1. **Cross-Session Persistence**: Save/load conversations from files
2. **Selective Memory**: Choose what to remember and share
3. **Memory Analysis**: Agents can analyze their own conversation history
4. **Context Compression**: Summarize long conversations for efficiency

## Setup

```bash
# Create virtual environment
uv venv

# Install dependencies
uv sync

# Run basic memory demo
uv run agent.py

# Run advanced memory demo  
uv run memory_demo.py
```

## What It Does

### Basic Demo (`agent.py`)
1. **Builds Context**: Creates conversation history with primary agent
2. **Transfers State**: Shares conversation with analyst for pattern analysis
3. **Creates Summary**: Transfers context to summarizer for concise overview
4. **Interactive Mode**: Explore memory features hands-on

### Advanced Demo (`memory_demo.py`)
1. **Persistent Storage**: Saves conversations to `conversation_memory.json`
2. **Session Restoration**: Loads previous conversations on startup
3. **Multi-Agent Memory**: Manages separate memory for different agents
4. **Memory Analytics**: Tracks conversation statistics and patterns

## Memory Management Commands

- **Save History**: `***SAVE_HISTORY session_memory.json`
- **Load Prompts**: Use prompt server to restore saved conversations
- **Transfer State**: Pass `agent.message_history` to other agents
- **Clear Memory**: Restart agent or use `use_history=False`

## Use Cases

### State Transfer Applications
- **Multi-Stage Processing**: Pass work between specialized agents
- **Context Preservation**: Maintain conversation context across agent switches
- **Collaborative Analysis**: Multiple agents analyzing the same conversation

### Persistent Memory Applications  
- **Long-Running Sessions**: Resume conversations across application restarts
- **User Profiles**: Remember user preferences and conversation patterns
- **Learning Systems**: Build knowledge base from conversation history
- **Audit Trails**: Maintain complete conversation logs for compliance

This example showcases how FastAgent's memory capabilities enable sophisticated multi-agent workflows with persistent state management.