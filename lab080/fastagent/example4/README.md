# FastAgent Configuration

This directory contains a configured FastAgent application with MCP (Model Context Protocol) servers.

## Configuration Files

### `fastagent.config.yaml`
Main configuration file containing:
- Default model settings
- MCP server configurations  
- Provider settings (with placeholder environment variables)
- Elicitation settings for user interaction

### `fastagent.secrets.yaml`
Sensitive configuration file containing:
- API keys and tokens
- Authentication credentials
- Private endpoints

**⚠️ Important:** This file is gitignored and should never be committed to version control.

## Quick Start

1. **Update secrets file**: Edit `fastagent.secrets.yaml` and add your actual API keys:
   ```yaml
   OPENAI_API_KEY: "sk-your-actual-openai-key"
   ANTHROPIC_API_KEY: "sk-ant-your-actual-anthropic-key"
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   uv pip install fast-agent-mcp
   ```

3. **Test configuration**:
   ```bash
   fast-agent check
   ```

## Available MCP Servers

- **youtube_transcribe**: Remote SSE server for YouTube transcription
- **exa_search**: Remote SSE server for web search
- **fetch**: Local STDIO server for web content fetching  
- **filesystem**: Local STDIO server for file system access
- **prompts**: Local server for loading saved conversations
- **brave_search**: Local STDIO server for Brave search (requires API key)

## Model Providers

The configuration supports multiple LLM providers:
- **OpenAI**: GPT-4o (default), GPT-4, GPT-3.5, o1 series
- **Anthropic**: Claude models (Sonnet, Haiku, Opus)
- **Azure OpenAI**: Enterprise Azure deployment
- **Google**: Gemini models
- **DeepSeek**: DeepSeek v3
- **Groq**: Fast inference models
- **Others**: XAI Grok, OpenRouter, AWS Bedrock, local Ollama

## Usage Examples

### Basic Agent
```python
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("My Agent")

@fast.agent(
    instruction="You are a helpful assistant",
    servers=["fetch", "filesystem"]  # Use specific MCP servers
)
async def main():
    async with fast.run() as agent:
        response = await agent.send("Help me analyze a file")
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Interactive Mode
```python
@fast.agent(instruction="You are a helpful assistant")
async def main():
    async with fast.run() as agent:
        await agent.interactive()  # Start chat session
```

### Command Line Usage
```bash
# Run with specific model
fast-agent --model anthropic.claude-3-5-sonnet-latest --message "Hello"

# Interactive mode
fast-agent --interactive

# Use specific servers
fast-agent --servers fetch,filesystem --message "List files"
```

## Security Notes

- Keep `fastagent.secrets.yaml` secure and never commit it
- Use environment variables in production
- Rotate API keys regularly
- Consider using Azure Key Vault or similar for production deployments

## Troubleshooting

1. **API Key Issues**: Run `fast-agent check` to validate configuration
2. **Server Connection**: Check MCP server URLs and authentication
3. **Model Access**: Verify you have access to the specified models
4. **Dependencies**: Ensure all required packages are installed

For more information, visit: https://fast-agent.ai/
