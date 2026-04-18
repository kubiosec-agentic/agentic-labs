"""
Exercise 4: OpenAI Agents SDK with runtime tool governance.

AGT's blog described runtime policy enforcement for tool calls,
but the current PyPI package (3.1.0) focuses on pre-deployment
checks (prompt defense, supply chain, integrity). This exercise
implements the runtime tool governance pattern described in the
blog using a lightweight Python policy engine.

The agent has four tools: scan_ports, read_logs, deploy_patch,
and wipe_server. The policy allows investigation tools but blocks
remediation tools. This models the common pattern: "investigate
autonomously, require human approval for destructive actions."

Requires:
    export OPENAI_API_KEY="sk-..."

Run:
    python3 govern_04.py
"""

from __future__ import annotations

import asyncio
import re
import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: set OPENAI_API_KEY first.")

from agents import Agent, Runner, function_tool
from agents.tool import FunctionToolResult


# ===================================================================
# Lightweight tool policy engine
# ===================================================================
# This implements the pattern AGT's blog described: regex-based
# tool name matching with allow/deny rules and an audit trail.

@dataclass
class PolicyRule:
    name: str
    pattern: str        # regex matched against tool name
    action: str         # "allow" or "deny"
    priority: int = 0
    description: str = ""

    def matches(self, tool_name: str) -> bool:
        return bool(re.search(self.pattern, tool_name, re.IGNORECASE))


@dataclass
class ToolPolicy:
    """Simple tool governance policy with regex rules and audit."""

    name: str
    default_action: str = "allow"   # "allow" or "deny"
    rules: list[PolicyRule] = field(default_factory=list)
    audit: list[dict] = field(default_factory=list)

    def evaluate(self, tool_name: str, arguments: str = "") -> dict:
        """Evaluate a tool call against the policy. Returns a decision dict."""
        ts = datetime.now(timezone.utc).isoformat()

        # Check rules in priority order (highest first)
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        for rule in sorted_rules:
            if rule.matches(tool_name):
                decision = {
                    "tool": tool_name,
                    "action": rule.action,
                    "rule": rule.name,
                    "timestamp": ts,
                }
                self.audit.append(decision)
                return decision

        # No rule matched, use default
        decision = {
            "tool": tool_name,
            "action": self.default_action,
            "rule": "default",
            "timestamp": ts,
        }
        self.audit.append(decision)
        return decision


# ===================================================================
# Define the governance policy
# ===================================================================

policy = ToolPolicy(
    name="security-analyst-policy",
    default_action="deny",
    rules=[
        PolicyRule(
            name="allow-investigation",
            pattern=r"^(scan_ports|read_logs)$",
            action="allow",
            priority=100,
            description="Read-only investigation tools are always allowed",
        ),
        PolicyRule(
            name="block-remediation",
            pattern=r"^(deploy_patch|wipe_server)$",
            action="deny",
            priority=200,
            description="Destructive remediation tools need human approval",
        ),
    ],
)


# ===================================================================
# Tool governance guard (decorator for OpenAI Agents SDK)
# ===================================================================

def governed(func):
    """Decorator that checks tool calls against the policy."""
    original = func

    async def wrapper(*args, **kwargs):
        tool_name = original.__name__
        decision = policy.evaluate(tool_name, str(kwargs))

        if decision["action"] == "deny":
            print(f"    [!] BLOCKED: {tool_name} (rule: {decision['rule']})")
            return (
                f"GOVERNANCE BLOCKED: tool '{tool_name}' was denied by "
                f"policy rule '{decision['rule']}'. This operation requires "
                f"human approval. Inform the user."
            )

        print(f"    [+] ALLOWED: {tool_name} (rule: {decision['rule']})")
        return await original(*args, **kwargs)

    wrapper.__name__ = original.__name__
    wrapper.__doc__ = original.__doc__
    wrapper.__wrapped__ = original
    return wrapper


# ===================================================================
# Agent tools
# ===================================================================

@function_tool
@governed
async def scan_ports(target: str) -> str:
    """Scan open ports on a target host."""
    return (
        f"Port scan results for {target}:\n"
        "  22/tcp   open   ssh\n"
        "  80/tcp   open   http\n"
        "  443/tcp  open   https\n"
        "  8080/tcp open   http-alt  (suspicious)\n"
        "  9090/tcp open   unknown   (suspicious)"
    )


@function_tool
@governed
async def read_logs(service: str) -> str:
    """Read recent log entries for a service."""
    return (
        f"Last 5 log entries for '{service}':\n"
        "  [WARN]  Unusual outbound traffic to 185.143.x.x\n"
        "  [ERROR] Authentication failure from 10.0.0.99 (3 attempts)\n"
        "  [WARN]  Port 8080 serving unrecognized binary\n"
        "  [INFO]  SSL certificate valid until 2026-12-01\n"
        "  [ERROR] Kernel module loaded: rootkit_detector flagged suspicious"
    )


@function_tool
@governed
async def deploy_patch(patch_id: str) -> str:
    """Deploy a security patch to the server."""
    return f"Patch {patch_id} deployed successfully."


@function_tool
@governed
async def wipe_server(target: str) -> str:
    """Wipe and reimage a compromised server."""
    return f"Server {target} wiped and reimaged."


# ===================================================================
# Agent
# ===================================================================

sec_agent = Agent(
    name="Security Analyst",
    instructions=(
        "You are a security analyst. You can scan ports, read logs, "
        "deploy patches, and wipe compromised servers. Investigate the "
        "situation first, then take remediation action. If a tool call "
        "is blocked by governance, explain what happened and recommend "
        "the user approve the action manually."
    ),
    tools=[scan_ports, read_logs, deploy_patch, wipe_server],
)


# ===================================================================
# Run
# ===================================================================

async def main() -> None:
    print("=" * 64)
    print("  Security Analyst with Tool Governance")
    print("=" * 64)
    print()
    print("Policy: investigation tools allowed, remediation tools blocked.")
    print()

    prompts = [
        "Investigate host 10.0.0.42: scan its ports and check the nginx logs.",
        "Deploy patch CVE-2026-1234 to host 10.0.0.42 and then wipe server 10.0.0.42.",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Prompt {i} ---")
        print(f"User: {prompt}")
        try:
            result = await Runner.run(sec_agent, prompt)
            print(f"\nAgent: {result.final_output}")
        except Exception as exc:
            print(f"\nError: {exc}")

    # --- Audit trail ---
    print()
    print("-" * 64)
    print("  Audit trail")
    print("-" * 64)
    for entry in policy.audit:
        icon = "[+]" if entry["action"] == "allow" else "[!]"
        print(f"  {icon} {entry['action'].upper():5s}  {entry['tool']:15s}  "
              f"rule={entry['rule']}")

    allowed = sum(1 for e in policy.audit if e["action"] == "allow")
    denied = sum(1 for e in policy.audit if e["action"] == "deny")
    print(f"\n  Total: {len(policy.audit)}  "
          f"Allowed: {allowed}  Denied: {denied}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
