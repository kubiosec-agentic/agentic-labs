"""
DevSecOps dependency vulnerability scanner with OpenAI function calling.

The LLM decides to scan a requirements file using pip-audit, receives the
JSON vulnerability report, and provides a security assessment with
remediation advice.

Runs in two modes:
  - With OPENAI_API_KEY: full LLM-powered analysis
  - Without: direct pip-audit scan with formatted output
"""

import os
import json
import subprocess
from openai import OpenAI

client = OpenAI()


def check_package_vulnerabilities(requirements_file: str) -> str:
    """Scan Python dependencies for known vulnerabilities using pip-audit."""
    if not os.path.exists(requirements_file):
        return json.dumps({
            "status": "error",
            "message": f"Requirements file not found: {requirements_file}"
        })

    try:
        result = subprocess.run(
            ["pip-audit", "--requirement", requirements_file, "--format", "json"],
            capture_output=True, text=True, timeout=120,
        )

        if result.stdout.strip():
            try:
                vulnerabilities = json.loads(result.stdout)

                # Handle both old and new pip-audit JSON formats
                if "dependencies" in vulnerabilities:
                    vuln_list = []
                    for dep in vulnerabilities.get("dependencies", []):
                        pkg = dep.get("name", "Unknown")
                        ver = dep.get("version", "Unknown")
                        for vuln in dep.get("vulns", []):
                            vuln_list.append({"package": pkg, "version": ver, **vuln})
                else:
                    vuln_list = vulnerabilities.get("vulnerabilities", [])

                formatted = []
                for vuln in vuln_list:
                    aliases = vuln.get("aliases", [])
                    cves = [a for a in aliases if a.startswith("CVE-")]
                    formatted.append({
                        "package": vuln.get("package", "Unknown"),
                        "version": vuln.get("version", vuln.get("installed_version", "Unknown")),
                        "vulnerability_id": vuln.get("id", "No ID"),
                        "cve_numbers": cves,
                        "description": vuln.get("description", "No description"),
                        "fix_versions": vuln.get("fix_versions", []),
                    })

                return json.dumps({
                    "status": "completed",
                    "vulnerabilities_found": len(formatted),
                    "summary": f"Found {len(formatted)} vulnerabilities",
                    "vulnerabilities": formatted,
                })

            except json.JSONDecodeError as e:
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to parse JSON output: {str(e)}",
                    "raw_stdout": result.stdout,
                    "raw_stderr": result.stderr,
                })
        else:
            if result.returncode != 0:
                return json.dumps({
                    "status": "error",
                    "message": f"pip-audit failed (rc={result.returncode})",
                    "stderr": result.stderr,
                })
            return json.dumps({
                "status": "completed",
                "vulnerabilities_found": 0,
                "message": "No vulnerabilities detected",
            })

    except subprocess.TimeoutExpired:
        return json.dumps({"status": "timeout", "message": "Scan timed out after 120s"})
    except FileNotFoundError:
        return json.dumps({"status": "error", "message": "pip-audit not found. Install: pip install pip-audit"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# --- Tool schema ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_package_vulnerabilities",
            "description": "Scan a Python requirements file for known security vulnerabilities using pip-audit",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements_file": {
                        "type": "string",
                        "description": "Path to the requirements file to scan",
                    }
                },
                "required": ["requirements_file"],
            },
        },
    }
]

SYSTEM_PROMPT = (
    "You are a DevSecOps security analyst. When you receive vulnerability scan "
    "results, present the ACTUAL findings in detail. For each vulnerability, list: "
    "the exact package name, version, CVE numbers, description, and recommended "
    "fix version. Start with 'SCAN RESULTS:' then list each vulnerability. "
    "Do NOT provide generic security advice; only show what the scan detected."
)


def security_assessment_llm(user_question, model="gpt-4o"):
    """LLM with pip-audit tool for vulnerability scanning."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]

    # Step 1: LLM decides to call the tool
    response = client.chat.completions.create(
        model=model, messages=messages, tools=tools, tool_choice="auto",
    )

    response_message = response.choices[0].message
    messages.append(response_message)

    tool_calls = response_message.tool_calls
    if not tool_calls:
        return response_message.content

    # Step 2: Execute the scan
    for tool_call in tool_calls:
        function_args = json.loads(tool_call.function.arguments)
        scan_result = check_package_vulnerabilities(function_args["requirements_file"])

        print(f"[debug] Scan result preview: {scan_result[:200]}...")

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": scan_result,
        })

    # Step 3: LLM summarizes
    final = client.chat.completions.create(model=model, messages=messages)
    return final.choices[0].message.content


if __name__ == "__main__":
    print("DevSecOps Dependency Vulnerability Scanner")
    print("=" * 50)

    if os.getenv("OPENAI_API_KEY"):
        analysis = security_assessment_llm(
            "Scan ./requirements-vulnerable.txt for security vulnerabilities. "
            "Provide a detailed assessment with severity and remediation."
        )
        print(analysis)
    else:
        print("OPENAI_API_KEY not set, running direct scan.\n")
        result = check_package_vulnerabilities("./requirements-vulnerable.txt")
        data = json.loads(result)

        print(f"Status: {data.get('status', 'Unknown')}")
        print(f"Vulnerabilities found: {data.get('vulnerabilities_found', 0)}")

        for i, vuln in enumerate(data.get("vulnerabilities", [])[:10], 1):
            cves = vuln.get("cve_numbers", [])
            cve_str = ", ".join(cves[:2]) if cves else vuln.get("vulnerability_id", "N/A")
            fix = ", ".join(vuln.get("fix_versions", [])[:2]) or "N/A"
            print(f"\n  {i}. {vuln['package']} v{vuln['version']}")
            print(f"     CVE: {cve_str}")
            print(f"     Fix: upgrade to {fix}")

        total = len(data.get("vulnerabilities", []))
        if total > 10:
            print(f"\n  ... and {total - 10} more")

    print("\n" + "=" * 50)
    print("Tip: Add pip-audit to your CI/CD pipeline for continuous scanning.")
