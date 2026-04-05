![MCP](https://img.shields.io/badge/MCP-purple) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Python](https://img.shields.io/badge/Python-blue) ![Security](https://img.shields.io/badge/Security-red)

# LAB070: Model Context Protocol

## Introduction
This lab introduces the Model Context Protocol (MCP), a secure standard for connecting AI agents to tools and data sources. You'll explore:
- MCP transports: stdio and streamable HTTP for agent-tool communication
- Building agents that use tools over MCP servers
- Simulating MCP shadowing and agent hijacking attacks to study security risks
- Debugging tools and best practices via the MCP debugging suite

Ideal for understanding secure tool orchestration in AI systems and the risks of compromised environments.
## List of MCP servers
- https://github.com/docker/mcp-servers

## Set up your environment

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab070/bin/activate
```

## Lab instructions

### MCP stdio
The Model Context Protocol (MCP) stdio transport is a communication method that enables local AI applications to interact with tools or data sources by spawning subprocesses and exchanging JSON-RPC messages via standard input and output streams.
```bash
python3 mcp_01_stdio.py
```

### MCP Streamable HTTP
The Model Context Protocol (MCP) Server-Sent Events (SSE) transport mode has been deprecated (though still widely used) and replaced by the streamable HTTP transport mode. This new mode is the preferred communication method, allowing AI applications to interact with tools and data sources by maintaining a persistent HTTP connection for server-to-client streaming, while using HTTP POST requests for client-to-server communication.

#### Start the MCP server (terminal_2)
```bash
python3 server_streamable.py
```

#### Run the agent (terminal_1)
```bash
python3 mcp_02_streamable.py
```
### MCP [SECURITY] (Shadowing attack)
A Model Context Protocol (MCP) shadowing attack is a sophisticated exploit where a malicious tool covertly alters the behavior of trusted tools within an AI agent's environment, leading to unauthorized actions or data exfiltration without user awareness.

#### Start the MCP SSE server (terminal_2)
```bash
python3 server_streamable.py
```

#### Start the MCP server (terminal_3)
```bash
python3 server_rogue_streamable.py
```

#### Run the agent (terminal_1)
Model Context Protocol (MCP) shadowing attack
```bash
python3 mcp_03_streamable.py
```

### MCP [SECURITY] (Indirect Prompt Injection)
#### Run the agent (terminal_1)
Indirect Prompt Injection (Agent Hijacking)
```bash
python3 mcp_04_streamable.py
```
### Youtube Transcriber
You can obtain a token from https://mcp-cloud.ai/ <br>
Deploy the youtube-transcribe MCP server.<br>

```bash
export MCPCLOUD_API_TOKEN="xxxxxx"
```
```bash
export MCP_SSE_URL="xxxxxxx"
```
```bash
python3 mcp_05_youtube-transcribe.py
```

### MCP Debugging
See https://github.com/mcp-firewall/mcp-debugging <br>

Use the following example to analyse the entire Agentic flow using mitmproxy.<br>
```bash
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1/"
```
```bash
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 8081:8081 \
    -p 8089:8089 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --set block_global=false \
        --mode reverse:https://api.openai.com:443@8080 \
        --mode reverse:http://192.168.0.246:8000@8089
```
```bash
python mcp_06_streamable_mitm.py
```

## Cleanup environment
```bash
deactivate
```
```bash
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
