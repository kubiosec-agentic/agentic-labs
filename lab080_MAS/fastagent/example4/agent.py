"""
Example 4: Kubernetes security auditor (multi-agent orchestration).

Four agents coordinate to generate, audit, and remediate a Kubernetes
Pod manifest against industry security benchmarks:

  generator   - creates a baseline NGINX Pod manifest
  reviewer    - audits against CIS, NSA/CISA, and Pod Security Standards
  remediator  - produces a corrected manifest from review findings
  writer      - writes all artifacts to disk

The orchestrator plans and delegates across reviewer, remediator, and
writer. Uses two local MCP servers (filesystem + fetch), no tokens needed.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("K8s-Benchmarked-Review")

# --- Agents ---

@fast.agent(
    name="generator",
    instruction=(
        "You create minimal, production-minded Kubernetes YAML. "
        "Prefer least-privilege defaults, avoid 'latest' tags, and include probes "
        "and resource requests/limits. When asked, write the manifest to disk."
    ),
    servers=["filesystem"],
)
@fast.agent(
    name="reviewer",
    instruction=(
        "You are a Kubernetes auditor. Fetch and base all checks on these sources:\n"
        "1) CIS Kubernetes Benchmark: https://www.cisecurity.org/benchmark/kubernetes\n"
        "2) NSA/CISA Kubernetes Hardening Guide 1.2: "
        "   https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/"
        "CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF\n"
        "3) Kubernetes Pod Security Standards: "
        "   https://kubernetes.io/docs/concepts/security/pod-security-standards/\n"
        "4) Pod Security Admission: "
        "   https://kubernetes.io/docs/concepts/security/pod-security-admission/\n\n"
        "Procedure:\n"
        "- Load the supplied YAML.\n"
        "- Build a checklist mapping each item to CIS, NSA/CISA, and PSS controls.\n"
        "- For each check: PASS or FAIL, severity, rationale, and control reference.\n"
        "- Provide targeted remediations with a patched YAML where possible.\n"
        "- Include a References section with the URLs you consulted.\n"
    ),
    servers=["fetch", "filesystem"],
)
@fast.agent(
    name="remediator",
    instruction=(
        "Take reviewer findings and produce a corrected manifest that satisfies "
        "the cited controls without changing application intent. Preserve names "
        "and labels unless a change is required. Write the fixed file and append "
        "a concise CHANGELOG to the report."
    ),
    servers=["filesystem"],
)
@fast.agent(
    name="writer",
    instruction=(
        "Write artifacts to disk in the requested location and format. "
        "Create directories if missing. Overwrite if asked."
    ),
    servers=["filesystem"],
)

# --- Orchestrator ---

@fast.orchestrator(
    name="orchestrate",
    agents=["reviewer", "remediator", "writer"],
    plan_type="full",
)
async def main() -> None:
    async with fast.run() as agent:
        # Step 1: generate a baseline NGINX Pod manifest
        await agent.generator(
            "Create a Kubernetes Pod manifest named 'nginx-pod' using image 'nginx'. "
            "Write only the YAML to ./manifests/nginx-pod.yaml"
        )

        # Step 2: orchestrate the review, remediation, and report
        await agent.orchestrate(
            "Load ./manifests/nginx-pod.yaml.\n"
            "Fetch and use CIS Kubernetes Benchmark, NSA/CISA Hardening Guide, "
            "and Kubernetes Pod Security Standards as the basis for checks.\n\n"
            "Deliverables:\n"
            "1) ./manifests/review.md with a checklist table (Item, PASS/FAIL, "
            "Severity, Rationale, Control Mapping) and a References section.\n"
            "2) ./manifests/nginx-pod-fixed.yaml with all remediations applied.\n"
        )


if __name__ == "__main__":
    asyncio.run(main())
