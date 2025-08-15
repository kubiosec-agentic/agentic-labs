# Example 3: YouTube Transcriber Agent

This example demonstrates how to use FastAgent with external MCP servers for YouTube video transcription and web search capabilities.

## Code Overview

The agent integrates with multiple MCP servers to provide comprehensive video analysis:

```python
fast = FastAgent("My YouTube Transcriber Agent")

@fast.agent(servers=["youtube_transcribe", "exa_search"])
async def main():
    async with fast.run() as agent:
        await agent("Find me a youtube video about the latest advancements in OpenAI and transcribe it in a detailed way.")
```

### Key Components

- **MCP Server Integration**: Uses `youtube_transcribe` and `exa_search` servers
- **Multi-step Workflow**: Searches for videos AND transcribes them
- **Detailed Analysis**: Requests comprehensive transcription output
- **External Service Coordination**: Orchestrates multiple external tools

### MCP Servers Used

1. **youtube_transcribe**: Handles YouTube video transcription
   - Extracts audio from videos
   - Converts speech to text
   - Provides detailed transcripts

2. **exa_search**: Provides web search capabilities
   - Finds relevant YouTube videos
   - Searches based on content topics
   - Helps locate specific content

## Configuration

The agent relies on configuration files for MCP server setup:

- **`fastagent.config.yaml`**: Main configuration with server endpoints and settings
- **`fastagent.secrets.yaml`**: API keys and authentication tokens for external services

### Server Configuration
The MCP servers are configured as remote SSE (Server-Sent Events) endpoints that provide real-time access to transcription and search services.

## What It Does

1. **Search Phase**: Uses exa_search to find relevant YouTube videos about OpenAI advancements
2. **Transcription Phase**: Uses youtube_transcribe to extract and transcribe video content
3. **Analysis Phase**: Provides detailed summary and insights from the transcribed content
4. **Integrated Workflow**: Seamlessly combines search and transcription for comprehensive results

This example shows how FastAgent can coordinate multiple external services to create powerful, multi-step workflows for content analysis and research.
