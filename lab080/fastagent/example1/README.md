# Example 1: Interactive Agent

This example demonstrates the simplest FastAgent setup with an interactive chat interface.

## Code Overview

**File**: `agent.py:1-13`

The code creates a basic FastAgent with minimal configuration:

```python
fast = FastAgent("My Interactive Agent")

@fast.agent(instruction="You are a helpful assistant")
async def main():
    async with fast.run() as agent:
        # Start interactive prompt
        await agent()
```

### Key Components

- **FastAgent Instance**: Creates an agent named "My Interactive Agent"  
- **Agent Decorator**: Configures the agent with a simple instruction
- **Interactive Mode**: `await agent()` starts a chat session where you can type messages
- **Context Manager**: `async with fast.run()` handles agent lifecycle

## Setup & Usage

```bash
# Create virtual environment
uv venv

# Install dependencies  
uv pip install fast-agent-mcp

# Run the agent
uv run agent.py
```

## What It Does

1. Initializes a FastAgent with basic configuration
2. Starts an interactive chat session
3. Responds to user input as a helpful assistant
4. Continues until you exit the session

This is the perfect starting point for understanding FastAgent basics before moving to more complex examples.