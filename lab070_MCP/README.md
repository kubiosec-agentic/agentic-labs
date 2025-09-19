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
The Model Context Protocol (MCP) **Server-Sent Events (SSE) transport** is a communication method that enables AI applications to interact with tools or data sources by establishing a persistent HTTP connection for server-to-client streaming and using HTTP POST requests for client-to-server communication.  

⚠️ **Deprecated:** SSE transport has been deprecated in favor of `mcp streamable-http`, which provides more robust, incremental streaming over plain HTTP and avoids some of the deployment limitations of SSE (such as reverse proxies and gateway compatibility).  

### MCP streamable-http
The **MCP streamable-http** transport is a variant of the Model Context Protocol that leverages standard HTTP endpoints with incremental, chunked responses. Instead of relying on long-lived event streams like SSE, it allows the server to stream tool outputs and model responses back to the client in a progressive way over plain HTTP.  

This approach is particularly useful when integrating with environments where WebSockets or SSE are restricted, while still enabling real-time interaction. The client sends standard HTTP POST requests, and the server responds with a sequence of JSON messages (chunks) that can be consumed as they arrive, making the experience close to interactive streaming.  

#### Start the MCP server (terminal_2)
```
python3 server_streamable.py
```
#### Run the agent (terminal_1)
```
python3 mcp_02_streamable.py 
```
### MCP [SECURITY]
A Model Context Protocol (MCP) **shadowing attack** is a sophisticated exploit where a malicious tool covertly alters the behavior of trusted tools within an AI agent's environment, leading to unauthorized actions or data exfiltration without user awareness.

An **Indirect prompt injection** attacts is covertly manipulating an agent’s external inputs, tools, or environment so it changes behavior or goals without modifying its core prompt.

#### Start the MCP server (terminal_2)
```
python3 server_streamable.py
```
#### Start the MCP server (terminal_3)
Shadowing MCP server
```
python3 server_rogue_streamable.py
```
#### Run the agent (terminal_1)
Model Context Protocol (MCP) shadowing attack
```
python3 mcp_03_streamable.py 
```
#### Run the agent (terminal_1)
Indirect Prompt Injection (Agent Hijacking)
```
python3 mcp_04_streamable.py 
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
