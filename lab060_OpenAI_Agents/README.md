# LAB060: Multi-Agent Orchestration & OpenAI APIs
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
source .lab060/bin/activate
```

## Lab instructions

#### Example 1: Simple Synchronous Agent
Basic agent using the OpenAI agents framework with synchronous execution.
```bash
python3 agent_01.py
```

#### Example 2: Multi-Agent Language Handoff  
Demonstrates agent orchestration with language detection. The triage agent routes Spanish/English requests to specialized agents.
```bash
python3 agent_02.py
```

#### Example 3: Agent with Function Tools
Tool-enabled agent that can call custom functions. Includes a weather lookup tool with async execution.
```bash
python3 agent_03.py
```

#### Example 4: Agent Output Guardrails
Shows how to implement content filtering using output guardrails. Detects and blocks mathematical content.
```bash
python3 agent_04.py
```

#### Example 5: OpenAI Responses API for Security Analysis
Uses OpenAI's Responses API (direct client approach) to analyze security traces and network captures.
```bash
python3 agent_05.py
```

#### Example 6: Security Analysis with Agents SDK
Same security analysis functionality but implemented using OpenAI Agents SDK with JSON output and line number references.
```bash
python3 agent_06.py
```

#### Example 7: Multi-Agent Security Analysis Pipeline
Advanced multi-agent orchestration demonstrating sophisticated agent workflows with three specialized agents:

**🔄 Agent Architecture:**
- **Analyzer Agent**: Performs detailed sysdig trace analysis with line number extraction
- **Summary Agent**: Converts technical analysis into markdown documentation (summary.md)
- **JSON Agent**: Structures findings into comprehensive JSON format (details.json)

**📊 Key Capabilities:**
- Agent handoff and result passing between specialized agents
- Automatic file generation with error handling
- Multi-format output (human-readable + machine-readable)
- Progress tracking through complex workflows
- Line number referencing for forensic review

**💾 Generated Artifacts:**
- `summary.md`: Executive summary and key findings in markdown format
- `details.json`: Structured analysis with metadata, line references, and evidence

```bash
python3 agent_07.py
```

**Expected Output Structure:**
```json
{
  "metadata": {"analysis_timestamp": "...", "trace_file": "..."},
  "summary": "Brief process overview",
  "process_info": {"command": "curl", "pid": "108261", "line_numbers": [1051]},
  "phases": [{"phase": "Library Loading", "line_range": {"start": 1051, "end": 1200}}],
  "network_activity": {"dns_queries": "...", "line_references": [2500, 2501]},
  "security_observations": [{"observation": "...", "line_number": 1234, "evidence": "..."}]
}
```

## Cleanup environment
```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
