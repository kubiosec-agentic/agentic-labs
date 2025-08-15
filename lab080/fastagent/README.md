# FastAgent Examples

This directory contains various examples demonstrating the capabilities of [FastAgent](https://fast-agent.ai/), a framework for building AI agents with Model Context Protocol (MCP) integration.

## Quick Start

### Prerequisites
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Create a bare `pyproject.toml`
uv init --bare

# Install FastAgent
uv add fast-agent-mcp
```

### Running Examples
Each example directory contains its own setup instructions. Generally:
```bash
cd exampleX
uv venv
uv sync
# uv pip install <dependencies>
uv run agent.py
```

## Examples Overview

### Example 1: Interactive Agent
- **File**: `example1/agent.py`
- **Purpose**: Basic interactive agent with chat interface
- **Features**: Simple FastAgent setup with interactive prompt
- **Use Case**: Getting started with FastAgent basics

### Example 2: XSS Learning Agent  
- **File**: `example2/agent.py`
- **Purpose**: Educational security testing agent for XSS detection
- **Features**: Remote instruction loading, security research focus
- **Use Case**: Learning about web application security testing (defensive)

### Example 3: YouTube Transcriber
- **File**: `example3/agent.py`  
- **Purpose**: YouTube video transcription and analysis
- **Features**: MCP server integration (youtube_transcribe, exa_search)
- **Use Case**: Content analysis and transcription workflows

### Example 4: Agent Chaining
- **File**: `example4/agent.py`
- **Purpose**: Demonstrates agent chaining for complex workflows
- **Features**: Multi-step agent pipeline, URL fetching and social media post generation
- **Use Case**: Content processing pipelines


## Configuration
Some examples include configuration files.<br>
Main configuration with server and model settings
- `fastagent.config.yaml`
<br>Sensitive configuration (API keys, tokens) keys can be stored in
- `fastagent.secrets.yaml`
<br>Both files are merged upon running the agent

## Resources

- **Official Documentation**: https://fast-agent.ai/
- **LLM-friendly docs**: https://fast-agent.ai/llms.txt
- **Repository**: FastAgent GitHub repository
