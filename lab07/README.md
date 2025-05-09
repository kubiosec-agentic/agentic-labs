# LAB07
## List of MCP servers
- https://github.com/docker/mcp-servers
- 
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab07/bin/activate
```
## Lab instructions
### MCP stdio
The Model Context Protocol (MCP) stdio transport is a communication method that enables local AI applications to interact with tools or data sources by spawning subprocesses and exchanging JSON-RPC messages via standard input and output streams.
```
python3 mcp_01.py
```
### MCP SSE
The Model Context Protocol (MCP) Server-Sent Events (SSE) transport is a communication method that enables remote AI applications to interact with tools or data sources by establishing a persistent HTTP connection for server-to-client streaming and using HTTP POST requests for client-to-server communication.  This code example connects to a MCP SSE server using the main() function, that in turn will call the run() function, creating an agent answering a few questions that require calling external tools.

#### Start the MCP SSE server (terminal_2)
```
python3 server.py
```
#### Run the agent (terminal_1)
```
python3 mcp_02.py 
```
### MCP SSE [SECURITY]
A Model Context Protocol (MCP) shadowing attack is a sophisticated exploit where a malicious tool covertly alters the behavior of trusted tools within an AI agent's environment, leading to unauthorized actions or data exfiltration without user awareness.
#### Start the MCP SSE server (terminal_2)
```
python3 server.py
```
#### Start the MCP SSE server (terminal_3)
```
python3 server_rouge.py
```
#### Run the agent (terminal_1)
```
python3 mcp_03.py 
```

### MCP Debugging
https://github.com/kubiosec-ai/mcp-debugging

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
