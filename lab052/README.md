![OpenAI](https://img.shields.io/badge/OpenAI-lightblue)
![Tools](https://img.shields.io/badge/Tools-purple)
![Python](https://img.shields.io/badge/Python-blue) 


# LAB052: OpenAI Function Calling and Tool Integration
## Introduction
This lab demonstrates OpenAI's function calling capabilities with custom tools. You'll learn:
- Directory analysis with function calling
- SQL simulation with tool integration
- Advanced tool execution patterns
- API call inspection using mitmproxy

Perfect for understanding how to integrate custom tools with OpenAI's chat completion API.

## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab052/bin/activate
```

## Lab instructions
#### Example 1: Directory Analysis Tool
This script demonstrates OpenAI function calling with a directory analysis tool. The model can automatically call the `summarize_directory` function to analyze file types in any directory path.
```
python3 OA_01.py
```

#### Example 2: SQL Simulation with Custom Tools
This example shows advanced tool integration with a simulated SQL database. It demonstrates:
- Custom tool schema definition
- Local function execution
- Tool result processing
- Multi-step conversation flow
```
python3 OA_02.py
```

#### Example 3: DevSecOps Dependency Vulnerability Scanner
This example demonstrates a security-focused tool that scans Python dependencies for known vulnerabilities. It showcases:
- Integration with security scanning tools (pip-audit)
- Fallback manual vulnerability checking
- Security-focused system prompts
- DevSecOps workflow automation
```
python3 OA_03.py
```

#### Example 4: API Call Inspection with Mitmproxy
This setup enables deep inspection of OpenAI API calls by routing them through a local MITM proxy in reverse mode.

#### Open a new terminal_2
```
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 127.0.0.1:8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --mode reverse:https://api.openai.com:443
```
You can now connect to `http://127.0.0.1:8081/?token=<see_your_terminal>`

#### Continue in terminal_1
```
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
```
```
python3 OA_02.py
```

## Cleanup environment
```
unset OPENAI_BASE_URL
```
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
