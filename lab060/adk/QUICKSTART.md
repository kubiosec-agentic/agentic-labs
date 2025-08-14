# 🤖 Google ADK (Agent Development Kit) - Quickstart Guide

Welcome to the world of intelligent agents! This directory contains **hands-on Google ADK examples** that showcase the power of Google's Agent Development Kit. From web search to flight booking, these agents demonstrate how AI can interact with real-world services through specialized tools.

> 💡 **What You'll Learn**: Build agents that can search the web, manage files, book flights, and integrate multiple tools - all powered by Google's Gemini models!

## 🛠️ Prerequisites

### 1. Install Google ADK
Get started with Google's powerful agent framework:
```bash
pip install google-adk
```
> ✨ **Pro Tip**: This gives you access to Gemini models and the ADK web interface!

### 2. Install Additional Dependencies  
Install the specific packages needed for our examples:
```bash
pip install -r requirements.txt
```
> 📦 **What's Inside**: MCP flight search, environment management, and async support

### 3. Install Node.js (for MCP servers)
Many agents use **Model Context Protocol (MCP)** servers for advanced integrations:
```bash
# On macOS using Homebrew
brew install node

# On Ubuntu/Debian
sudo apt install nodejs npm

# Verify installation
node --version  # Should be v18+ for best compatibility
npm --version
```
> 🔧 **Why Node.js?**: MCP servers often run as Node.js processes that agents communicate with

## ⚙️ Environment Setup

### 1. Create Environment File
Create a `.env` file in the `adk/` directory with your API credentials:
```bash
# Required for Google ADK (tells it to use Google AI Studio instead of Vertex AI)
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Required for Google Search agent - get from Google AI Studio
GOOGLE_API_KEY=your_google_api_key_here

# Required for Flight Assistant - get from SerpApi (free tier available!)
SERP_API_KEY=your_serp_api_key_here
```
> 🔒 **Security Note**: Never commit your `.env` file to version control!

### 2. Get API Keys

