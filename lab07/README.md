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
This example code connects to a MCP SSE server using main() function, that in turn calls the run() function, which creates an agent and sends it a few questions that require calling external tools.

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
