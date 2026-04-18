"""
Exercise 1: Agent Governance in 60 seconds.

The simplest possible example. Create an allow/deny policy with one
call, then test agent actions against it. No LLM, no framework, just
deterministic policy evaluation.

Run:
    python3 govern_01.py
"""

from agent_os.lite import govern

# 1. Create a governance gate: allow two tools, deny three.
check = govern(
    allow=["web_search", "read_file"],
    deny=["execute_code", "delete_file", "send_email"],
)


def test_action(action: str) -> bool:
    """Check whether an action is allowed and print the result."""
    allowed = check.is_allowed(action)
    status = "ALLOWED" if allowed else "BLOCKED"
    marker = "+" if allowed else "!"
    print(f"  [{marker}] {action}: {status}")
    return allowed


print("\nAgent Governance Toolkit: policy enforcement demo\n")
print("Policy:")
print("  allow: web_search, read_file")
print("  deny:  execute_code, delete_file, send_email\n")

print("Testing actions against policy:\n")
test_action("web_search")       # allowed
test_action("read_file")        # allowed
test_action("execute_code")     # blocked
test_action("delete_file")      # blocked
test_action("send_email")       # blocked

# Stats: total decisions, denials, avg latency
stats = check.stats
print(f"\nStats: {stats['total']} decisions, "
      f"{stats['denied']} blocked, "
      f"{stats['violation_rate']} violation rate, "
      f"{stats['avg_latency_ms']}ms avg latency")
