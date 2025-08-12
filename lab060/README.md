# LAB06: Multi Agent Orchestration
## Introduction
This lab introduces the **OpenAI agents framework** for building structured, tool-using AI agents. You’ll learn to:
- Create basic agents and run them synchronously
- Implement agent handoff based on input language
- Attach custom tools to agents for function calling
- Enforce guardrails to filter or block certain outputs

Perfect for understanding core concepts in building modular, controllable AI agents.
## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab06/bin/activate
```
## Lab instructions
#### Simple OpenAI Agent
This simple script runs a synchronous AI agent using the agents framework. It defines an Agent with the role of a helpful assistant.
```
python3 ./agent_01.py
```
#### Agent handoff
This script demonstrates multi-agent handoff using the agents framework. It sets up three agents. 
The `triage agent` detects the input language and delegates the task to the appropriate agent.
```
python3 ./agent_02.py
```
#### Agent and tools
This script shows how to create a simple tool-using AI agent with the agents framework. It defines a `get_weather` function as a tool, registers it with the agent, and uses it to process a user query. 
```
python3 ./agent_03.py
```
#### Agent and Guardrails
This script demonstrates how to enforce output guardrails on an AI agent using the agents framework.
```
python3 ./agent_04.py
```
### Google Agent Development Kit
Optionally, check out [Agent Development Kit](https://google.github.io/adk-docs/get-started/quickstart/)<br>
[ADK Sample agents](https://github.com/google/adk-samples) can be found.

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
