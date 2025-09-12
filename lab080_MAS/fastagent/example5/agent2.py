"""
Multi-agent orchestration that:
1) generates an NGINX Pod manifest,
2) reviews it against CIS, NSA/CISA, and Kubernetes Pod Security Standards,
3) writes a fixed manifest and a markdown report with mapped controls.
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
    model="gpt-4o",
)
@fast.agent(
    name="reviewer",
    instruction=(
        "You are a Kubernetes auditor. Fetch and base all checks on these sources:\n"
        "1) CIS Kubernetes Benchmark landing: https://www.cisecurity.org/benchmark/kubernetes\n"
        "   If accessible, also use a current CIS PDF for control names.\n"
        "2) NSA/CISA Kubernetes Hardening Guide 1.2 PDF: "
        "   https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF\n"
        "3) Kubernetes Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/\n"
        "4) Pod Security Admission: https://kubernetes.io/docs/concepts/security/pod-security-admission/\n"
        "Optionally enrich with OWASP K8s Top 10: https://owasp.org/www-project-kubernetes-top-ten/\n\n"
        "Procedure:\n"
        "- Load the supplied YAML.\n"
        "- Build a checklist that maps each item to one or more controls:\n"
        "  * CIS sections relevant to workload security and runtime (eg container security settings, "
        "    image policy, resource limits, capabilities, seccomp, non-root).\n"
        "  * NSA/CISA recommendations on least privilege, scanning, isolation, logging.\n"
        "  * Pod Security Standards levels (Baseline and Restricted) and Pod Security Admission language.\n"
        "- For each check: PASS or FAIL, severity (High, Medium, Low), rationale, and the exact control reference "
        "  like CIS-<section>, NSA-CISA <page or section>, PSS:Restricted <rule>.\n"
        "- Provide targeted remediations. When feasible, output a patched YAML.\n"
        "- At the end, include a References section with clickable links used.\n"
    ),
    servers=["fetch", "filesystem"],
    model="gpt-4o",
)
@fast.agent(
    name="remediator",
    instruction=(
        "Take reviewer findings and produce a corrected manifest that satisfies the cited controls "
        "without changing application intent. Preserve names and labels unless a change is required. "
        "Write the fixed file and append a concise CHANGELOG to the report."
    ),
    servers=["filesystem"],
    model="gpt-4o",
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
        # 1) Generate a baseline NGINX Pod manifest and save it
        gen_task = """
Create a Kubernetes Pod manifest named 'nginx-pod' using image 'nginx'.
Write only the YAML to ./manifests/nginx-pod.yaml
"""
        await agent.generator(gen_task)

        # 2) Review against CIS, NSA/CISA, PSS
        task = """
Load ./manifests/nginx-pod.yaml.
Fetch and use these sources as the basis for checks and citations:
- CIS Kubernetes Benchmark landing page and any accessible CIS PDF.
- NSA/CISA Kubernetes Hardening Guide 1.2 PDF.
- Kubernetes Pod Security Standards and Pod Security Admission docs.
- Optionally OWASP Kubernetes Top 10.

Deliverables:
1) ./manifests/review.md with:
   - Checklist table: Item, PASS/FAIL, Severity, Rationale, Control Mapping
     (eg CIS <section or control id>, NSA/CISA <section or page>, PSS:Baseline|Restricted <rule>).
   - Detailed Findings with remediation steps.
   - References section with the exact URLs you consulted.
2) Also print a patched YAML to stdout if any FAIL items can be auto-fixed.
"""

        await agent.orchestrate(task)

# Run the orchestrator  
  

if __name__ == "__main__":
    asyncio.run(main())
