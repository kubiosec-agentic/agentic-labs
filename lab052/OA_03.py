import os
import json
import subprocess
import sys
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
        return f"Requirements file not found: {requirements_file}"
    
    try:
        # Run pip-audit to check for vulnerabilities
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pip-audit", "--quiet"
        ], capture_output=True, text=True, timeout=60)
        
        # Now run the actual vulnerability scan
        result = subprocess.run([
            sys.executable, "-m", "pip_audit", 
            "--requirement", requirements_file,
            "--format", "json"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            if result.stdout.strip():
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return json.dumps({
                        "status": "completed",
                        "vulnerabilities_found": len(vulnerabilities.get("vulnerabilities", [])),
                        "details": vulnerabilities
                    })
                except json.JSONDecodeError:
                    return json.dumps({
                        "status": "completed", 
                        "vulnerabilities_found": 0,
                        "message": "No vulnerabilities found",
                        "raw_output": result.stdout
                    })
            else:
                return json.dumps({
                    "status": "completed",
                    "vulnerabilities_found": 0, 
                    "message": "No vulnerabilities detected"
                })
        else:
            # Fallback: Manual vulnerability knowledge base for common packages
            return _manual_vulnerability_check(requirements_file)
            
    except subprocess.TimeoutExpired:
        return json.dumps({
            "status": "timeout",
            "message": "Vulnerability scan timed out"
        })
    except Exception as e:
        return _manual_vulnerability_check(requirements_file)

def _manual_vulnerability_check(requirements_file: str) -> str:
    """Manual check using known vulnerability patterns."""
    try:
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Known vulnerability patterns (simplified for demo)
        known_issues = {
            "flask": {
                "versions": ["<2.0.0"],
                "cve": "CVE-2019-1010083",
                "severity": "HIGH", 
                "description": "Potential denial of service vulnerability"
            },
            "requests": {
                "versions": ["<2.20.0"],
                "cve": "CVE-2018-18074",
                "severity": "MEDIUM",
                "description": "Potential request smuggling vulnerability"
            },
            "openai": {
                "versions": ["<1.0.0"],
                "cve": "N/A",
                "severity": "LOW",
                "description": "Consider updating to latest stable version"
            }
        }
        
        findings = []
        for pkg_line in packages:
            pkg_name = pkg_line.split('==')[0].split('>=')[0].split('<=')[0].strip()
            if pkg_name.lower() in known_issues:
                findings.append({
                    "package": pkg_name,
                    "installed_version": pkg_line,
                    "vulnerability": known_issues[pkg_name.lower()]
                })
        
        return json.dumps({
            "status": "manual_check_completed",
            "vulnerabilities_found": len(findings),
            "packages_scanned": len(packages),
            "findings": findings,
            "recommendation": "Install pip-audit for comprehensive scanning: pip install pip-audit"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error reading requirements file: {str(e)}"
        })

# Tool schema for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_package_vulnerabilities",
            "description": "Scan a Python requirements.txt file for known security vulnerabilities",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements_file": {
                        "type": "string",
                        "description": "Path to the requirements.txt file to scan"
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
            "content": "You are a DevSecOps security analyst. Help users identify and understand security vulnerabilities in their Python dependencies. Provide clear explanations and actionable remediation advice."
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
    
    # Scan the current lab's requirements
    analysis = security_assessment_llm(
        "Please scan the requirements.txt file in the current directory for security vulnerabilities. "
        "Provide a detailed assessment including severity levels and remediation recommendations."
    )
    
    print(analysis)
    print("\n" + "=" * 50)
    print("💡 Security Tip: Regularly scan dependencies in your CI/CD pipeline!")