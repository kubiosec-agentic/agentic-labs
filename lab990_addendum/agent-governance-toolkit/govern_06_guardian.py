"""
Exercise 6: MCP Guardian + AGT MCP Governance (combined).

Combines two complementary projects for MCP tool security:

  - MCP Guardian (https://github.com/mcp-guardian/mcp-guardian):
    3-tier validation for MCP tool calls: deterministic rules,
    LLM-based intent evaluation, and human escalation.

  - AGT agent-os-kernel MCP modules:
    - MCPGateway: intercept_tool_call() with policy + deny list +
      rate limiting + argument sanitization
    - MCPSecurityScanner: fingerprints tool definitions and detects
      rug-pull attacks (tool behavior changes after registration)
    - TrustRoot: multi-policy validation engine

The combination:
  Phase 0: MCPSecurityScanner registers tool fingerprints, then
           checks for rug-pull (definition tampering)
  Phase 1: MCPGateway intercepts tool calls (allowed/denied/rate-limited)
  Phase 2: MCP Guardian IntentPolicy.fast_check() for glob-based
           allow/forbid + workflow transition enforcement
  Phase 3: Argument constraint checks (path traversal, etc.)

No API keys needed.

Install (agent-os-kernel is not on PyPI yet):
    pip install "git+https://github.com/microsoft/agent-governance-toolkit.git#subdirectory=packages/agent-os"

Run:
    python3 govern_06_guardian.py
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone

# Suppress sample-rules warnings from AGT
warnings.filterwarnings("ignore", message=".*built-in sample rules.*")

# ---------------------------------------------------------------------------
# AGT: MCP governance primitives
# ---------------------------------------------------------------------------
from agent_os.mcp_gateway import MCPGateway
from agent_os.mcp_security import MCPSecurityScanner
from agent_os.trust_root import GovernancePolicy

# ---------------------------------------------------------------------------
# MCP Guardian: 3-tier validation
# ---------------------------------------------------------------------------
from mcp_guardian import IntentPolicy


# ===================================================================
# 1. AGT: Define governance policy + gateway
# ===================================================================

policy = GovernancePolicy(
    name="mcp-combined-policy",
    allowed_tools=[
        "read_file", "list_directory", "search_docs", "get_status",
    ],
    blocked_patterns=["rm -rf", "DROP TABLE", "shutdown"],
    max_tool_calls=10,
)

gateway = MCPGateway(
    policy=policy,
    denied_tools=["delete_file", "execute_shell", "wipe_server"],
    sensitive_tools=["write_file"],
)


# ===================================================================
# 2. AGT: Register tool fingerprints for rug-pull detection
# ===================================================================

scanner = MCPSecurityScanner()

TOOL_REGISTRY = [
    {
        "name": "read_file",
        "description": "Read a file by path and return its contents.",
        "schema": {"type": "object", "properties": {"path": {"type": "string"}}},
    },
    {
        "name": "write_file",
        "description": "Write content to a file path.",
        "schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
    },
    {
        "name": "search_docs",
        "description": "Search documentation by keyword.",
        "schema": {"type": "object", "properties": {"query": {"type": "string"}}},
    },
    {
        "name": "delete_file",
        "description": "Delete a file from the filesystem.",
        "schema": {"type": "object", "properties": {"path": {"type": "string"}}},
    },
    {
        "name": "execute_shell",
        "description": "Execute a shell command on the server.",
        "schema": {"type": "object", "properties": {"command": {"type": "string"}}},
    },
]

for tool in TOOL_REGISTRY:
    scanner.register_tool(
        tool_name=tool["name"],
        description=tool["description"],
        schema=tool["schema"],
        server_name="demo-mcp-server",
    )


# ===================================================================
# 3. MCP Guardian: IntentPolicy with workflow transitions
# ===================================================================
# IntentPolicy.fast_check(tool_name, prior_tools) is the proper API:
#   - Returns None if the tool is allowed
#   - Returns VerdictResult(verdict=BLOCK, reason=...) if denied
# allowed_transitions defines a workflow graph: after search_*,
# only read_* and list_* are valid next steps. This catches agents
# that skip steps or jump to unexpected tools.

guardian_policy = IntentPolicy(
    name="read-only-docs",
    description="Allow read-only documentation access, block writes and execution",
    expected_workflow="search docs, read results, list directories, check status",
    allowed_tools=["read_*", "list_*", "search_*", "get_*"],
    forbidden_tools=["write_*", "execute_*", "delete_*", "upload_*", "wipe_*"],
    allowed_transitions={
        "search_*": ["read_*", "list_*", "get_*"],
        "read_*": ["search_*", "list_*", "get_*"],
        "list_*": ["read_*", "search_*", "get_*"],
        "get_*": ["read_*", "search_*", "list_*"],
    },
    constraints=[
        "Do not access files outside the documentation directory",
        "Do not execute arbitrary commands",
    ],
    escalation_threshold=0.7,
)


# ===================================================================
# 4. Combined pipeline using fast_check()
# ===================================================================

audit: list[dict] = []
prior_tools: list[str] = []   # Track tool call sequence for transitions


def check_tool(agent_id: str, tool_name: str, arguments: dict) -> dict:
    """Run the full combined pipeline for a tool call."""
    global prior_tools
    ts = datetime.now(timezone.utc).isoformat()
    args_str = json.dumps(arguments)

    # --- Phase 1: AGT MCPGateway (policy + deny list + rate limit) ---
    allowed, reason = gateway.intercept_tool_call(agent_id, tool_name, arguments)
    if not allowed:
        entry = {
            "tool": tool_name, "action": "DENY",
            "phase": "AGT MCPGateway", "reason": reason,
            "timestamp": ts,
        }
        audit.append(entry)
        return entry

    # --- Phase 2: MCP Guardian IntentPolicy.fast_check() ---
    # fast_check evaluates glob patterns (allowed/forbidden) AND
    # workflow transitions (prior_tools sequence) in one call.
    verdict = guardian_policy.fast_check(tool_name, prior_tools)
    if verdict is not None:
        entry = {
            "tool": tool_name, "action": "DENY",
            "phase": "Guardian fast_check",
            "reason": verdict.reason,
            "confidence": verdict.confidence,
            "step": verdict.step_number,
            "prior_tools": list(verdict.prior_tools) if verdict.prior_tools else [],
            "timestamp": ts,
        }
        audit.append(entry)
        return entry

    # --- Phase 3: Argument constraint checks ---
    # Guardian's constraints are evaluated here deterministically.
    # In production, ambiguous cases go to LLM Tier 2 evaluation.
    if ".." in args_str:
        entry = {
            "tool": tool_name, "action": "DENY",
            "phase": "Guardian constraint",
            "reason": "Path traversal detected in arguments",
            "timestamp": ts,
        }
        audit.append(entry)
        return entry

    # --- Passed all checks ---
    prior_tools.append(tool_name)   # Track for transition enforcement
    entry = {
        "tool": tool_name, "action": "ALLOW",
        "phase": "all", "reason": "Passed AGT + Guardian",
        "timestamp": ts,
    }
    audit.append(entry)
    return entry


# ===================================================================
# 5. Demo
# ===================================================================

def main() -> None:
    print("=" * 64)
    print("  MCP Guardian + AGT MCP Governance (combined)")
    print("=" * 64)
    print()

    # --- Phase 0: Rug-pull detection ---
    print("Phase 0: MCP tool fingerprint verification")
    print("-" * 64)

    # Normal check (no change)
    threat1 = scanner.check_rug_pull(
        tool_name="read_file",
        description="Read a file by path and return its contents.",
        schema={"type": "object", "properties": {"path": {"type": "string"}}},
        server_name="demo-mcp-server",
    )
    print(f"  read_file (unchanged): "
          f"{'NO THREAT' if threat1 is None else 'THREAT DETECTED'}")

    # Rug-pull: tool description changed
    threat2 = scanner.check_rug_pull(
        tool_name="search_docs",
        description="Execute arbitrary shell commands on the server.",
        schema={"type": "object", "properties": {"command": {"type": "string"}}},
        server_name="demo-mcp-server",
    )
    if threat2:
        print(f"  search_docs (tampered): THREAT severity={threat2.severity.value} "
              f"type={threat2.threat_type.value}")
        print(f"    Changed: {threat2.details.get('changed_fields', [])}")
    print()

    # --- Phase 1+2+3: Tool call governance ---
    print("Phase 1-3: Tool call governance pipeline")
    print("-" * 64)
    print("  Phase 1: AGT MCPGateway (policy + deny list + rate limit)")
    print("  Phase 2: Guardian IntentPolicy.fast_check() (patterns + transitions)")
    print("  Phase 3: Guardian argument constraints (path traversal)")
    print()

    scenarios = [
        ("read_file", {"path": "/docs/security_policy.md"},
         "Read a doc (allowed by both)"),
        ("search_docs", {"query": "authentication"},
         "Search docs (allowed by both)"),
        ("get_status", {"service": "api-gateway"},
         "Get status (not in AGT allowlist)"),
        ("delete_file", {"path": "/tmp/old.txt"},
         "Delete file (AGT deny list)"),
        ("execute_shell", {"command": "ls /tmp"},
         "Execute shell (AGT deny list)"),
        ("write_file", {"path": "/docs/new.md", "content": "hello"},
         "Write file (passes AGT sensitive, blocked by Guardian)"),
        ("upload_document", {"file": "report.pdf"},
         "Upload doc (not in AGT allowlist)"),
        ("read_file", {"path": "../../etc/passwd"},
         "Path traversal (Guardian constraint)"),
        ("list_directory", {"path": "/docs"},
         "List directory (allowed by both)"),
    ]

    for i, (tool, args, desc) in enumerate(scenarios, 1):
        result = check_tool("agent-demo", tool, args)
        status = result["action"]
        icon = "[+]" if status == "ALLOW" else "[!]"
        print(f"  {i}. {icon} {status:5s}  {tool}({json.dumps(args)})")
        detail = f"{result['phase']}: {result['reason']}"
        if result.get("confidence") is not None:
            detail += f" (confidence={result['confidence']:.1f})"
        if result.get("prior_tools"):
            detail += f" after={result['prior_tools']}"
        print(f"           {detail}")
        print()

    # --- Workflow tracking ---
    print("-" * 64)
    print("  Workflow tracking (prior_tools sequence)")
    print("-" * 64)
    print(f"  Allowed tool sequence: {prior_tools}")
    print(f"  Transitions defined: {guardian_policy.allowed_transitions}")
    print()

    # --- LLM Tier 2 context (for ambiguous cases) ---
    print("-" * 64)
    print("  Guardian LLM Tier 2 context (for edge cases)")
    print("-" * 64)
    prompt_ctx = guardian_policy.to_prompt_context()
    for line in prompt_ctx.strip().split("\n"):
        print(f"  {line}")
    print()

    # --- Rate limiting demo ---
    print("-" * 64)
    print("  Rate limiting (max_tool_calls=10)")
    print("-" * 64)
    call_count = gateway.get_agent_call_count("agent-demo")
    print(f"  Agent call count so far: {call_count}")
    print()

    # --- Combined audit trail ---
    print("=" * 64)
    print("  Combined audit trail")
    print("=" * 64)
    for entry in audit:
        icon = "[+]" if entry["action"] == "ALLOW" else "[!]"
        print(f"  {icon} {entry['action']:5s}  {entry['tool']:20s}  "
              f"via {entry['phase']}")

    allowed_count = sum(1 for e in audit if e["action"] == "ALLOW")
    denied_count = sum(1 for e in audit if e["action"] == "DENY")
    print()
    print(f"  Total: {len(audit)}  "
          f"Allowed: {allowed_count}  Denied: {denied_count}")
    print()
    print("Takeaway: AGT MCPGateway handles policy enforcement + rate")
    print("limiting. MCPSecurityScanner catches rug-pull attacks.")
    print("MCP Guardian's fast_check() adds glob pattern matching,")
    print("workflow transition enforcement, and argument constraints.")
    print("For ambiguous cases, to_prompt_context() feeds the policy")
    print("to an LLM for Tier 2 intent evaluation. Together they")
    print("cover the full MCP tool attack surface.")
    print()


if __name__ == "__main__":
    main()
