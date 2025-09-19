# LAB070: Model Context Protocol
## Introduction
This lab introduces the Model Context Protocol (MCP), a secure standard for connecting AI agents to tools and data sources. You'll explore:
- MCP transports: stdio and SSE for agent-tool communication
- Building agents that use tools over MCP servers
- Simulating MCP shadowing and agent hijacking attacks to study security risks
- Debugging tools and best practices via the MCP debugging suite

Ideal for understanding secure tool orchestration in AI systems and the risks of compromised environments.
## List of MCP servers
- https://github.com/docker/mcp-servers

## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab070/bin/activate
```
## Lab instructions
### MCP stdio
The Model Context Protocol (MCP) stdio transport is a communication method that enables local AI applications to interact with tools or data sources by spawning subprocesses and exchanging JSON-RPC messages via standard input and output streams.
```
python3 mcp_01_stdio.py
```
### MCP SSE
The Model Context Protocol (MCP) Server-Sent Events (SSE) transport is a communication method that enables AI applications to interact with tools or data sources by establishing a persistent HTTP connection for server-to-client streaming and using HTTP POST requests for client-to-server communication.  This code example connects to a MCP SSE server using the main() function, that in turn will call the run() function, creating an agent answering a few questions that require calling external tools.

#### Start the MCP SSE server (terminal_2)
```
python3 server_streamable.py
```
#### Run the agent (terminal_1)
```
python3 mcp_02_streamable.py 
```
### MCP SSE [SECURITY] (Shadowing attack)
A Model Context Protocol (MCP) shadowing attack is a sophisticated exploit where a malicious tool covertly alters the behavior of trusted tools within an AI agent's environment, leading to unauthorized actions or data exfiltration without user awareness.
#### Start the MCP SSE server (terminal_2)
```
python3 server_streamable.py
```
#### Start the MCP SSE server (terminal_3)
```
python3 server_rogue_streamable.py
```
#### Run the agent (terminal_1)
Model Context Protocol (MCP) shadowing attack
```
python3 mcp_03_streamable.py 
```
### MCP SSE [SECURITY] (Indirect Prompt Injection)
#### Run the agent (terminal_1)
Indirect Prompt Injection (Agent Hijacking)
```
python3 mcp_04_streamable.py 
```
### Youtube Transcriber
You can obtain a token from https://mcp-cloud.ai/ <br>
Deploy the youtube-transcribe MCP server.<br>

```
export MCPCLOUD_API_TOKEN="xxxxxx"
```
```
export MCP_SSE_URL="xxxxxxx"
```
```
python3 mcp_05_youtube-transcribe.py 
```
### MCP Debugging
https://github.com/mcp-firewall/mcp-debugging

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
