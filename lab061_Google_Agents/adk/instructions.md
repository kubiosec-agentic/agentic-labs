# Creating a new ADK agent

These are working examples of Google ADK agents using the Google Generative AI API.

## Skeleton

Every ADK agent lives in its own subdirectory under `adk/` and requires at minimum two files.

### 1. `.env` (in the `adk/` root, shared by all agents)

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. `__init__.py`

```python
from . import agent
```

### 3. `agent.py`

Define a `root_agent` at module level. `adk web` discovers it automatically.

**Example: agent with Python function tools**

```python
import os
from google.adk.agents import Agent

def my_tool(query: str) -> str:
    """Look up something. ADK infers the schema from type hints and docstring.

    Args:
        query: The search query.
    """
    return f"Result for {query}"

root_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.0-flash"),
    name="my_agent",
    instruction="Help the user by calling your tools.",
    tools=[my_tool],
)
```

ADK wraps plain Python functions as tools automatically. Type hints must be specific (use `list[str]`, not bare `list`). The docstring becomes the tool description.
