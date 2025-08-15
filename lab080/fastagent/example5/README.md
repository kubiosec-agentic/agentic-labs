# Example 5: Prompt Server Integration

This example demonstrates how to use FastAgent's built-in prompt server for loading and managing saved conversation histories.

## Code Overview

**File**: `agent.py:1-39`

The agent integrates with the prompts server to demonstrate conversation persistence:

```python
fast = FastAgent("Prompt Server Demo Agent")

@fast.agent(
    instruction="You are a helpful assistant that can access saved conversation prompts",
    servers=["prompts"]
)
async def main():
    async with fast.run() as agent:
        # Initial conversation building
        response1 = await agent.send("What are the key benefits of using AI agents?")
        response2 = await agent.send("Can you elaborate on the automation benefits?")
        
        # Interactive mode for prompt server exploration
        await agent.interactive()
```

### Key Components

- **Prompts Server Integration**: Uses the `prompts` server to access saved conversations
- **Conversation Building**: Creates sample conversations to demonstrate saving
- **Interactive Demo**: Allows hands-on exploration of prompt server features
- **Sample Data**: Includes a pre-built conversation JSON for testing

### Prompt Server Features

1. **Save Conversations**: Use `***SAVE_HISTORY filename.json` to save current conversation
2. **Load Prompts**: Use `/prompts` command to see available saved conversations  
3. **Replay Conversations**: Load and continue from saved conversation states
4. **Multimodal Support**: Save conversations with text, images, and other resources

## Files Included

- **`agent.py`**: Main demonstration script
- **`sample_conversation.json`**: Example saved conversation in MCP format
- **`pyproject.toml`**: Project dependencies

### Sample Conversation Format

The `sample_conversation.json` file shows the MCP `GetPromptResult` format:

```json
{
  "name": "sample_ai_conversation",
  "description": "A sample conversation about AI and automation", 
  "arguments": {
    "messages": [
      {
        "role": "user",
        "content": [{"type": "text", "text": "What are the main advantages..."}]
      },
      {
        "role": "assistant",
        "content": [{"type": "text", "text": "AI automation offers..."}]
      }
    ]
  }
}
```

## Setup

```bash
# Create virtual environment
uv venv

# Install dependencies
uv sync

# Run the prompt server demo
uv run agent.py
```

## Configuration

To use the prompt server in your own projects, add this to `fastagent.config.yaml`:

```yaml
mcp:
  servers:
    prompts:
      command: prompt-server
      args: ["history.json"]  # or your saved conversation file
```

## What It Does

1. **Demonstrates Conversation Saving**: Shows how to save conversation history using `***SAVE_HISTORY`
2. **Prompt Server Access**: Integrates with the prompts server to load saved conversations
3. **Interactive Exploration**: Provides hands-on experience with prompt management commands
4. **Format Examples**: Includes properly formatted conversation JSON for reference

## Use Cases

- **Session Continuity**: Resume conversations across different sessions
- **Template Management**: Store and reuse conversation templates
- **Testing & Debugging**: Replay specific conversation scenarios
- **Multi-Agent Workflows**: Share conversation context between different agents

This example serves as a foundation for building applications that need persistent conversation memory and state management.