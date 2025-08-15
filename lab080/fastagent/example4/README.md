# Example 4: Agent Chaining

This example demonstrates FastAgent's powerful agent chaining capabilities, showing how to create multi-step workflows where the output of one agent becomes the input for another.

## Code Overview

**Files**: `agent.py:1-32`, `main.py:1-6`

The main agent demonstrates a two-step pipeline for content processing:

```python
MyFastAgent = FastAgent("Agent Chaining")

@MyFastAgent.agent(
    "url_fetcher",
    instruction="Given a URL, provide a complete and comprehensive summary",
    servers=["fetch"],
)
@MyFastAgent.agent(
    "social_media", 
    instruction="Write a 280 character social media post for any given text. Respond only with the post, never use hashtags.",
)
@MyFastAgent.chain(
    name="post_writer",
    sequence=["url_fetcher", "social_media"],
)
async def main():
    async with MyFastAgent.run() as agent:
        result = await agent.post_writer.send("https://www.radarhack.com")
        print(result)
```

### Key Components

1. **URL Fetcher Agent** (`agent.py:9-13`)
   - Uses the "fetch" MCP server
   - Retrieves and summarizes web content
   - Provides comprehensive analysis of URLs

2. **Social Media Agent** (`agent.py:14-20`)
   - Processes text into social media format
   - Creates 280-character posts
   - Follows specific formatting rules (no hashtags)

3. **Agent Chain** (`agent.py:22-25`)
   - Links agents in sequence: url_fetcher → social_media
   - Named "post_writer" for easy access
   - Passes output automatically between agents

4. **Simple Main** (`main.py:1-6`)
   - Basic Python entry point
   - Demonstrates non-async usage patterns

### Workflow Process

1. **Input**: User provides a URL (e.g., "https://www.radarhack.com")
2. **Step 1**: `url_fetcher` agent retrieves and summarizes the webpage content  
3. **Step 2**: `social_media` agent converts the summary into a 280-character social media post
4. **Output**: Final social media post ready for publishing

## Configuration

This example includes comprehensive configuration files:

### `fastagent.config.yaml`
- Default model settings (GPT-4o, Claude models, etc.)
- MCP server configurations for multiple services
- Provider settings with environment variable placeholders
- Elicitation settings for user interaction

### `fastagent.secrets.yaml`
- API keys and authentication tokens
- Private endpoint configurations
- **⚠️ Important**: Gitignored, never commit to version control

## Available MCP Servers

- **fetch**: Web content retrieval (used by url_fetcher)
- **youtube_transcribe**: YouTube transcription
- **exa_search**: Web search capabilities
- **filesystem**: File system access
- **brave_search**: Brave search engine
- **prompts**: Saved conversation loading

## Setup

```bash
# Create virtual environment
uv venv

# Install dependencies from pyproject.toml
uv sync

# Update secrets file with your API keys
cp fastagent.secrets.yaml.template fastagent.secrets.yaml
# Edit fastagent.secrets.yaml with actual keys

# Test configuration
fast-agent check

# Run the chaining example
uv run agent.py

# Or run the simple main
uv run main.py
```

## What It Does

This example shows how to:
- **Chain Multiple Agents**: Create sequential processing workflows
- **Use MCP Servers**: Integrate external tools (web fetching)
- **Configure Complex Setups**: Handle multiple models and providers
- **Build Content Pipelines**: Transform web content into social media posts
- **Manage State**: Pass data between different specialized agents

The result is a powerful content processing pipeline that can turn any webpage into a social media-ready post automatically.

## Advanced Features

- **Multiple Model Support**: OpenAI, Anthropic, Google, Azure, and more
- **Flexible Configuration**: YAML-based setup with environment variables
- **Security Best Practices**: Separate secrets management
- **Production Ready**: Includes troubleshooting and deployment guidance

For more information, visit: https://fast-agent.ai/
