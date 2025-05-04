# LAB07
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
### MCP stdio
```
python3 mcp_01.py
```
### MCP SSE
The script starts by connecting to a MCP SSE server using main(), then calls the run() function, which creates an agent and sends it a few questions that require calling external tools (like adding numbers or checking the weather). The agent uses those tools via the server, and the final answers are printed to the console.

#### Start the MCP SSE server
```
python3 server.py
```
#### Run the agent
```
python3 mcp_02.py
```
### MCP Debugging
https://github.com/kubiosec-ai/mcp-debugging

## Cleanup environment
```
./lab_cleanup.sh
```
