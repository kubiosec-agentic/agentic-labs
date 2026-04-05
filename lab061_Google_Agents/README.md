![Google](https://img.shields.io/badge/Google-green) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB061: Google ADK
## Introduction
Welcome to the world of intelligent agents! This directory contains hands-on Google ADK examples that showcase the power of Google's Agent Development Kit. From web search to flight booking, these agents demonstrate how AI can interact with real-world services through specialized tools.
## Set up your environment
### Prerequisites
- Python 3.8+ with pip  
- OpenAI API key with access to agents framework and Responses API

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab061/bin/activate
```

## Lab instructions

### Google Agent Development Kit (ADK)
This lab includes Google's Agent Development Kit examples in the `adk/` directory:
- **Flight Assistant**: AI agent for flight booking and scheduling
- **Google Search Agent**: Web search integration with Google APIs
- **MCP Agent**: Model Context Protocol implementation
- **Multi-Tool Agent**: Agent with multiple tool integrations

## Environment Setup

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

**Security Note**: Never commit your `.env` file to version control!

### 2. Get API Keys

**Google API Key (Free with quotas):**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key" and create a new key
3. Copy and paste into your `.env` file

**Cost**: Google AI Studio offers generous free quotas for Gemini models

**SERP API Key (Optional - for flight search):**
1. Sign up at [SerpApi](https://serpapi.com/)
2. Get your API key from the dashboard
3. Add to `.env` file

**Usage**: Only needed for the Flight Assistant agent - other agents work without it

## Available Agent Examples

### 1. Google Search Agent (`google_search_agent/`)
**What it does**: Personal research assistant that can search the web for real-time information

**Powered by**: Gemini 2.5 Flash

**Special abilities**: Google Search API integration

**Try asking**: "What's the latest news about AI?" or "How does quantum computing work?"

### 2. Flight Assistant (`flight_assistant/`)
**What it does**: Finds flights, compares prices, and helps plan travel

**Powered by**: Gemini 2.0 Flash

**Special abilities**: MCP Flight Search server (needs SERP API key)

**Try asking**: "Find flights from San Francisco to Tokyo next month"

### 3. MCP Agent (`mcp_agent/`)
**What it does**: Manages files and directories like a smart file manager

**Powered by**: Gemini 2.0 Flash

**Special abilities**: Model Context Protocol filesystem server

**Try asking**: "List the Python files in my project" or "Show me the largest files"

### 4. Multi-Tool Agent (`multi_tool_agent/`)
**What it does**: Swiss Army knife agent with multiple integrated capabilities

**Powered by**: Gemini 2.0 Flash

**Special abilities**: Combines several tools for complex tasks

**Try asking**: Mix of search, file management, and analysis tasks

**One Interface, Many Agents**: All agents are accessed through a single `adk web` command - the interface lets you switch between them!

## Running the Examples

### Web Interface
This is the main interface - a web portal that lets you chat with any agent:

1. **Navigate to mission control**:
   ```bash
   cd adk
   ```

2. **Launch the agent portal**:
   ```bash
   adk web
   ```

3. **Open your browser** to `http://localhost:8000`

4. **Pick your agent** from the dropdown or agent selector. Start with the Google Search Agent - no extra setup needed!

5. **Start chatting!** Type your questions and watch the agent respond.

### API Server & Documentation

**ADK provides two interfaces when you run `adk web`:**

- **Web Chat Interface**: `http://localhost:8080` (main user interface)
- **API Server**: `http://127.0.0.1:8000` (REST API endpoints)
- **API Documentation**: `http://127.0.0.1:8000/docs#/` (Swagger/OpenAPI docs)

**How to Access the API Server:**
1. **Start ADK**: Run `adk web` from the `adk/` directory
2. **Two servers start automatically**:
   - Web interface on port 8080
   - API server on port 8000
3. **Access API docs**: Open `http://127.0.0.1:8000/docs#/` in your browser
4. **Interactive testing**: Use the Swagger UI to test API calls directly

**Important Note**: Always run `adk web` from the main `adk/` directory, not from individual agent subdirectories. The ADK CLI will automatically discover all agents in the subdirectories.

### Command Line (Optional)
**Note**: Command line execution may have different syntax or may not be available for all agent types. The web interface (`adk web`) is the recommended and most reliable method.

```bash
# From the adk directory - syntax may vary
# Check ADK documentation for current CLI commands
adk run mcp_agent
```

### API Server Method
Run the API server:
```bash
adk api_server
```

Explore the Swagger docs as explained above. Now you can interact using API calls.

Create a session:
```bash
curl -X POST http://localhost:8000/apps/mcp_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"name": "demo"}}'
```

```bash
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"app_name": "mcp_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "what is the current allowed list"
    }]
    }
}'
```




## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [ADK Sample Agents](https://github.com/google/adk-samples)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google AI Studio](https://aistudio.google.com/)

## Cleanup environment
```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
