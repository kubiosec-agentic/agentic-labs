"""Cyber Guardian: multi-agent cybersecurity incident response.

Orchestrates 4 specialized sub-agents (triage, threat intel, investigation,
response) using ADK's built-in planner with extended thinking. The planner
reasons about which sub-agent to delegate to at each step.

Uses mock tools that return realistic simulated data, so no external
infrastructure (BigQuery, SIEM, SOAR) is needed.

Try this sample alert in the adk web UI:
    "ALERT: IOC_MATCH detected on host srv-web-prod-01 by user svc-apache.
     Outbound connection to 185.220.101.42:443 flagged by network IDS.
     Process: certutil.exe downloading from 185.220.101.42."

Based on google/adk-samples/cyber-guardian-agent (Apache 2.0).
"""

import logging
import os

from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types

from .prompt import root_agent_instruction
from .sub_agents.investigation.agent import investigation_agent
from .sub_agents.response.agent import response_agent
from .sub_agents.threatintel.agent import threatintel_agent
from .sub_agents.triage.agent import triage_agent

logging.basicConfig(level=logging.INFO)

root_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.0-flash"),
    name="cyber_guardian_orchestrator",
    description="Orchestrates a multi-agent cybersecurity incident response workflow",
    instruction=root_agent_instruction,
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=512,
        )
    ),
    sub_agents=[threatintel_agent, investigation_agent, triage_agent, response_agent],
)
