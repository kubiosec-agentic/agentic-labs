# Google ADK (Agent Development Kit) - Quickstart Guide

This directory contains Google ADK agent examples that demonstrate different agent capabilities using Google's Agent Development Kit.

## Prerequisites

### 1. Install Google ADK
```bash
pip install google-adk
```

### 2. Install Additional Dependencies  
```bash
pip install -r requirements.txt
```

### 3. Install Node.js (for MCP servers)
Required for MCP (Model Context Protocol) servers:
```bash
# On macOS using Homebrew
brew install node

# On Ubuntu/Debian
sudo apt install nodejs npm

# Verify installation
node --version
npm --version
```

## Environment Setup

### 1. Create Environment File
Create a `.env` file in the `adk/` directory:
```bash
# Required for Google ADK
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Required for Google Search agent
GOOGLE_API_KEY=your_google_api_key_here

# Required for Flight Assistant (from serpapi.com)
SERP_API_KEY=your_serp_api_key_here
```

### 2. Get API Keys

**Google API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to `.env` file

**SERP API Key (for flight search):**
1. Go to [SerpApi](https://serpapi.com/)
2. Sign up and get your API key
3. Add to `.env` file

## Available Agent Examples

### 1. Google Search Agent (`google_search_agent/`)
**Purpose**: Answer questions using Google Search  
**Model**: Gemini 2.5 Flash  
**Tools**: Google Search API

### 2. Flight Assistant (`flight_assistant/`)  
**Purpose**: Search for flights and travel information  
**Model**: Gemini 2.0 Flash  
**Tools**: MCP Flight Search server (requires SERP API)

### 3. MCP Agent (`mcp_agent/`)
**Purpose**: File system management using MCP  
**Model**: Gemini 2.0 Flash  
**Tools**: Model Context Protocol filesystem server

### 4. Multi-Tool Agent (`multi_tool_agent/`)
**Purpose**: Agent with multiple tool integrations
**Model**: Gemini 2.0 Flash  
**Tools**: Multiple integrated tools

### 5. Standalone Flight Schedule (`standalone/flight_schedule/`)
**Purpose**: Standalone flight scheduling agent
**Model**: Gemini 2.0 Flash
**Requirements**: Separate requirements.txt

**Note**: All agents are accessed by running `adk web` from the main `adk/` directory. The web interface will present all available agents for selection.

## Running the Examples

### Primary Method: Web Interface (Recommended & Tested)
1. Navigate to the main ADK directory:
   ```bash
   cd adk
   ```

2. Start the web interface:
   ```bash
   adk web
   ```

3. Open your browser to `http://localhost:8080`

4. The web interface will show all available agents - select the one you want to interact with

5. Interact with the selected agent through the web UI

### Method 2: Command Line (Optional)
**Note**: Command line execution may have different syntax or may not be available for all agent types. The web interface (`adk web`) is the recommended and most reliable method.

```bash
# From the adk directory - syntax may vary
# Check ADK documentation for current CLI commands
adk --help
```

**Important Note**: Always run `adk web` from the main `adk/` directory, not from individual agent subdirectories. The ADK CLI will automatically discover all agents in the subdirectories.

## Troubleshooting

### Common Issues

**1. "google-adk not found"**
```bash
pip install google-adk
# or
pip install --upgrade google-adk
```

**2. "GOOGLE_API_KEY not set"**
- Ensure `.env` file exists in the `adk/` directory
- Verify API key is correct and has necessary permissions

**3. "MCP server failed to start"**
- Ensure Node.js is installed: `node --version`  
- Check if MCP packages are accessible
- Verify absolute paths in agent configuration

**4. "SERP_API_KEY missing"**
- Required only for flight_assistant example
- Get free API key from [serpapi.com](https://serpapi.com/)
- Add to `.env` file

**5. Port conflicts**
```bash
# Use different port
adk web --port 8081
```

**6. Command line (`adk run`) not working**
- The `adk run` command may not be available or may have different syntax
- Use `adk --help` to see available commands
- **Recommendation**: Use `adk web` interface which is known to work reliably

### Available Commands
Check what commands are available:
```bash
adk --help
adk web --help
```

### Debug Mode
Run with debug information:
```bash
adk web --debug
```

## Agent Configuration

### Basic Agent Structure
```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='my_agent',
    instruction='Agent instructions here',
    tools=[google_search]  # Add tools
)
```

### MCP Integration
```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

tools=[
    MCPToolset(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/folder"]
        )
    )
]
```

## Example Interactions

### Google Search Agent
```
User: "What's the latest news about AI?"
Agent: [Searches Google and provides current information]
```

### Flight Assistant  
```
User: "Find flights from NYC to LAX next week"
Agent: [Searches flight options using SERP API]
```

### MCP File Agent
```
User: "List files in my directory"
Agent: [Uses MCP filesystem server to browse files]
```

## Additional Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Sample Agents](https://github.com/google/adk-samples)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google AI Studio](https://aistudio.google.com/)

## Next Steps

1. **Start Simple**: Begin with `google_search_agent`
2. **Add API Keys**: Configure `.env` file with required keys
3. **Experiment**: Try different prompts and interactions
4. **Customize**: Modify agent instructions and tools
5. **Build New**: Create your own agents using the examples as templates

Happy building with Google ADK! 🚀