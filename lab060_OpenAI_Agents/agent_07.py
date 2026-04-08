"""
Security trace analysis with the Agent SDK (JSON output).

Same analysis as agent_06 but uses the Agent SDK instead of the raw
Responses API. The agent's instructions request structured JSON output
with line-number references into the sysdig trace.

Input: data/docker-curl-https.txt (sysdig capture of curl inside Docker).
"""

from agents import Agent, Runner
import asyncio
import json

with open("data/docker-curl-https.txt", "r", encoding="utf-8") as f:
    text = f.read()

security_agent = Agent(
    name="Security Trace Analyst",
    model="gpt-4o-mini",
    instructions="""You are a security and malware analyst.

Analyze the sysdig system call trace and provide your analysis in the following JSON format:

{
  "summary": "Concise summary of the process being traced",
  "process_info": {
    "command": "executed command",
    "arguments": "command arguments",
    "pid": "process ID if identifiable",
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
      "observation": "factual security-relevant observation",
      "line_number": 1234,
      "evidence": "specific trace line content"
    }
  ]
}

IMPORTANT: Each trace line starts with a number (like 1051, 1052, etc.).
Always include these line numbers in your analysis for reference.

Stick to facts from the trace data. Avoid speculation.""",
)


async def main():
    print("Security Trace Analysis (Agent SDK, JSON output)")
    print("=" * 60)

    result = await Runner.run(
        security_agent,
        f"Analyze this sysdig system call trace data:\n\n{text}",
    )

    response_text = result.final_output

    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            parsed = json.loads(response_text[json_start:json_end])
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        else:
            print("Raw output (no JSON found):")
            print(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print("\nRaw output:")
        print(result.final_output)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
