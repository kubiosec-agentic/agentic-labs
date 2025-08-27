from agents import Agent, Runner
import asyncio
import json
import os

# Load the document
with open("data/docker-curl-https.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Agent 1: Security Trace Analyzer - performs detailed analysis
analyzer_agent = Agent(
    name="Security Trace Analyzer",
    model="gpt-4.1-mini",
    instructions="""You are a security analyst specialized in system call trace analysis.

Analyze the provided sysdig trace data and extract:
1. Process execution details (command, PID, arguments)
2. System call patterns and phases
3. Network activity (DNS, connections, data transfer)
4. File operations (libraries, configs, certificates)
5. Security-relevant observations with line numbers

Provide a comprehensive analysis with specific line number references from the trace.
Focus on facts only, avoid speculation."""
)

# Agent 2: Summary Generator - creates high-level markdown summary
summary_agent = Agent(
    name="Summary Generator",
    instructions="""You are a technical writer specializing in security reports.

Based on the security analysis provided, create a concise markdown summary that includes:
- Executive summary of the traced process
- Key findings and phases
- Security implications
- Timeline of major events

Format as clean markdown suitable for documentation.
Keep it concise but informative."""
)

# Agent 3: JSON Formatter - structures detailed results as JSON
json_agent = Agent(
    name="JSON Formatter",
    instructions="""You are a data analyst who structures security analysis into JSON format.

Convert the security analysis into this detailed JSON structure:

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

Include actual line numbers from the trace data. Output only valid JSON."""
)

async def run_multi_agent_analysis():
    """Run multi-agent security analysis pipeline."""
    
    print("🔍 Multi-Agent Security Trace Analysis")
    print("=" * 60)
    
    # Step 1: Security Analysis
    print("📊 Step 1: Running security analysis...")
    analysis_result = await Runner.run(
        analyzer_agent,
        f"Analyze this sysdig system call trace data:\n\n{text}"
    )
    
    analysis = analysis_result.final_output
    print(f"✅ Analysis completed ({len(analysis)} characters)")
    
    # Step 2: Generate Summary
    print("\n📝 Step 2: Generating markdown summary...")
    summary_result = await Runner.run(
        summary_agent,
        f"Create a markdown summary based on this security analysis:\n\n{analysis}"
    )
    
    summary = summary_result.final_output
    print(f"✅ Summary generated ({len(summary)} characters)")
    
    # Step 3: Format as JSON
    print("\n📋 Step 3: Formatting detailed JSON...")
    json_result = await Runner.run(
        json_agent,
        f"Convert this security analysis into structured JSON:\n\n{analysis}"
    )
    
    json_output = json_result.final_output
    print(f"✅ JSON formatted ({len(json_output)} characters)")
    
    return analysis, summary, json_output

async def save_outputs(summary, json_output):
    """Save outputs to files."""
    try:
        # Save summary.md
        with open("summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\n💾 Saved summary.md")
        
        # Parse and save details.json
        try:
            # Extract JSON from response
            json_start = json_output.find('{')
            json_end = json_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = json_output[json_start:json_end]
                parsed_json = json.loads(json_content)
                
                with open("details.json", "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                print("💾 Saved details.json")
            else:
                # Save raw output if JSON parsing fails
                with open("details.json", "w", encoding="utf-8") as f:
                    f.write(json_output)
                print("💾 Saved details.json (raw format - JSON parsing failed)")
                
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            with open("details.json", "w", encoding="utf-8") as f:
                f.write(json_output)
            print("💾 Saved details.json (raw format)")
            
    except Exception as e:
        print(f"❌ Error saving files: {e}")

async def display_summary(summary, json_output):
    """Display analysis results."""
    print("\n" + "=" * 60)
    print("📄 SUMMARY (summary.md)")
    print("=" * 60)
    print(summary[:800] + "..." if len(summary) > 800 else summary)
    
    print("\n" + "=" * 60)
    print("📋 DETAILS (details.json)")
    print("=" * 60)
    
    try:
        # Try to parse and pretty-print JSON
        json_start = json_output.find('{')
        json_end = json_output.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_content = json_output[json_start:json_end]
            parsed_json = json.loads(json_content)
            
            # Display key sections
            print(f"Summary: {parsed_json.get('summary', 'N/A')}")
            if 'process_info' in parsed_json:
                print(f"Process: {parsed_json['process_info'].get('command', 'N/A')}")
            if 'phases' in parsed_json:
                print(f"Phases: {len(parsed_json['phases'])} identified")
            if 'security_observations' in parsed_json:
                print(f"Security observations: {len(parsed_json['security_observations'])}")
        else:
            print("Raw JSON output:")
            print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
            
    except json.JSONDecodeError:
        print("Raw JSON output:")
        print(json_output[:500] + "..." if len(json_output) > 500 else json_output)

async def main():
    # Run multi-agent analysis
    analysis, summary, json_output = await run_multi_agent_analysis()
    
    # Save outputs to files
    await save_outputs(summary, json_output)
    
    # Display results
    await display_summary(summary, json_output)
    
    print("\n" + "=" * 60)
    print("✅ Multi-agent analysis complete!")
    print("📁 Files generated: summary.md, details.json")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
