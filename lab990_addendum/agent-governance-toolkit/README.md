![Microsoft](https://img.shields.io/badge/Microsoft-blue) ![Security](https://img.shields.io/badge/Security-red) ![Python](https://img.shields.io/badge/Python-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue)

# LAB990 Addendum: Agent Governance Toolkit

## Introduction

Prompt-based safety (system prompts, guardrail agents) is
probabilistic: the LLM decides whether to comply. Microsoft's Agent
Governance Toolkit (AGT) takes a different approach. It sits between
your agent framework and the actions your agent wants to take, and
evaluates every tool call against a deterministic policy before
execution happens. If the policy says "deny", the call never fires,
regardless of what the LLM asked for.

AGT was open-sourced on April 2, 2026 under the MIT license. It is
framework-agnostic (LangChain, CrewAI, OpenAI Agents SDK, Google ADK,
Microsoft Agent Framework, and others) and adds sub-millisecond
overhead per policy evaluation.

The toolkit has seven packages. This addendum focuses on the two you
will use first:

1. **agent-os**: the core policy engine. Supports YAML rules,
   OPA/Rego, and Cedar policies. This is where allow/deny lists,
   content pattern matching, and rate limiting live.
2. **OpenAI Agents SDK integration**: a `GovernancePolicy` class and
   a `@guard` decorator that wrap async tool functions with policy
   enforcement, including allowlist/blocklist checks and dangerous
   content pattern matching.

The other packages (agent-mesh for zero-trust identity, agent-runtime
for execution sandboxing, agent-sre for SLOs and circuit breakers,
agent-compliance for regulatory mapping, agent-marketplace for plugin
signing, and agent-lightning for RL training governance) are documented
in the repo but not covered here.

Repository: https://github.com/microsoft/agent-governance-toolkit

## Set up your environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No API keys are needed for exercise 1. Exercise 2 uses the OpenAI
Agents SDK integration but does not make actual LLM calls; it
demonstrates the governance layer in isolation.

## Exercise 1: Governance in 60 seconds

The simplest possible governance example. A single `govern()` call
creates a policy gate with an allow list and a deny list. Each agent
action is checked against the policy before execution.

```bash
python3 govern_01.py
```

The output shows five actions tested against the policy: two pass, three
are blocked. The `stats` object reports total decisions, denial count,
violation rate, and average evaluation latency (typically under 0.1ms).

Things to notice: there is no LLM involved. The policy is
deterministic. A blocked action never executes, period. This is the
fundamental difference from prompt-based guardrails.

## Exercise 2: OpenAI Agents SDK with governance guardrails

This exercise wraps async tool functions with a governance guard.
The `GovernancePolicy` defines three layers of enforcement:

1. **Tool allowlist**: only `file_search` and `code_interpreter` are
   permitted. Any other tool name is blocked.
2. **Tool blocklist**: `shell_exec` and `network_request` are
   explicitly denied (defense in depth).
3. **Content patterns**: arguments containing `DROP TABLE` or `rm -rf`
   are blocked, even if the tool itself is allowed.

```bash
python3 govern_02.py
```

Three scenarios run in sequence:

| Scenario | Tool | Why it is blocked or allowed |
|----------|------|-----------------------------|
| 1 | `web_search` | Not in the allowlist |
| 2 | `code_interpreter` | Allowed tool, but argument contains `rm -rf` |
| 3 | `file_search` | Allowed tool, safe argument |

An audit trail is printed at the end with timestamps and
pass/fail status for each call.

## Exercise 3: File assistant agent

This wires governance into a real OpenAI agent. The agent has four
tools: `search_docs`, `read_file`, `execute_shell`, and `delete_file`.
The policy allows only the read-only tools. Two prompts are sent:

1. "Search for security policy docs and read the first result."
   The agent calls `search_docs` and `read_file`, both pass.
2. "Delete /tmp/old_logs.txt and run ls /tmp to confirm."
   The agent tries `delete_file` and `execute_shell`, both are blocked
   by governance before they execute.

```bash
export OPENAI_API_KEY="sk-..."
python3 govern_03.py
```

The key observation: the agent still tries to call the blocked tools
(the LLM does not know they are forbidden). Governance intercepts the
call after the LLM decides but before the tool runs. This is the
difference from prompt-based guardrails, where you tell the LLM "do
not use these tools" and hope it complies.

## Exercise 4: Security analyst agent

Same pattern, security-themed. The agent has `scan_ports`, `read_logs`,
`deploy_patch`, and `wipe_server`. Governance allows investigation
(read-only) but blocks remediation (destructive actions).

1. "Investigate host 10.0.0.42: scan ports and check nginx logs."
   Both tools pass; the agent reports suspicious findings.
2. "Deploy patch CVE-2026-1234 and wipe the server."
   Both `deploy_patch` and `wipe_server` are blocked. The agent
   explains it cannot proceed and recommends manual intervention.

```bash
python3 govern_04.py
```

This models a real-world pattern: let agents investigate autonomously,
but require human approval for destructive actions. The governance
layer enforces this boundary deterministically regardless of how
convincing the prompt is.

## How AGT fits into the OWASP Agentic Top 10

AGT maps its enforcement capabilities to all 10 risks in the OWASP
Agentic Top 10. The exercises above touch on three of them directly:

| OWASP risk | AGT mitigation | Exercise |
|------------|---------------|----------|
| Excessive Capabilities | Tool allowlist/blocklist | 1, 2, 3, 4 |
| Uncontrolled Code Execution | Content pattern matching | 2, 3 |
| Goal Hijacking | Deterministic policy (LLM cannot override) | 3, 4 |

The full mapping is in the repo at `docs/OWASP-COMPLIANCE.md`.

## What AGT is not

AGT is not a prompt guardrail or content moderation tool. It does not
inspect LLM inputs or outputs. It governs agent actions: which tools
can be called, with what arguments, by which identity, at what rate.
The two approaches are complementary. Use prompt guardrails (like the
OpenAI Moderation API) for content safety, and AGT for action safety.

## Cleanup

```bash
deactivate
rm -rf .venv
```

## Additional resources

- AGT repository: https://github.com/microsoft/agent-governance-toolkit
- Announcement blog post: https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/
- OWASP Agentic Top 10: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
