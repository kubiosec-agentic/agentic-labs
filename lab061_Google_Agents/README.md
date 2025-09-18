# LAB061: Google ADK
## Introduction
This lab explores both the **OpenAI agents framework** and **OpenAI Responses API** for building structured AI agents. You'll learn to:
- Create basic agents with synchronous and asynchronous execution
- Implement agent handoff based on input language detection
- Attach custom tools to agents for function calling  
- Enforce output guardrails to filter or block certain content
- Compare OpenAI Responses API vs Agents SDK approaches
- Build security analysis agents with specialized tools

Perfect for understanding different agent orchestration patterns and OpenAI's API capabilities.
## Set up your environment
### Prerequisites
- Python 3.8+ with pip  
- OpenAI API key with access to agents framework and Responses API

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab061/bin/activate
```

## Lab instructions

### Google Agent Development Kit (ADK)
This lab also includes Google's Agent Development Kit examples in the `adk/` directory:
- **Flight Assistant**: AI agent for flight booking and scheduling  
- **Google Search Agent**: Web search integration with Google APIs
- **MCP Agent**: Model Context Protocol implementation
- **Multi-Tool Agent**: Agent with multiple tool integrations

**Setup ADK (Optional):**
```bash
cd adk
pip install -r requirements.txt
export GOOGLE_API_KEY="xxxxxxxxx"
export SERP_API_KEY="xxxxxxxxx"  # From https://serpapi.com/
adk web
```

**Resources:**
- [ADK Documentation](https://google.github.io/adk-docs/get-started/quickstart/)
- [ADK Sample Agents](https://github.com/google/adk-samples)

## Cleanup environment
```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
