# Microsoft Agent Framework Demo

This repository contains three demo scripts showcasing the Microsoft Agent Framework with Azure OpenAI integration.

## Prerequisites

1. **Azure OpenAI Resource**: You need access to an Azure OpenAI resource with a deployed model
2. **Python Environment**: Python 3.12+ with virtual environment support
3. **API Key**: Azure OpenAI API key for authentication

## Setup

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install agent-framework
```

### 3. Set Environment Variables

Set the required environment variables for Azure OpenAI:

```bash
export AZURE_OPENAI_API_KEY="your-actual-azure-openai-api-key"
```

**Optional environment variables:**
```bash
export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o-mini"  # If not specified in code
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"     # For Azure AI Agent examples
```

## Demo Scripts

### demo_fomo_1.py - Basic Weather Agent

A simple weather agent that demonstrates basic Azure OpenAI integration.

**Features:**
- Basic ChatAgent with Azure OpenAI
- Simple weather function tool
- Direct API key authentication

**Run:**
```bash
source .venv/bin/activate
python ./demo_fomo_1.py
```

**Expected Output:**
```
The current weather in Seattle is sunny with a high temperature of 53°C...
```

### demo_fomo_2.py - Weather Agent with Function Middleware

Extends the basic agent with function middleware that blocks certain requests.

**Features:**
- Function middleware that blocks weather requests for "Atlantis"
- Demonstrates middleware intercepting tool calls
- Same Azure OpenAI configuration as demo 1

**Run:**
```bash
source .venv/bin/activate
python ./demo_fomo_2.py
```

**Test the middleware:**
```bash
python -c "
import asyncio
from demo_fomo_2 import agent
print(asyncio.run(agent.run('What is the weather like in Atlantis?')))
"
```

**Expected Output:**
- Normal request: Weather information for Seattle
- Atlantis request: "Atlantis is a special place, we must never ask about the weather there!!"

### demo_fomo_3.py - Multi-Layer Middleware Security

Advanced demo with both chat and function middleware for comprehensive security.

**Features:**
- **Chat Middleware**: Blocks requests containing sensitive terms (password, secret, api_key, token)
- **Function Middleware**: Blocks weather requests for Atlantis
- Demonstrates middleware layering and execution order
- Cost-saving by blocking inappropriate requests before LLM calls

**Run:**
```bash
source .venv/bin/activate
python ./demo_fomo_3.py
```

**Expected Output:**
```
Testing normal weather request:
The weather in Seattle is currently sunny, with a high of 53°C...

Testing Atlantis request (function middleware):
Atlantis is a special place, and we must never ask about the weather there!

Testing security filter (chat middleware):
I cannot process requests containing sensitive information...
```

### demo_fomo_4.py - Azure AI Agent Client with Middleware

Enterprise-grade demo using Azure AI Agent Client with Azure CLI authentication and comprehensive middleware.

**Features:**
- **Azure AI Agent Client**: Uses Azure CLI authentication (requires `az login`)
- **Auto-managed lifecycle**: Agents created and deleted automatically
- **Both streaming and non-streaming** response examples
- **Multi-layer middleware**: Same security features as demo_fomo_3
- **Comprehensive testing**: Three test scenarios included

**Prerequisites:**
```bash
# Install and login to Azure CLI first
az login

# Set required environment variables
export AZURE_AI_PROJECT_ENDPOINT="https://demo-project-kubiosec-resource.services.ai.azure.com/api/projects/demo-project-kubiosec"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"
```

**Run:**
```bash
source .venv/bin/activate
python ./demo_fomo_4.py
```

**Expected Output:**
```
=== Non-streaming Response Example with Middleware ===
User: What's the weather like in Seattle?
Agent: The weather in Seattle is sunny with a high of 53°C...

=== Middleware Test Examples ===
Test 2 - Atlantis request (should be blocked by function middleware):
Agent: Atlantis is a special place, and we must never ask about the weather there!

Test 3 - Request with sensitive info (should be blocked by chat middleware):
Agent: I cannot process requests containing sensitive information...
```

## Demo Comparison: Authentication & Chat Clients

| Demo | Chat Client | Authentication | Middleware | Key Features |
|------|-------------|----------------|------------|--------------|
| **demo_fomo_1.py** | `AzureOpenAIChatClient` | API Key | None | Basic weather agent, simple setup |
| **demo_fomo_2.py** | `AzureOpenAIChatClient` | API Key | Function only | Adds Atlantis blocking |
| **demo_fomo_3.py** | `AzureOpenAIChatClient` | API Key | Chat + Function | Multi-layer security, cost optimization |
| **demo_fomo_4.py** | `AzureAIAgentClient` | Azure CLI | Chat + Function | Enterprise-grade, auto-lifecycle, streaming |

### Key Differences:

#### **Authentication Methods:**
- **API Key** (demos 1-3): Simple, direct authentication using `AZURE_OPENAI_API_KEY`
- **Azure CLI** (demo 4): Enterprise authentication, requires `az login` and environment variables

#### **Chat Client Types:**
- **AzureOpenAIChatClient** (demos 1-3): 
  - Direct Azure OpenAI API access
  - Manual agent lifecycle management
  - Simpler configuration
  - Endpoint: `https://phbo-openai-1.openai.azure.com/`
  
- **AzureAIAgentClient** (demo 4):
  - Azure AI Foundry project integration
  - Automatic agent creation/deletion
  - Advanced features (streaming, lifecycle management)
  - Endpoint: `https://demo-project-kubiosec-resource.services.ai.azure.com/`

#### **Middleware Evolution:**
1. **No Middleware**: Basic functionality
2. **Function Middleware**: Blocks specific tool calls
3. **Chat + Function**: Comprehensive security layers
4. **Enterprise Implementation**: Same security with enterprise client

#### **Use Cases:**
- **Demos 1-3**: Development, testing, simple deployments
- **Demo 4**: Production, enterprise environments, complex workflows

## Configuration Details

### Azure OpenAI Configuration

All demos use the following configuration:
- **Endpoint**: `https://phbo-openai-1.openai.azure.com/`
- **Deployment**: `gpt-4o-mini`
- **Authentication**: API Key via environment variable

### Middleware Execution Order

In demo_fomo_3.py, middleware executes in this order:
1. **Security Chat Middleware** (before LLM call)
2. **LLM Processing** (if not blocked)
3. **Atlantis Function Middleware** (during tool execution)

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'agent_framework'**
   ```bash
   # Make sure virtual environment is activated and package is installed
   source .venv/bin/activate
   pip install agent-framework
   ```

2. **ServiceInitializationError: Azure OpenAI deployment name is required**
   ```bash
   export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o-mini"
   ```

3. **AuthenticationError: Access denied due to invalid subscription key**
   ```bash
   # Check your API key is correct
   export AZURE_OPENAI_API_KEY="your-correct-api-key"
   ```

4. **DeploymentNotFound: The API deployment for this resource does not exist**
   - Verify the deployment name exists in your Azure OpenAI resource
   - Check the endpoint URL matches your resource
   - Ensure the deployment is fully deployed and active

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_API_KEY` | Yes | Your Azure OpenAI API key |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | Optional | Deployment name (defaults to code value) |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Optional | For Azure AI Agent examples |

## Additional Resources

- [Microsoft Agent Framework GitHub](https://github.com/microsoft/agent-framework/)
- [Azure OpenAI Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure AI Foundry](https://ai.azure.com)

<!-- Generated by Copilot -->
