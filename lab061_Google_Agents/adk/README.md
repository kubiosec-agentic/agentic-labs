# ADK Agents

This directory contains two security-focused ADK agent modules discovered by `adk web`:

| Directory | Agent | Description |
|-----------|-------|-------------|
| `llm_red_team_agent/` | security_orchestrator | Adversarial AI safety testing (red team / target / evaluator) |
| `cyber_guardian/` | cyber_guardian_orchestrator | Incident response with 6 tool functions (triage, intel, investigate, respond) |

See the [lab README](../README.md) for setup instructions and a full walkthrough.

## Quick start

```bash
adk web
```

Open `http://localhost:8000` and pick an agent from the dropdown.

## Creating new agents

See [instructions.md](./instructions.md) for templates and conventions.
