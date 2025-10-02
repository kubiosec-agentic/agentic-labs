# Microsoft Agent Framework 
## Getting Started
1. Goto https://ai.azure.com and <Sign In>
2. Create new <Azure AI Foundry resource>
3. Create a project **<demo-project-kubiosec>**
4. Note Azure AI Foundry project endpoint <https://demo-project-kubiosec-resource.services.ai.azure.com/api/projects/demo-project-kubiosec>
5. Goto Models + endpoints -> Deploy model -> Deploy base model -> Select gpt-4o -> Confirm -> Deploy
6. Note (see Deployment info) Name **<gpt-4o>**

## Azure Agent Framwork
For more information see https://github.com/microsoft/agent-framework/ <br>
Set the endpoint (3)
```
export AZURE_AI_PROJECT_ENDPOINT="https://demo-project-kubiosec-resource.services.ai.azure.com/api/projects/demo-project-kubiosec"
```
Set the Deployment Name (6)
```
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"
```
Optional
```
export BING_CONNECTION_ID="your-bing-connection-id"  # Optional, only needed for web search samples
```

## Run the agent
```
python3 -m venv .venv
```
```
source .venv/bin/activate
```
```
pip install agent-framework
```
### Simple Agent
```
python3 ./azure_agent.py
```
### Code Executing Agent

```
python3 ./azure_code_interpreter.py
```


### OpenAI example 
```
export OPENAI_CHAT_MODEL_ID=gpt-4o
export OPENAI_RESPONSES_MODEL_ID=gpt-4o
export OPENAI_API_KEY=xxxxxx
export OPENAI_ORG_ID=xxxxxx    #optional
export OPENAI_API_BASE_URL=xxxxx #optional
```
```
python openai_agent.py
```
