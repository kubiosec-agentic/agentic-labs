"""Cyber Guardian: multi-agent cybersecurity incident response.

The orchestrator has 6 tools representing the stages of incident response:
triage, threat intel enrichment, investigation, playbook lookup, action
execution, and incident creation. It chains them based on alert classification.

Uses mock tools that return realistic simulated data, so no external
infrastructure (BigQuery, SIEM, SOAR) is needed.

Try this sample alert in the adk web UI:
    "ALERT: IOC_MATCH detected on host srv-web-prod-01 by user svc-apache.
     Outbound connection to 185.220.101.42:443 flagged by network IDS.
     Process: certutil.exe downloading from 185.220.101.42."

Based on google/adk-samples/cyber-guardian-agent (Apache 2.0).
"""

import os
from google.adk.agents import Agent

from .tools import (
    triage_alert,
    enrich_threat_intel,
    investigate_alert,
    get_response_playbook,
    execute_response_action,
    create_incident,
)

ORCHESTRATOR_INSTRUCTION = """
You are a cybersecurity incident response orchestrator. When you receive a
raw alert, parse it, classify it, and use your tools to run the full
incident response workflow.

WORKFLOW:

Step 1 - Parse and classify:
    Determine the alert type (IOC_MATCH, EDR_DETECTION, PHISHING_EMAIL).
    Extract entities: hostname, user, IP addresses, processes, IOCs.

Step 2 - Triage (always first):
    Call triage_alert with hostname and alert_type.
    If is_duplicate is true, STOP and report to the user.

Step 3 - Threat intel and investigation:
    For IOC-heavy alerts (IOC_MATCH, PHISHING_EMAIL):
        Call enrich_threat_intel first with all IOCs (IPs, hashes, domains).
        Then call investigate_alert for deep technical analysis.
    For EDR alerts:
        Call investigate_alert first.
        Then call enrich_threat_intel with any IOCs found.

Step 4 - Response:
    Call get_response_playbook with the identified threat name.
    For actions that do NOT require approval, call execute_response_action.
    For actions that DO require approval, flag them for human review.

Step 5 - Create incident:
    Call create_incident to log the incident for tracking.

Step 6 - Report:
    Present a comprehensive summary with all findings and recommended actions.
    Clearly flag any actions requiring human approval.
"""

root_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.0-flash"),
    name="cyber_guardian_orchestrator",
    description="Cybersecurity incident response orchestrator with mock security tools",
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
