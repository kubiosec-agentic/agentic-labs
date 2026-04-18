![Microsoft](https://img.shields.io/badge/Microsoft-blue) ![Security](https://img.shields.io/badge/Security-red) ![Python](https://img.shields.io/badge/Python-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue)

# LAB990 Addendum: Agent Governance Toolkit

## Introduction

Microsoft's Agent Governance Toolkit (AGT) was open-sourced on April 2,
2026 under the MIT license. The project's vision includes runtime policy
enforcement (allow/deny lists, YAML/OPA/Cedar policies), zero-trust
agent identity, execution sandboxing, and Merkle-chained audit trails.

The PyPI package (`agent-governance-toolkit` v3.1.0) currently ships
three functional modules:

1. **PromptDefenseEvaluator**: grades agent system prompts for defense
   coverage against 12 OWASP LLM attack vectors. Pure regex, zero LLM
   cost, under 5ms per prompt. Think of it as a linter for system
   prompts.
2. **SupplyChainGuard**: scans dependency manifests (requirements.txt,
   package.json, pyproject.toml) for unpinned versions, version ranges,
   and typosquatting.
3. **IntegrityVerifier**: SHA-256 manifest generation and verification
   for governance code. Currently scoped to AGT's internal modules.

The blog post described additional capabilities (runtime
`PolicyEvaluator`, `AuditLog`, agent-os policy engine) that are not yet
in the PyPI package. Exercises 4-6 implement the runtime governance
pattern described in the blog using lightweight Python policy engines,
showing how you would build this today while waiting for AGT's runtime
modules to ship.

Repository: https://github.com/microsoft/agent-governance-toolkit

## Set up your environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Exercises 1-3 need no API keys. Exercises 4-6 are noted individually.

### Optional: full agent-os policy engine

The repo also contains `agent-os-kernel`, which provides runtime
`PolicyEvaluator`, `GovernancePolicy`, and the `agent_os.lite.govern()`
API described in the blog post. This package is not yet on PyPI but
installs directly from GitHub:

```bash
pip install "git+https://github.com/microsoft/agent-governance-toolkit.git#subdirectory=packages/agent-os"
```

See the repo's `examples/` directory for demos that use the full
`agent_os` API, including the 9-scenario OpenAI Agents governance demo.

## Exercise 1: Prompt Defense Evaluator

Grades agent system prompts for defense coverage against 12 OWASP LLM
attack vectors. Three prompts are tested: a naive one (grade F), one
with partial defenses (grade D), and a hardened one (grade B).

```bash
python3 govern_01.py
```

The output shows which attack vectors are undefended and generates an
audit entry suitable for compliance reporting. Run this in CI/CD before
deploying any agent: a system prompt graded below B is likely vulnerable
to at least one OWASP attack vector.

## Exercise 2: Supply Chain Guard

Scans dependency manifests for supply chain risks: unpinned versions,
version ranges, and typosquatting. Two sample requirements files are
tested: one with intentional problems and one properly pinned.

```bash
python3 govern_02.py
```

The exercise also scans its own requirements.txt and runs standalone
typosquatting checks against package names like "requets" and
"tenserflow". Run `SupplyChainGuard` in CI before `pip install` to
catch problems before they reach your agent's runtime.

## Exercise 3: Integrity Verification

Demonstrates the tamper detection pattern behind AGT's
IntegrityVerifier. Generates SHA-256 hashes of governance code files,
verifies them, then simulates tampering by modifying a hash in the
manifest.

```bash
python3 govern_03.py
```

In production: generate the manifest during a trusted CI build, sign it,
and verify at agent startup. If any file has been tampered with, the
agent should refuse to start.

## Exercise 4: Runtime tool governance (OpenAI Agents SDK)

AGT's blog described runtime policy enforcement for tool calls, but
the current PyPI package does not include this module yet. This exercise
implements the pattern using a lightweight Python policy engine with
regex-based tool name matching.

A security analyst agent has four tools: `scan_ports`, `read_logs`,
`deploy_patch`, and `wipe_server`. The policy allows investigation but
blocks remediation. This models a common pattern: investigate
autonomously, require human approval for destructive actions.

```bash
export OPENAI_API_KEY="sk-..."
python3 govern_04.py
```

Two prompts run:

1. "Investigate host 10.0.0.42" -- `scan_ports` and `read_logs` pass.
2. "Deploy patch and wipe the server" -- both are blocked by governance
   before they execute.

The agent still tries to call the blocked tools (the LLM does not know
they are forbidden). Governance intercepts after the LLM decides but
before the tool runs. This is the key difference from prompt-based
guardrails.

## Exercise 5: Governing MCP tool calls (AGT MCPGateway)

This exercise requires `agent-os-kernel` (see Exercise 6 install).

The agent connects to the Microsoft Learn MCP server. AGT's
`MCPGateway` and `GovernancePolicy` compute which tools the agent
is allowed to use. The allowed list is passed to
`get_mcp_tool(allowed_tools=[...])`, which filters tools at the API
level before the LLM even sees them.

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_CHAT_MODEL="gpt-4o-mini"
python3 govern_05_mcp.py
```

**Why not `function_middleware`?** MAF's `get_mcp_tool()` uses OpenAI's
hosted MCP execution. Tool calls are sent to OpenAI, which calls the
MCP server remotely. Your Python process never sees the actual tool
invocation, so `function_middleware` cannot intercept it. The correct
interception point is `allowed_tools` on `get_mcp_tool()`, which
filters tools server-side.

Two prompts demonstrate the governance:

1. "Search for Azure Container Apps docs" - the search tool is in the
   allowed list, so the LLM can use it and gets results.
2. "Fetch the full content" - fetch/read tools are not in the allowed
   list, so the LLM never sees them and must explain the limitation.

`MCPGateway` also provides an audit trail and rate limiting per agent.

## Exercise 6: MCP Guardian + AGT MCP Governance (combined)

This exercise requires `agent-os-kernel` from the AGT repo:

```bash
pip install "git+https://github.com/microsoft/agent-governance-toolkit.git#subdirectory=packages/agent-os"
```

Combines MCP Guardian with three AGT modules from `agent-os-kernel`
that directly address MCP tool security:

- **MCPSecurityScanner**: fingerprints tool definitions at registration
  time, then detects rug-pull attacks when an MCP server changes a
  tool's description or schema after the agent trusts it.
- **MCPGateway**: `intercept_tool_call()` enforces a `GovernancePolicy`
  with allowed/denied tool lists, rate limiting per agent, and argument
  sanitization. This is the server-side complement to Exercise 5's
  client-side middleware (which does not intercept MCP tools).
- **MCP Guardian IntentPolicy**: `fast_check(tool_name, prior_tools)`
  evaluates glob-based allow/forbid patterns and workflow transition
  enforcement in one call. Constraint checks catch path traversal, etc.
  `to_prompt_context()` generates policy text for LLM Tier 2 intent
  evaluation. In production, adds human escalation for ambiguous cases.

```bash
python3 govern_06_guardian.py
```

No API keys needed. The exercise runs four phases:

**Phase 0: Rug-pull detection.** Two fingerprint checks: one unchanged
tool (no threat) and one tampered tool where `search_docs` was silently
changed to "execute arbitrary shell commands" (CRITICAL rug-pull).

**Phases 1-3: Tool call governance.** Nine scenarios through the
combined pipeline:

| Scenario | Tool | Blocked by | Reason |
|----------|------|-----------|--------|
| 1 | `read_file` (safe) | -- | Allowed by both |
| 2 | `search_docs` | -- | Allowed by both |
| 3 | `get_status` | -- | Allowed by both |
| 4 | `delete_file` | AGT MCPGateway | On deny list |
| 5 | `execute_shell` | AGT MCPGateway | On deny list |
| 6 | `write_file` | AGT MCPGateway | Sensitive tool, not on allow list |
| 7 | `upload_document` | AGT MCPGateway | Not on allow list |
| 8 | `read_file` (traversal) | Guardian constraint | `../` in arguments |
| 9 | `list_directory` | -- | Allowed by both |

The audit trail shows which layer blocked each call. AGT handles the
fast policy checks and rate limiting; Guardian adds constraint checks
and (in production) LLM-based intent evaluation for ambiguous cases.

## How AGT fits into the OWASP Agentic Top 10

| OWASP risk | AGT mitigation | Exercise |
|------------|---------------|----------|
| Prompt Injection | PromptDefenseEvaluator grades system prompts | 1, 6 |
| Supply Chain | SupplyChainGuard scans dependencies | 2 |
| Excessive Capabilities | Tool allow/deny policies | 4, 5, 6 |
| Uncontrolled Code Execution | Content pattern matching | 4, 5 |
| Goal Hijacking | Deterministic policy (LLM cannot override) | 4, 5 |
| Integrity | Hash-based tamper detection | 3 |

## What AGT is not

AGT is not a prompt guardrail or content moderation tool. Its current
PyPI modules focus on pre-deployment checks (prompt defense, supply
chain, integrity). The runtime policy enforcement described in the blog
(agent-os, PolicyEvaluator) is not yet shipped. Exercises 4-6 implement
this pattern manually, demonstrating how to build runtime governance
today using middleware and custom policy engines.

The two approaches are complementary: use prompt guardrails for content
safety, and deterministic policy engines for action safety.

## Cleanup

```bash
deactivate
rm -rf .venv
```

## Additional resources

- AGT repository: https://github.com/microsoft/agent-governance-toolkit
- Announcement blog post: https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/
- MCP Guardian: https://github.com/mcp-guardian/mcp-guardian
- OWASP Agentic Top 10: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
