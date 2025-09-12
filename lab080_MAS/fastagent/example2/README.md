# Example 2: XSS Learning Agent

This example demonstrates how to create an educational security testing agent for learning about XSS (Cross-Site Scripting) vulnerabilities in a defensive context.

## Code Overview

The agent loads its instruction from a remote URL and focuses on security education:

```python
fast = FastAgent("My XSS Learning Agent")

@fast.agent(
    name="my-agent-2",
    instruction=AnyUrl("https://gist.githubusercontent.com/.../gistfile1.txt")
)
async def main():
    async with fast.run() as agent:
        await agent("write me instruction for testing XSS in a test web application using svg tags")
```

### Key Components

- **Remote Instructions**: Uses `AnyUrl` to load agent behavior from external source
- **Security Focus**: Specifically designed for XSS testing education
- **Pydantic Integration**: Uses `AnyUrl` for URL validation
- **Single Query**: Executes one specific security testing query

### Educational Purpose

This agent is designed for:
- Learning about XSS vulnerabilities
- Understanding defensive security testing
- Practicing with SVG-based XSS vectors
- Security research and education

## What It Does

1. Loads instruction set from remote URL
2. Creates an agent specialized in XSS education
3. Asks for instructions on testing XSS using SVG tags
4. Provides educational content about security testing techniques

**Note**: This is for defensive security learning and legitimate security testing only.
