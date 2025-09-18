# Orchestrated security trace analysis with agent handoffs (Open Agents SDK style)
from agents import Agent, Runner  # assumes your SDK exposes these
import asyncio
import json
from pathlib import Path

INPUT_PATH = Path("data/docker-curl-https.txt")
OUT_SUMMARY = Path("summary.md")
OUT_JSON = Path("details.json")

# 1) Define worker agents
analyzer_agent = Agent(
    name="Security Trace Analyzer",
    instructions=(
        "You receive raw sysdig-like trace text. "
        "Identify security-relevant events, suspicious patterns, and likely root cause. "
        "Produce a concise but complete analysis in markdown with sections: "
        "Findings, Evidence, Impact, Likelihood, Recommendations."
    ),
)

summary_agent = Agent(
    name="Summary Generator",
    instructions=(
        "You receive a technical analysis and must write an executive summary for a security lead. "
        "Use 5 to 8 bullets with concrete actions, no fluff. "
        "Return only markdown that is suitable for a report."
    ),
)

json_agent = Agent(
    name="JSON Formatter",
    model="gpt-4o-mini",
    instructions=(
        "You are a JSON formatter agent. Your ONLY job is to convert security analysis into valid JSON.\n\n"
        "CRITICAL RULES:\n"
        "1. Output ONLY valid JSON - no markdown, no text, no backticks, no explanations\n"
        "2. Start immediately with { and end with }\n"
        "3. Use this exact structure:\n"
        "{\n"
        '  "findings": ["finding1", "finding2"],\n'
        '  "evidence": ["evidence1", "evidence2"],\n'
        '  "impact": "impact description",\n'
        '  "likelihood": "HIGH|MEDIUM|LOW",\n'
        '  "recommendations": ["rec1", "rec2"]\n'
        "}\n\n"
        "Convert the input security summary into this JSON format. Output JSON only."
    )
)


# 2) Orchestrator with handoffs
orchestrator_agent = Agent(
    name="Security Analysis Orchestrator",
    instructions=(
        "You orchestrate a handoff workflow. "
        "Start by handing the input to the Security Trace Analyzer. "
        "Then hand off the analyzer result to the Summary Generator. "
        "Then hand off the summary to the JSON Formatter. "
        "Do not add your own content. Only forward and ensure the chain completes."
    ),
    handoffs=[analyzer_agent],  # first hop; the analyzer then knows to hand off to summary, then to JSON
)

# Chain the rest explicitly
analyzer_agent.handoffs = [summary_agent]
summary_agent.handoffs = [json_agent]

async def run_orchestrated_analysis(trace_text: str):
    """Run the orchestrated analysis and return both human summary and JSON."""
    run = await Runner.run(
        orchestrator_agent,
        f"Analyze this sysdig trace data:\n\n{trace_text}"
    )

    # Many SDKs return a single final string. If your SDK exposes per-agent artifacts,
    # you can retrieve them here. For now, we will parse the final output:
    final_text = run.final_output or ""

    # Heuristic split: the JSON agent is supposed to return only JSON,
    # so try to detect a JSON block at the end.
    summary_md = final_text
    json_blob = None
    try:
        # last brace block
        start = final_text.rfind("{")
        end = final_text.rfind("}")
        if start >= 0 and end >= start:
            maybe_json = final_text[start:end+1].strip()
            json_blob = json.loads(maybe_json)
            summary_md = final_text[:start].rstrip()
    except Exception:
        # leave json_blob as None if parsing fails
        pass

    return summary_md, json_blob, final_text

async def save_outputs(summary_md: str, json_obj: dict | None):
    OUT_SUMMARY.write_text(summary_md, encoding="utf-8")
    if json_obj is not None:
        OUT_JSON.write_text(json.dumps(json_obj, indent=2), encoding="utf-8")

async def display_summary(summary_md: str, json_obj: dict | None):
    print("\n=== Executive Summary (preview) ===")
    preview = summary_md.strip().splitlines()
    print("\n".join(preview[:12]))
    if len(preview) > 12:
        print("...")

    if json_obj is not None:
        json_text = json.dumps(json_obj)
        print("\n=== JSON (preview) ===")
        print((json_text[:300] + "...") if len(json_text) > 300 else json_text)

async def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input not found: {INPUT_PATH}")

    trace_text = INPUT_PATH.read_text(encoding="utf-8")

    print("🎭 Orchestrator-Controlled Security Analysis")
    print("=" * 60)
    print("🔄 Flow: Orchestrator → Analyzer → Summary → JSON")

    summary_md, json_obj, raw = await run_orchestrated_analysis(trace_text)
    await save_outputs(summary_md, json_obj)
    await display_summary(summary_md, json_obj)

    print("\n" + "=" * 60)
    print("✅ Orchestrated analysis complete")
    print(f"📁 Files generated: {OUT_SUMMARY.name}" + (f", {OUT_JSON.name}" if json_obj else ""))
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
