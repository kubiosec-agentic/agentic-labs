# Example 4: Kubernetes Security Auditor

Multi-agent orchestration that generates an NGINX Pod manifest, audits
it against CIS, NSA/CISA, and Kubernetes Pod Security Standards, then
produces a remediated manifest and a graded report.

## What it demonstrates

- **`@fast.orchestrator`** pattern: a planner agent coordinates three
  specialist workers (reviewer, remediator, writer)
- **Local MCP servers** (stdio): `filesystem` for disk I/O and `fetch`
  for pulling security benchmark documents from the web
- **No tokens needed**: both MCP servers are local subprocesses

## Agents

| Agent | Role | MCP servers |
|-------|------|-------------|
| `generator` | Creates a baseline K8s Pod manifest | filesystem |
| `reviewer` | Audits against CIS, NSA/CISA, PSS benchmarks | fetch, filesystem |
| `remediator` | Produces a corrected manifest from findings | filesystem |
| `writer` | Writes all artifacts to disk | filesystem |

## Run

```bash
cd example4
uv run agent.py
```

## Output

After running, check the `./manifests/` directory for:

- `nginx-pod.yaml`: the original generated manifest
- `nginx-pod-fixed.yaml`: the remediated manifest
- `review.md`: audit report with control mappings
