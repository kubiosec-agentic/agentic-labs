"""Threat intel sub-agent: enriches IOCs with threat intelligence."""

import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ...tools import threatIntelQueryTool
from .prompt import agent_instructions

threatintel_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.0-flash"),
    name="threat_intel_agent",
    description="Enriches IPs, domains, and hashes with threat intelligence context",
    instruction=agent_instructions,
    tools=[FunctionTool(threatIntelQueryTool)],
    output_key="threatintel_agent_output",
)