**🔑 Google API Key (Free with quotas):**
1. Visit [Google AI Studio](https://aistudio.google.com/) 
2. Click "Get API Key" and create a new key
3. Copy and paste into your `.env` file
> 💰 **Cost**: Google AI Studio offers generous free quotas for Gemini models

**🛫 SERP API Key (Optional - for flight search):**
1. Sign up at [SerpApi](https://serpapi.com/) 
2. Get your API key from the dashboard
3. Add to `.env` file
> 🎯 **Usage**: Only needed for the Flight Assistant agent - other agents work without it

## 🤖 Available Agent Examples

### 1. 🔍 Google Search Agent (`google_search_agent/`)
**What it does**: Your personal research assistant that can search the web for real-time information
**Powered by**: Gemini 2.5 Flash  
**Special abilities**: Google Search API integration
> 💬 **Try asking**: "What's the latest news about AI?" or "How does quantum computing work?"

### 2. ✈️ Flight Assistant (`flight_assistant/`)  
**What it does**: Finds flights, compares prices, and helps plan travel
**Powered by**: Gemini 2.0 Flash  
**Special abilities**: MCP Flight Search server (needs SERP API key)
> 🌍 **Try asking**: "Find flights from San Francisco to Tokyo next month"

### 3. 📁 MCP Agent (`mcp_agent/`)
**What it does**: Manages files and directories like a smart file manager
**Powered by**: Gemini 2.0 Flash  
**Special abilities**: Model Context Protocol filesystem server
> 💻 **Try asking**: "List the Python files in my project" or "Show me the largest files"

### 4. 🔧 Multi-Tool Agent (`multi_tool_agent/`)
**What it does**: Swiss Army knife agent with multiple integrated capabilities
**Powered by**: Gemini 2.0 Flash  
**Special abilities**: Combines several tools for complex tasks
> 🎯 **Try asking**: Mix of search, file management, and analysis tasks

### 5. 🛩️ Standalone Flight Schedule (`standalone/flight_schedule/`)
**What it does**: Specialized flight scheduling and booking assistant
**Powered by**: Gemini 2.0 Flash
**Special setup**: Has its own requirements.txt file
> 📅 **Try asking**: "Help me plan a multi-city trip for next summer"

> 🎨 **One Interface, Many Agents**: All agents are accessed through a single `adk web` command - the interface lets you switch between them!

## 🚀 Running the Examples

### 🌐 Web Interface (The Magic Happens Here!)
**This is where the fun begins** - a beautiful web interface that lets you chat with any agent:

1. **Navigate to mission control**:
   ```bash
   cd adk
   ```

2. **Launch the agent portal**:
   ```bash
   adk web
   ```
   > ⚡ **What happens**: ADK scans all agent directories and spins up a web server

3. **Open your browser** to `http://localhost:8080`
   > 🎨 **You'll see**: A clean interface with all your agents ready to chat

4. **Pick your agent** from the dropdown or agent selector
   > 🤔 **Can't decide?** Start with the Google Search Agent - no extra setup needed!

5. **Start chatting!** Type your questions and watch the magic happen
   > 💡 **Pro tip**: Each agent has different personalities and capabilities

### 📚 API Documentation & Advanced Access

**For developers who want programmatic access:**

- **🌐 Web Chat Interface**: `http://localhost:8080` (main user interface)
- **📖 API Documentation**: `http://127.0.0.1:8000/docs#/` (Swagger/OpenAPI docs)
- **🔧 API Server**: Access agents programmatically via REST API endpoints

> 🚀 **Developer Power-up**: The API docs show you how to integrate these agents into your own applications via HTTP requests!

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
# Use different port for web interface
adk web --port 8081

# Note: API server typically runs on port 8000
# Check http://127.0.0.1:8000/docs#/ for API documentation
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

## 💬 Example Interactions

Get inspired by these conversation starters:

### 🔍 Google Search Agent
```
You: "What's the latest breakthrough in quantum computing?"
Agent: *Searches the web and finds recent research papers and news articles*
"Based on my search, IBM recently announced a major breakthrough..."

You: "How do I cook the perfect risotto?"
Agent: *Finds cooking tutorials and expert tips*
"Here are the key techniques from top chefs..."
```

### ✈️ Flight Assistant  
```
You: "Find flights from New York to Paris for next month under $800"
Agent: *Uses SERP API to search flight comparison sites*
"I found several options for you. Air France has flights starting at $720..."

You: "What's the best time to book flights to Japan?"
Agent: "Based on travel data, booking 6-8 weeks in advance typically offers..."
```

### 📁 MCP File Agent
```
You: "What Python files are in my current directory?"
Agent: *Scans filesystem using MCP*
"I found 12 Python files: agent.py, config.py, utils.py..."

You: "Show me the largest files in my Downloads folder"
Agent: "Here are your largest downloads: movie.mp4 (2.3GB), dataset.zip (1.8GB)..."
```

### 🔧 API Integration Example
```bash
# Example: Call the Google Search agent via API
curl -X POST "http://127.0.0.1:8000/agents/google_search_agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the latest news about AI?"}'

# Check the Swagger docs for complete API reference:
# http://127.0.0.1:8000/docs#/
```

> 🎭 **Each Agent Has Personality**: Notice how each agent responds differently based on their specialized training and tools!
> 
> 🔌 **API Integration**: Use the Swagger docs to integrate agents into your own applications programmatically!

## Additional Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Sample Agents](https://github.com/google/adk-samples)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google AI Studio](https://aistudio.google.com/)

## 🎯 Next Steps - Your Agent Journey

### 🚀 **Level 1: First Contact**
1. **Start with the basics**: Fire up `google_search_agent` (no extra setup!)
2. **Chat away**: Ask it about current events, recipes, or technical topics
3. **Marvel at the magic**: Watch it search the web and synthesize information

### 🔑 **Level 2: Power User** 
1. **Get your API keys**: Set up your `.env` file with Google AI Studio key
2. **Try the Flight Assistant**: Add SERP API key and search for real flights
3. **File management**: Use MCP Agent to explore your filesystem

### 🎨 **Level 3: Customization Master**
1. **Tweak the agents**: Modify instructions in `agent.py` files
2. **Experiment with prompts**: Try different conversation styles
3. **Mix and match tools**: See how agents combine different capabilities

### 🏗️ **Level 4: Agent Architect**
1. **Study the patterns**: Learn how agents are structured
2. **API integration**: Use `http://127.0.0.1:8000/docs#/` to integrate agents into apps
3. **Build your own**: Create custom agents for your specific needs
4. **Share your creations**: Contribute back to the community!

---

## 🎉 Ready to Start Building?

```bash
cd adk
adk web
# Open http://localhost:8080 and let the conversations begin!
```

**Happy building with Google ADK!** 🤖✨

> 💌 **Need Help?** Check the troubleshooting section above or dive into the [official documentation](https://google.github.io/adk-docs/)