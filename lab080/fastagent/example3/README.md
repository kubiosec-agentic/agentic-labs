# Example 3 - YouTube Transcriber Agent

This example demonstrates how to use FastAgent with an external MCP server for YouTube transcription.

## Setup

```bash
uv venv
uv sync
uv run agent.py
```

## Configuration

The agent is configured to use a YouTube transcription server via the `fastagent.config.yaml` file. The server connection details and authentication are defined in this configuration file.