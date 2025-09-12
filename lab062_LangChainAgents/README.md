![OpenAI](https://img.shields.io/badge/OpenAI-lightblue)
![LangChain](https://img.shields.io/badge/LangChain-lightgrey)
![Tools](https://img.shields.io/badge/Tools-purple)
![Agents](https://img.shields.io/badge/Agents-orange)
![Python](https://img.shields.io/badge/Python-blue)
![Experimental](https://img.shields.io/badge/Experimental-red)

# LAB062: LangChain ReAct Agents (Experimental)

> ⚠️ **EXPERIMENTAL LAB WARNING**  
> This lab uses `langchain_experimental` which contains potentially dangerous code.  
> While still supported (as of 2025), it's designed for research and experimental use.  
> **DO NOT** deploy experimental code to production without proper security review.

> 📚 **MIGRATION GUIDANCE**  
> LangChain is transitioning experimental features toward [LangGraph](https://python.langchain.com/docs/langgraph/) and newer agent patterns.  
> See [LangChain Migration Guide](https://github.com/langchain-ai/langchain/blob/master/MIGRATE.md) and [Deprecations](https://python.langchain.com/docs/versions/v0_2/deprecations/) for migration paths.  
> Use `langchain-cli migrate` to update deprecated imports automatically.

## Introduction
This lab focuses specifically on LangChain ReAct agents using experimental features. You'll explore:
- LangChain ReAct agents with and without tools
- Python REPL tool integration (potentially unsafe)
- Wikipedia integration for research queries  
- CTF-style agent challenges
- Agent execution patterns and debugging

Perfect for understanding LangChain's agent capabilities while learning about experimental framework risks.
## Set up your environment
### Prerequisites  
- Python 3.8+ with pip
- OpenAI API key
- **Security Warning**: This lab uses experimental LangChain features

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab053/bin/activate
```
```bash
pip install -r requirements.txt
```

### Suppress LangSmith Warnings (Optional)
To avoid **LangSmith** warnings from LangChain's monitoring framework:
```bash
export LANGCHAIN_TRACING_V2="false"
export LANGCHAIN_API_KEY=""
```

## Lab instructions

#### Example 1: ReAct Agent without Tools
Basic LangChain ReAct agent using GPT-3.5-turbo without any tool access. Demonstrates pure reasoning workflow.
```bash
python3 LA_01.py
```

#### Example 2: ReAct Agent with Python REPL Tool  
> ⚠️ **SECURITY WARNING**: Uses PythonREPLTool which can execute arbitrary Python code

LangChain ReAct agent with access to Python REPL for mathematical computations. Uses experimental tools.
```bash
python3 LA_02.py
```

#### Example 3: CTF Challenge Agent (API Mode)
Agent-based CTF middleware exposing OpenAI-compatible API. Test agent security and prompt injection.
```bash
python3 LA_03.py
```

Test in **terminal_2**:
```bash
curl -XPOST http://127.0.0.1:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_key" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "What is the SQRT of 12345"}]
  }'
```

#### Example 4: Wikipedia Research Agent
LangChain ReAct agent with Wikipedia integration for research queries. Demonstrates external knowledge source integration.
```bash
python3 LA_04.py  
```

#### Example 5: LangChain Chain (Advanced)
Advanced LangChain chain example.
```bash
python3 LA_05.py
```

## Security Notes for Experimental Features

**🔒 LangChain Experimental Security Considerations:**
- **PythonREPLTool**: Can execute arbitrary Python code - sandbox recommended
- **Agent Execution**: May follow unexpected reasoning paths
- **External Tools**: Wikipedia and web access may leak information
- **Prompt Injection**: Agents vulnerable to malicious prompts

**✅ Safe Usage Guidelines:**
- Run in isolated/sandboxed environments only
- Never expose experimental agents to untrusted input
- Monitor agent actions and tool usage
- Review security team before production use

## Deprecation Timeline & Migration Path

**📅 LangChain Experimental Status (2025):**
- **Current Status**: Active but experimental (version 0.3.x)
- **Migration Target**: [LangGraph](https://python.langchain.com/docs/langgraph/) for complex agent orchestration
- **Legacy Support**: Maintained until LangChain 1.0.0 release
- **Security Concerns**: Features with CVEs moved to experimental package in 2023

**🔄 Migration Strategy:**
1. **Immediate**: Use this lab for learning experimental patterns
2. **Near-term**: Migrate to `create_react_agent()` from core LangChain
3. **Long-term**: Transition to LangGraph for production agent workflows

**📖 Key Resources:**
- [LangChain v0.3 Migration Guide](https://python.langchain.com/docs/versions/v0_3/)
- [Deprecations List](https://python.langchain.com/docs/versions/v0_2/deprecations/)
- [GitHub Migration Discussion](https://github.com/langchain-ai/langchain/discussions/18547)

**⚙️ Migration Tools:**
```bash
# Install migration CLI
pip install langchain-cli

# Preview migration changes
langchain-cli migrate --diff /path/to/your/code

# Interactive migration
langchain-cli migrate --interactive /path/to/your/code
```

## Cleanup environment
```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
