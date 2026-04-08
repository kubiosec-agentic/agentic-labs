"""
Multi-agent security analysis pipeline.

Three agents run sequentially, each consuming the previous agent's output:

  1. Analyzer: detailed sysdig trace analysis with line-number references
  2. Summary Generator: converts the analysis into a markdown report (summary.md)
  3. JSON Formatter: structures the analysis as machine-readable JSON (details.json)

This demonstrates agent-to-agent result passing, multi-format output, and
file generation from an agentic pipeline.

Input: data/docker-curl-https.txt (sysdig capture of curl inside Docker).
"""

from agents import Agent, Runner
import asyncio
import json

with open("data/docker-curl-https.txt", "r", encoding="utf-8") as f:
    text = f.read()

# ---- Agent 1: detailed analysis ----

analyzer_agent = Agent(
    name="Security Trace Analyzer",
    model="gpt-4o-mini",
    instructions="""You are a security analyst specialized in system call trace analysis.

Analyze the provided sysdig trace data and extract:
1. Process execution details (command, PID, arguments)
2. System call patterns and phases
3. Network activity (DNS, connections, data transfer)
4. File operations (libraries, configs, certificates)
5. Security-relevant observations with line numbers

Provide a comprehensive analysis with specific line number references.
Focus on facts only, avoid speculation.""",
)

# ---- Agent 2: markdown summary ----

summary_agent = Agent(
    name="Summary Generator",
    instructions="""You are a technical writer specializing in security reports.

Based on the security analysis provided, create a concise markdown summary:
- Executive summary of the traced process
- Key findings and phases
- Security implications
- Timeline of major events

Format as clean markdown suitable for documentation.
Keep it concise but informative.""",
)

# ---- Agent 3: structured JSON ----

json_agent = Agent(
    name="JSON Formatter",
    instructions="""You are a data analyst who structures security analysis into JSON.

Convert the security analysis into this JSON structure:

{
  "metadata": {
    "analysis_timestamp": "current timestamp",
    "trace_file": "data/docker-curl-https.txt",
    "total_lines": "number of trace lines"
  },
  "summary": "Brief summary of the traced process",
  "process_info": {
    "command": "executed command",
    "arguments": "command arguments",
    "pid": "process ID",
    "line_numbers": [1051, 1052]
  },
  "phases": [
    {
      "phase": "phase name",
      "description": "what happens in this phase",
      "key_syscalls": ["list of important system calls"],
      "line_range": {"start": 1051, "end": 1200},
      "key_lines": [1051, 1055, 1062]
    }
  ],
  "network_activity": {
    "dns_queries": "DNS resolution details",
    "connections": "network connections made",
    "data_transfer": "data transfer summary",
    "line_references": [2500, 2501, 2502]
  },
  "file_operations": {
    "libraries_loaded": ["list of key libraries"],
    "config_files": ["configuration files accessed"],
    "certificates": "certificate handling details",
    "line_references": [1062, 1070, 1091]
  },
  "security_observations": [
    {
      "observation": "security-relevant observation",
      "severity": "LOW|MEDIUM|HIGH",
      "line_number": 1234,
      "evidence": "specific trace line content"
    }
  ]
}

Include actual line numbers from the trace data. Output only valid JSON.""",
)


# ---- Pipeline ----

async def run_pipeline():
    """Run the three-agent analysis pipeline."""
    print("Multi-Agent Security Trace Analysis")
    print("=" * 60)

    # Step 1
    print("\n[1/3] Running security analysis...")
    analysis_result = await Runner.run(
        analyzer_agent,
        f"Analyze this sysdig system call trace data:\n\n{text}",
    )
    analysis = analysis_result.final_output
    print(f"  Analysis complete ({len(analysis)} chars)")

    # Step 2
    print("[2/3] Generating markdown summary...")
    summary_result = await Runner.run(
        summary_agent,
        f"Create a markdown summary based on this security analysis:\n\n{analysis}",
    )
    summary = summary_result.final_output
    print(f"  Summary complete ({len(summary)} chars)")

    # Step 3
    print("[3/3] Formatting structured JSON...")
    json_result = await Runner.run(
        json_agent,
        f"Convert this security analysis into structured JSON:\n\n{analysis}",
    )
    json_output = json_result.final_output
    print(f"  JSON complete ({len(json_output)} chars)")

    return analysis, summary, json_output


async def save_outputs(summary, json_output):
    """Write summary.md and details.json to disk."""
    try:
        with open("summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\n  Saved summary.md")
    except Exception as e:
        print(f"\n  Error saving summary.md: {e}")

    try:
        json_start = json_output.find("{")
        json_end = json_output.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            parsed = json.loads(json_output[json_start:json_end])
            with open("details.json", "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            print("  Saved details.json")
        else:
            with open("details.json", "w", encoding="utf-8") as f:
                f.write(json_output)
            print("  Saved details.json (raw, JSON parsing failed)")
    except json.JSONDecodeError as e:
        print(f"  JSON parsing error: {e}")
        with open("details.json", "w", encoding="utf-8") as f:
            f.write(json_output)
        print("  Saved details.json (raw)")
    except Exception as e:
        print(f"  Error saving details.json: {e}")


async def main():
    analysis, summary, json_output = await run_pipeline()
    await save_outputs(summary, json_output)

    # Display summary preview
    print("\n" + "=" * 60)
    print("SUMMARY PREVIEW (summary.md)")
    print("=" * 60)
    preview = summary[:800]
    if len(summary) > 800:
        preview += "\n..."
    print(preview)

    # Display JSON stats
    print("\n" + "=" * 60)
    print("JSON DETAILS (details.json)")
    print("=" * 60)
    try:
        json_start = json_output.find("{")
        json_end = json_output.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            parsed = json.loads(json_output[json_start:json_end])
            print(f"Summary: {parsed.get('summary', 'N/A')}")
            if "process_info" in parsed:
                print(f"Process: {parsed['process_info'].get('command', 'N/A')}")
            if "phases" in parsed:
                print(f"Phases: {len(parsed['phases'])} identified")
            if "security_observations" in parsed:
                print(f"Security observations: {len(parsed['security_observations'])}")
    except (json.JSONDecodeError, KeyError):
        print("(could not parse JSON preview)")

    print("\n" + "=" * 60)
    print("Pipeline complete. Files generated: summary.md, details.json")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
