# LAB08: Agentic frameworks
## Introduction
This lab explores advanced AutoGen agents and teamwork, combining tool integration, group chat dynamics, secure code execution, and blogging workflows:
- Use MCP to connect agents to real tools like web fetchers
- Try group chats (RoundRobin and MagenticOne) for iterative refinement
- Use MultimodalWebSurfer for live web browsing with vision
- Run Docker-isolated code with DockerCommandLineCodeExecutor
- Generate content using CrewAI with specialized roles (researcher + writer)

Ideal for building powerful, tool-using, collaborative agents across a range of real-world tasks.
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab08/bin/activate
```
## Lab instructions
#### Agent using MCP
This lab demonstrates how to use AutoGen's MCP integration to empower an AssistantAgent with external tool access via a local MCP server. Specifically, it uses mcp-server-fetch to retrieve and summarize web content. The agent runs tasks like summarizing a Wikipedia page or searching for information on AutoGen, combining tool use with language model reasoning.
```
python3 AG_01.py
```
#### Agent Group Chat
This lab showcases how to create a collaborative agent team using AutoGen, featuring a primary assistant and a critic agent. The agents engage in a round-robin group chat, where the critic provides feedback until satisfied—signaled by the keyword "APPROVE". This setup is ideal for iterative refinement tasks like writing or coding, demonstrating multi-agent coordination and automatic termination based on dynamic conditions.
```
python3 AG_02.py
```
#### MultimodalWebSurfer (Works best on a MAC)
This lab demonstrates how to use the MultimodalWebSurfer agent from AutoGen to perform real web navigation tasks with vision and language capabilities, powered by gpt-4o. It runs within a RoundRobinGroupChat for controlled interaction (max 3 turns) and streams output to the console. The agent can see and interpret web content—ideal for automating tasks like finding documentation or navigating websites.<br>
**Note:** If using the MultimodalWebSurfer, you also need to install playwright dependencies:
```
playwright install --with-deps chromium
```
```
python3 AG_03.py
```
#### MagenticOne
This lab introduces the MagenticOneGroupChat team structure in AutoGen, designed for focused, single-agent collaboration workflows. It wraps an AssistantAgent powered by GPT-4o and runs a streamed task—in this case, exploring a different proof for Fermat’s Last Theorem. The setup demonstrates how to combine rich prompt reasoning with team infrastructure for deep, continuous problem-solving in a structured chat environment.
```
pip install "autogen-agentchat" "autogen-ext[magentic-one]"
```
```
python3 AG_04.py
```
#### DockerCommandLineCodeExecutor
This lab shows how to execute Python code in a Docker container using AutoGen's DockerCommandLineCodeExecutor. It sets up a temporary workspace and runs a CodeBlock inside a python:3.11 Docker image. This approach is useful for isolated and secure code execution, especially when evaluating untrusted or dynamic code.
```
python3 AG_05.py
```

### CrewAI
This script uses CrewAI to coordinate two agents <br>
- a Senior Researcher
- a Writer
<br>
Explore a topic (e.g., AI) and generate a blog post. <br>
The researcher gathers insights using a search tool. The writer creates a markdown-formatted article from the findings. Tasks are run sequentially with agent memory and caching enabled.

```
export SERPER_API_KEY=xxxxxxxxxx
```
```
python3 CRAI_01.py
```

### Google A2A
tbd ...

### Cool extra
- https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/components/command-line-code-executors.html#docker
- https://arxiv.org/abs/2411.04468
- https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/framework/distributed-agent-runtime.html#

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
