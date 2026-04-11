# Microsoft Agent Framework (Addendum)

Reference examples for the Microsoft Agent Framework 1.0 GA Python API.
These scripts complement the hands-on exercises in **lab075_MS_Agent_Framework**.

The Azure examples here use `az login` (AzureCliCredential) for authentication
instead of API keys, showing an alternative approach to the key-based setup in lab075.

> For the full documentation see <https://github.com/microsoft/agent-framework/>

## Azure AI Foundry Setup

1. Go to <https://ai.azure.com> and sign in
2. Create a new Azure AI Foundry resource and a project
3. Go to **Models + endpoints**, deploy a base model (e.g. `gpt-4o`)
4. Note the project endpoint and the deployment name
5. Set your environment variables:

```bash
export FOUNDRY_PROJECT_ENDPOINT="https://<project>.services.ai.azure.com"
export FOUNDRY_MODEL="gpt-4o"
```

6. Authenticate with the Azure CLI:

```bash
az login
```

> The Azure portal UI changes frequently. If the steps above don't match
> exactly, refer to the official docs at <https://learn.microsoft.com/en-us/azure/ai-foundry/>.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Scripts

### openai_agent.py

Minimal example using `OpenAIChatClient().as_agent()` with a weather tool.

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_CHAT_MODEL="gpt-4o-mini"
python3 openai_agent.py
```

### azure_agent.py

Uses `FoundryChatClient` + `Agent` with streaming and non-streaming examples.

```bash
python3 azure_agent.py
```

### azure_agent_mcp.py

Connects to an HTTP-based MCP server (Microsoft Learn docs) and queries it.

```bash
python3 azure_agent_mcp.py
```

### azure_code_interpreter.py

Uses `client.get_code_interpreter_tool()` to execute Python code server-side.

```bash
python3 azure_code_interpreter.py
```

### openai_workflow.py

Demonstrates `WorkflowBuilder` with a Worker/Reviewer cycle wrapped as an agent
via `.as_agent()`. The Worker generates responses and the Reviewer evaluates them,
iterating until approval.

```bash
python3 openai_workflow.py
```

## Cleanup

```bash
deactivate
rm -rf .venv
```
