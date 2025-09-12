from agents import Agent, Runner
import asyncio
import json

# Load the document
with open("data/docker-curl-https.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Create security analysis agent with JSON output
security_agent = Agent(
    name="Security Trace Analyst",
    model="gpt-4.1-mini",
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

IMPORTANT: Each trace starts with a number (like 1051, 1052, etc.). Always include these line numbers in your analysis for reference. Use the actual line numbers from the trace data to make it easy to review specific events.

Stick to facts from the trace data. Avoid speculation."""
)

async def main():
    print("🔍 Security Trace Analysis with OpenAI Agents (JSON Output)")
    print("=" * 60)
    
    # Run the security analysis with the loaded trace data
    result = await Runner.run(
        security_agent,
        f"Analyze this sysdig system call trace data:\n\n{text}"
    )
    
    # Try to parse and pretty-print the JSON output
    try:
        # Extract JSON from the response (in case there's extra text)
        response_text = result.final_output
        
        # Find JSON content (look for opening brace)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_content = response_text[json_start:json_end]
            parsed_json = json.loads(json_content)
            
            # Pretty print the JSON
            print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        else:
            # Fallback: print raw output
            print("Raw output (JSON parsing failed):")
            print(response_text)
            
    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("\nRaw output:")
        print(result.final_output)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
