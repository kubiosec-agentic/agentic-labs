"""Response sub-agent: playbook selection and action execution."""

import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ...tools import getPlaybookTool, responseExecutionTool
from .prompt import agent_instructions

response_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.0-flash"),
    name="response_agent",
    description="Recommends and triggers incident response actions",
    instruction=agent_instructions,
    tools=[FunctionTool(responseExecutionTool), FunctionTool(getPlaybookTool)],
    output_key="response_agent_output",
)
