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

# Acticate the virtual environment
source .venv/bin/activate 

uv pip install fast-agent-mcp

# Run the agent
uv run agent.py
```

### API Key Configuration

1. **Get API Keys**: 
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. **Update Configuration**:
   ```bash
   # Edit the secrets file
   nano fastagent.secrets.yaml
   ```
   
   Replace `"xxxxxxx"` with your actual API keys:
   ```yaml
   OPENAI_API_KEY: "sk-your-openai-key-here"
   ANTHROPIC_API_KEY: "sk-ant-your-anthropic-key-here"
   ```

3. **Choose Your Model** in `fastagent.config.yaml`:
   ```yaml
   # For OpenAI (recommended for beginners)
   default_model: "openai.gpt-4o"
   
   # For Anthropic
   default_model: "anthropic.claude-3-5-haiku-20241022"
   ```

### Troubleshooting

**Error: `invalid x-api-key`**
- Check that your API key is valid and not expired
- Ensure the key is correctly formatted in `fastagent.secrets.yaml`
- Verify you have credits/usage available in your account

**Error: `authentication_error`**  
- Double-check the API key is copied correctly (no extra spaces)
- Try generating a new API key from the provider's dashboard

**No API Keys Available**
- The configuration defaults to `playbook` model for testing without keys
- Add real API keys to use actual AI models

## What It Does

1. Initializes a FastAgent with basic configuration
2. Starts an interactive chat session
3. Responds to user input as a helpful assistant
4. Continues until you exit the session

This is the perfect starting point for understanding FastAgent basics before moving to more complex examples.