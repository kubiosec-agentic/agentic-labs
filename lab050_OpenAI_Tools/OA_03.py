import os
import json
import subprocess
from openai import OpenAI

# Initialize OpenAI client
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL if BASE_URL else "https://api.openai.com/v1"
)

def check_package_vulnerabilities(requirements_file: str) -> str:
    """Scan Python dependencies for known vulnerabilities using pip-audit."""
    if not os.path.exists(requirements_file):
        return json.dumps({
            "status": "error",
            "message": f"Requirements file not found: {requirements_file}"
        })
    
    try:
        # Run pip-audit to check for vulnerabilities
        result = subprocess.run([
            "pip-audit", 
            "--requirement", requirements_file,
            "--format", "json"
        ], capture_output=True, text=True, timeout=120)
        
        # pip-audit returns 0 for success even when vulnerabilities are found
        # The summary message goes to stderr, JSON data goes to stdout
        if result.stdout.strip():
            try:
                vulnerabilities = json.loads(result.stdout)
                
                # Handle both old and new pip-audit JSON formats
                if "dependencies" in vulnerabilities:
                    # New format: {"dependencies": [{"name": "pkg", "vulns": [...]}]}
                    vuln_list = []
                    for dep in vulnerabilities.get("dependencies", []):
                        package_name = dep.get("name", "Unknown")
                        package_version = dep.get("version", "Unknown") 
                        for vuln in dep.get("vulns", []):
                            vuln_list.append({
                                "package": package_name,
                                "version": package_version,
                                **vuln
                            })
                else:
                    # Old format: {"vulnerabilities": [...]}
                    vuln_list = vulnerabilities.get("vulnerabilities", [])
                
                # Format vulnerability details for better LLM understanding
                formatted_vulns = []
                for vuln in vuln_list:
                    # Extract CVE IDs from aliases
                    aliases = vuln.get("aliases", [])
                    cve_ids = [alias for alias in aliases if alias.startswith('CVE-')]
                    
                    formatted_vulns.append({
                        "package": vuln.get("package", "Unknown"),
                        "version": vuln.get("version", vuln.get("installed_version", "Unknown")),
                        "vulnerability_id": vuln.get("id", "No ID"),
                        "cve_numbers": cve_ids,
                        "description": vuln.get("description", "No description"),
                        "fix_versions": vuln.get("fix_versions", []),
                        "severity": "HIGH" if any(word in vuln.get("description", "").lower() for word in ["overflow", "crash", "remote", "execute"]) else "MEDIUM"
                    })
                
                return json.dumps({
                    "status": "completed",
                    "vulnerabilities_found": len(formatted_vulns),
                    "summary": f"Found {len(formatted_vulns)} vulnerabilities",
                    "vulnerabilities": formatted_vulns
                })
                
            except json.JSONDecodeError as e:
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to parse JSON output: {str(e)}",
                    "raw_stdout": result.stdout,
                    "raw_stderr": result.stderr
                })
        else:
            # No JSON output - check if it's an actual error
            if result.returncode != 0:
                return json.dumps({
                    "status": "error",
                    "message": f"pip-audit failed with return code {result.returncode}",
                    "stderr": result.stderr,
                    "suggestion": "Ensure pip-audit is installed: pip install pip-audit"
                })
            else:
                return json.dumps({
                    "status": "completed",
                    "vulnerabilities_found": 0, 
                    "message": "No vulnerabilities detected"
                })
            
    except subprocess.TimeoutExpired:
        return json.dumps({
            "status": "timeout",
            "message": "Vulnerability scan timed out after 120 seconds"
        })
    except FileNotFoundError:
        return json.dumps({
            "status": "error",
            "message": "pip-audit not found. Please install it: pip install pip-audit"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during vulnerability scan: {str(e)}"
        })

# Tool schema for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_package_vulnerabilities",
            "description": "Scan a Python requirements-vulnerable.txt file for known security vulnerabilities",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements_file": {
                        "type": "string",
                        "description": "Path to the requirements-vulnerable.txt file to scan"
                    }
                },
                "required": ["requirements_file"]
            }
        }
    }
]

def security_assessment_llm(user_question, model="gpt-4o"):
    """LLM function with security vulnerability checking capability."""
    messages = [
        {
            "role": "system", 
            "content": "You are a DevSecOps security analyst. When you receive vulnerability scan results, you MUST present the ACTUAL findings in detail. For each vulnerability found, list: the exact package name, version, CVE numbers, vulnerability description, and recommended fix version. Start with 'SCAN RESULTS:' and then list each vulnerability. Do NOT provide generic security advice - only show the specific vulnerabilities that were detected in the scan."
        },
        {
            "role": "user", 
            "content": user_question
        }
    ]
    
    try:
        # Step 1: Get tool call from LLM
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        tool_calls = response_message.tool_calls
        if not tool_calls:
            return response_message.content
        
        # Step 2: Execute security scan
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "check_package_vulnerabilities":
                scan_result = check_package_vulnerabilities(function_args["requirements_file"])
                
                # Debug: Print what we're sending to the LLM (for testing)
                print("🔍 DEBUG: Scan result data:", scan_result[:500], "..." if len(scan_result) > 500 else "")
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": scan_result
                })
        
        # Step 3: Get final analysis from LLM
        final_response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return final_response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error during security assessment: {str(e)}"

# Example usage
if __name__ == "__main__":
    print("🔍 DevSecOps Dependency Vulnerability Scanner")
    print("=" * 50)
    
    # Check if we can run with OpenAI integration
    if API_KEY:
        # Scan using LLM integration
        analysis = security_assessment_llm(
            "Please scan the ./requirements-vulnerable.txt file in the current directory for security vulnerabilities. "
            "Provide a detailed assessment including severity levels and remediation recommendations."
        )
        print(analysis)
    else:
        print("⚠️  OpenAI API key not found - running direct scan mode")
        print()
        
        # Run direct vulnerability check
        result = check_package_vulnerabilities("./requirements-vulnerable.txt")
        
        try:
            data = json.loads(result)
            print(f"📊 Scan Status: {data.get('status', 'Unknown')}")
            print(f"🔍 Vulnerabilities Found: {data.get('vulnerabilities_found', 0)}")
            
            if data.get('vulnerabilities'):
                print("\n📋 Vulnerability Details:")
                print("-" * 40)
                
                for i, vuln in enumerate(data['vulnerabilities'][:10], 1):
                    print(f"\n{i}. 📦 Package: {vuln.get('package', 'Unknown')} v{vuln.get('version', 'Unknown')}")
                    
                    vuln_id = vuln.get('vulnerability_id', 'No ID')
                    aliases = vuln.get('aliases', [])
                    cve_ids = [alias for alias in aliases if alias.startswith('CVE-')]
                    if cve_ids:
                        print(f"   🚨 CVE: {', '.join(cve_ids[:2])}")
                    else:
                        print(f"   🔍 ID: {vuln_id}")
                    
                    desc = vuln.get('description', 'No description')
                    print(f"   📝 Description: {desc[:120]}...")
                    
                    fix_versions = vuln.get('fix_versions', [])
                    if fix_versions:
                        print(f"   ✅ Fix: Upgrade to {', '.join(fix_versions[:2])}")
                    
                total_vulns = len(data['vulnerabilities'])
                if total_vulns > 10:
                    print(f"\n   ... and {total_vulns - 10} more vulnerabilities")
            
            print(f"\n💡 Recommendation: Update pillow to latest version (>=10.3.0)")
            print("🔧 Command: pip install --upgrade pillow")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing results: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Security Tip: Regularly scan dependencies in your CI/CD pipeline!")