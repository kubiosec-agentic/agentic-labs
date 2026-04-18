"""
Exercise 6: MCP Guardian + Agent Governance Toolkit (combined).

This exercise combines two complementary projects:

  - MCP Guardian (https://github.com/mcp-guardian/mcp-guardian):
    3-tier validation for MCP tool calls: deterministic rules,
    LLM-based intent evaluation, and human escalation.

  - Microsoft AGT (https://github.com/microsoft/agent-governance-toolkit):
    PolicyEvaluator for rich deterministic rule matching, and
    Merkle-chained audit logs for tamper-proof decision trails.

The idea: use AGT's PolicyEvaluator as an enhanced Tier-1 engine
inside MCP Guardian's validation pipeline, and feed every Guardian
decision into AGT's AuditLog for a tamper-proof record.

This is a proof-of-concept that runs without an MCP server or LLM.
It simulates tool calls and shows the combined enforcement +
audit pipeline.

Run:
    python3 govern_06_guardian.py
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# AGT: deterministic policy engine + tamper-proof audit
# ---------------------------------------------------------------------------
from agent_os.policies import (
    PolicyEvaluator,
    PolicyDocument,
    PolicyRule,
    PolicyCondition,
    PolicyAction,
    PolicyOperator,
    PolicyDefaults,
)
from agentmesh.governance.audit import AuditLog, AuditEntry

# ---------------------------------------------------------------------------
# MCP Guardian: 3-tier validation pipeline
# ---------------------------------------------------------------------------
from mcp_guardian import IntentPolicy


# ===================================================================
# 1. AGT policy: rich deterministic rules
# ===================================================================
# This replaces Guardian's built-in allowlist/blocklist with AGT's
# more expressive rule engine (regex matching, priorities, etc.).

agt_evaluator = PolicyEvaluator(policies=[PolicyDocument(
    name="guardian-enhanced-policy",
    version="1.0",
    defaults=PolicyDefaults(action=PolicyAction.ALLOW),
    rules=[
        # Block destructive tools by name pattern
        PolicyRule(
            name="block-destructive-tools",
            description="Block tools that modify or delete resources",
            condition=PolicyCondition(
                field="tool_name",
                operator=PolicyOperator.MATCHES,
                value=r"(?i)(delete|remove|drop|wipe|destroy|write|execute|shell)",
            ),
            action=PolicyAction.DENY,
            priority=100,
        ),
        # Block dangerous argument patterns
        PolicyRule(
            name="block-dangerous-args",
            description="Block calls containing shell injection or SQL injection",
            condition=PolicyCondition(
                field="arguments",
                operator=PolicyOperator.MATCHES,
                value=r"(rm -rf|DROP TABLE|;.*sh\b|&&|\.\.\/)",
            ),
            action=PolicyAction.DENY,
            priority=200,
        ),
        # Block path traversal in any argument
        PolicyRule(
            name="block-path-traversal",
            description="Block arguments attempting directory traversal",
            condition=PolicyCondition(
                field="arguments",
                operator=PolicyOperator.MATCHES,
                value=r"\.\./",
            ),
            action=PolicyAction.DENY,
            priority=150,
        ),
    ],
)])


# ===================================================================
# 2. AGT audit log: Merkle-chained, tamper-proof
# ===================================================================
audit_log = AuditLog()


# ===================================================================
# 3. MCP Guardian policy: defines the intent-level rules
# ===================================================================
# Guardian's IntentPolicy handles Tier 2 (LLM evaluation) and
# Tier 3 (human escalation). Here we define the policy but use
# AGT for the Tier 1 deterministic check instead of Guardian's
# built-in allowlist.

guardian_policy = IntentPolicy(
    name="read-only-enhanced",
    allowed_tools=["read_*", "list_*", "search_*", "get_*"],
    forbidden_tools=["write_*", "execute_*", "delete_*"],
    constraints=[
        "Do not access files outside the working directory",
        "Do not execute arbitrary commands",
        "Do not modify or delete any resources",
    ],
    escalation_threshold=0.7,
)


# ===================================================================
# 4. Combined validation pipeline
# ===================================================================

class GuardianWithAGT:
    """
    Combined enforcement pipeline:

    Tier 1 (deterministic): AGT PolicyEvaluator
      - Rich regex-based rules, priorities, pattern matching
      - Sub-millisecond evaluation
      - If DENY: stop immediately, log to AGT audit

    Tier 2 (intent check): MCP Guardian IntentPolicy
      - Checks tool name against allowed/forbidden glob patterns
      - In production, adds LLM-based intent evaluation
      - If forbidden: stop, log to AGT audit

    Tier 3 (escalation): MCP Guardian escalation
      - If confidence < threshold, escalate to human
      - Not demonstrated here (requires interactive setup)

    Every decision is recorded in AGT's Merkle-chained audit log.
    """

    def __init__(self, agt_eval: PolicyEvaluator, policy: IntentPolicy, audit: AuditLog):
        self.agt_eval = agt_eval
        self.policy = policy
        self.audit = audit

    async def check(self, tool_name: str, arguments: dict) -> dict:
        """Run the combined validation pipeline for a tool call."""
        args_str = json.dumps(arguments)
        timestamp = datetime.now(timezone.utc).isoformat()

        # --- Tier 1: AGT deterministic policy ---
        agt_result = self.agt_eval.evaluate({
            "tool_name": tool_name,
            "arguments": args_str,
        })

        if agt_result.action == PolicyAction.DENY:
            rule_name = agt_result.matched_rule.name if agt_result.matched_rule else "unknown"
            decision = {
                "tool": tool_name,
                "action": "DENY",
                "tier": "Tier-1 (AGT PolicyEvaluator)",
                "reason": f"Matched rule: {rule_name}",
                "timestamp": timestamp,
            }
            self.audit.append(AuditEntry(
                action="tool_call_blocked",
                agent_id="guardian-agt-combined",
                details=decision,
            ))
            return decision

        # --- Tier 2: MCP Guardian intent check ---
        # Check against Guardian's glob-based allowed/forbidden lists
        import fnmatch

        is_forbidden = any(
            fnmatch.fnmatch(tool_name, pat)
            for pat in self.policy.forbidden_tools
        )
        is_allowed = any(
            fnmatch.fnmatch(tool_name, pat)
            for pat in self.policy.allowed_tools
        )

        if is_forbidden:
            decision = {
                "tool": tool_name,
                "action": "DENY",
                "tier": "Tier-2 (MCP Guardian IntentPolicy)",
                "reason": f"Tool matches forbidden pattern",
                "timestamp": timestamp,
            }
            self.audit.append(AuditEntry(
                action="tool_call_blocked",
                agent_id="guardian-agt-combined",
                details=decision,
            ))
            return decision

        if not is_allowed:
            decision = {
                "tool": tool_name,
                "action": "DENY",
                "tier": "Tier-2 (MCP Guardian IntentPolicy)",
                "reason": "Tool not in allowed list",
                "timestamp": timestamp,
            }
            self.audit.append(AuditEntry(
                action="tool_call_blocked",
                agent_id="guardian-agt-combined",
                details=decision,
            ))
            return decision

        # --- Passed all tiers ---
        decision = {
            "tool": tool_name,
            "action": "ALLOW",
            "tier": "all",
            "reason": "Passed Tier-1 (AGT) and Tier-2 (Guardian)",
            "timestamp": timestamp,
        }
        self.audit.append(AuditEntry(
            action="tool_call_allowed",
            agent_id="guardian-agt-combined",
            details=decision,
        ))
        return decision


# ===================================================================
# 5. Demo: run test scenarios
# ===================================================================

async def main() -> None:
    print("=" * 64)
    print("  MCP Guardian + Agent Governance Toolkit (combined)")
    print("=" * 64)
    print()
    print("Tier 1: AGT PolicyEvaluator (regex rules, pattern matching)")
    print("Tier 2: MCP Guardian IntentPolicy (glob allow/forbid lists)")
    print("Audit:  AGT Merkle-chained audit log")
    print()

    pipeline = GuardianWithAGT(agt_evaluator, guardian_policy, audit_log)

    scenarios = [
        # (tool_name, arguments, description)
        ("read_file", {"path": "/docs/security_policy.md"},
         "Read a file (allowed by both tiers)"),

        ("list_directory", {"path": "/docs"},
         "List a directory (allowed by both tiers)"),

        ("search_docs", {"query": "authentication best practices"},
         "Search docs (allowed by both tiers)"),

        ("delete_file", {"path": "/tmp/old_logs.txt"},
         "Delete a file (blocked by AGT Tier-1: name matches 'delete')"),

        ("execute_shell", {"command": "ls /tmp"},
         "Execute shell (blocked by AGT Tier-1: name matches 'execute')"),

        ("read_file", {"path": "../../etc/passwd"},
         "Path traversal (blocked by AGT Tier-1: argument matches '../')"),

        ("read_file", {"path": "/data/records.db; rm -rf /"},
         "Injection in argument (blocked by AGT Tier-1: 'rm -rf' pattern)"),

        ("upload_document", {"file": "report.pdf"},
         "Upload doc (passes AGT, blocked by Guardian: not in allowed list)"),

        ("write_config", {"key": "debug", "value": "true"},
         "Write config (blocked by AGT Tier-1: name matches 'write')"),

        ("get_status", {"service": "api-gateway"},
         "Get status (allowed by both tiers)"),
    ]

    for i, (tool, args, desc) in enumerate(scenarios, 1):
        result = await pipeline.check(tool, args)
        status = "ALLOW" if result["action"] == "ALLOW" else "DENY"
        icon = "[+]" if status == "ALLOW" else "[!]"
        print(f"  {i:2d}. {icon} {status:5s}  {tool}({json.dumps(args)})")
        print(f"              {result['tier']}: {result['reason']}")
        print()

    # --- Print audit trail ---
    print("-" * 64)
    print("  Merkle-chained audit trail")
    print("-" * 64)
    entries = audit_log.entries()
    for entry in entries:
        details = entry.details
        tool = details.get("tool", "?")
        action = details.get("action", "?")
        tier = details.get("tier", "?")
        print(f"  [{entry.timestamp}] {action:5s} {tool:20s} via {tier}")

    print()
    print(f"  Total entries: {len(entries)}")
    print(f"  Chain valid:   {audit_log.verify()}")
    print()

    # --- Stats ---
    allowed = sum(1 for e in entries if e.details.get("action") == "ALLOW")
    denied = sum(1 for e in entries if e.details.get("action") == "DENY")
    print(f"  Allowed: {allowed}  |  Denied: {denied}  |  "
          f"Violation rate: {denied / len(entries) * 100:.0f}%")
    print()


if __name__ == "__main__":
    asyncio.run(main())
