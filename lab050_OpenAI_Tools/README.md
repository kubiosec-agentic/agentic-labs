![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Tools](https://img.shields.io/badge/Tools-purple) ![Python](https://img.shields.io/badge/Python-blue)

# LAB050: OpenAI Function Calling and Tool Integration

## Introduction

LLMs can generate text, but they cannot execute code, query databases, or call APIs on their own. **Function calling** (tool use) bridges this gap: you define tools as JSON schemas, the model decides when to call them, and your code executes the actual function. The model then uses the result to produce a final answer.

These examples use the **Chat Completions API** with the `tools` parameter. While we use OpenAI's GPT-4o here, the same pattern works with any provider that supports the Chat Completions format with tool use: Azure OpenAI, Mistral, Groq, Together AI, and local models served through OpenAI-compatible endpoints (Ollama, vLLM, LM Studio). To switch providers, set the `OPENAI_BASE_URL` environment variable to point at a different endpoint.

This lab walks through four examples of increasing complexity, plus a bonus step that uses mitmproxy to inspect the raw API traffic.

| Step | Script | Tool | What it demonstrates |
|------|--------|------|---------------------|
| 1 | `OA_01.py` | `summarize_directory` | Basic tool-call flow: model calls a local function, gets results, answers |
| 2 | `OA_02.py` | `find_product` (SQL) | Simulated SQL execution; model generates a query, tool returns mock data |
| 3 | `OA_03.py` | `check_package_vulnerabilities` | DevSecOps: pip-audit as a tool; real vulnerability scanning |
| 4 | `OA_04.py` | `search_security_innovators` | External API: Wikipedia search as a tool |
| 5 | mitmproxy | (inspection) | Intercept and inspect OpenAI API calls |

## Set up your environment

```bash
export OPENAI_API_KEY="your-key-here"
```

```bash
./lab_setup.sh
source .lab050/bin/activate
```

## Lab instructions

### Step 1: Directory analysis tool (`OA_01.py`)

The simplest possible tool-call example. The model receives a user question about directory contents, decides to call `summarize_directory`, gets back a file-type summary, and produces a natural-language answer.

```bash
python3 OA_01.py
```

**What to observe:**
- The three-phase flow: (1) model emits a `tool_calls` response, (2) your code runs the function, (3) model gets the result and answers
- The `tool_choice="auto"` parameter lets the model decide whether to call the tool or answer directly
- The JSON arguments the model generates for the tool call (check the `arguments` field)

### Step 2: SQL simulation with tool use (`OA_02.py`)

The model generates a SQL query based on a natural-language request. A local function "executes" it (returns mock data), and the model summarizes the result. This pattern is common in database-backed agents.

```bash
python3 OA_02.py
```

**What to observe:**
- The model generates syntactically valid SQL from a plain English request
- The tool returns structured data (JSON), not natural language
- The model's final response incorporates the tool output naturally
- The `OPENAI_BASE_URL` env var is supported: set it to route requests through a proxy (see Step 5)

**Exercise: parallel tool calls and blind execution**

Open `OA_02.py` and change the prompt on the last line to:

```python
"Create an SQL query to update the price of the blue pen to 5 dollars and remove the stale red pen"
```

Run it again and watch the output. The model now returns **two** tool calls in a single response: an UPDATE and a DELETE. Both are executed automatically by the loop, without any human confirmation. The user asked one question; the system silently ran two database operations, one of them destructive.

This is a core risk in agentic tool use. The model decides which tools to call, how many times, and with what arguments. If your execution layer trusts the model unconditionally, a single user prompt (or a prompt injection hidden in retrieved context) can trigger actions the user never intended.

Things to think about:
- What would happen if the tool were connected to a real database?
- How would you add a human-in-the-loop confirmation step before executing destructive operations?
- Could you filter tool calls by operation type (e.g., allow SELECT, block DELETE) before execution?

Use mitmproxy (Step 5) to inspect the raw API traffic for this prompt. Look at the `tool_calls` array in the first response: you will see two entries, each with its own `id`, `function.name`, and `function.arguments`. The second request must include a `tool` role message for every `tool_call_id`, or the API rejects it with a 400 error.

### Step 3: DevSecOps vulnerability scanner (`OA_03.py`)

A security-focused example where the tool is `pip-audit`, a real dependency scanner. The model decides to scan `requirements-vulnerable.txt` (which contains `pillow==6.2.0` with known CVEs), receives the JSON vulnerability report, and provides a security assessment.

```bash
python3 OA_03.py
```

The script works in two modes: with `OPENAI_API_KEY` set, the LLM analyzes the scan results and provides remediation advice. Without the key, it runs pip-audit directly and prints formatted output.

**What to observe:**
- The tool executes a real subprocess (`pip-audit`), not a mock function
- pip-audit sends summary messages to stderr and JSON data to stdout; the tool handles both
- The LLM's system prompt is tuned for security analysis: it asks the model to present actual findings, not generic advice
- The `requirements-vulnerable.txt` file is intentionally insecure (for testing only)

### Step 4: Wikipedia research tool (`OA_04.py`)

Demonstrates tool use with an external API. The model searches Wikipedia for cybersecurity pioneers, retrieves page summaries, and synthesizes a research overview. Unlike Steps 1-3 where the tool runs locally, this tool makes network calls to Wikipedia.

```bash
python3 OA_04.py
```

**What to observe:**
- The model may issue multiple tool calls in one turn (searching for different people)
- The tool handles Wikipedia disambiguation pages gracefully
- The response includes URLs to Wikipedia pages for further reading
- Compare with Step 1: same tool-call pattern, but the tool itself calls an external API

### Step 5: API call inspection with mitmproxy

This is not a script but a setup that lets you intercept and inspect the HTTP traffic between your code and OpenAI. It uses mitmproxy in reverse mode to sit between your client and `api.openai.com`.

**Terminal 1:** Start the mitmproxy container:

```bash
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 127.0.0.1:8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --set block_global=false \
        --mode reverse:https://api.openai.com:443
```

Open the web UI at `http://127.0.0.1:8081` (the token is shown in Terminal 1 output).

**Terminal 2:** Point the OpenAI client at the proxy and run any script:

```bash
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
python3 OA_02.py
```

**What to observe:**
- The full request/response cycle in the mitmproxy web UI
- The `tools` array in the request body: this is how tool schemas are sent to the model
- The `tool_calls` field in the response: the model's decision to call a function
- The second request with the `tool` role message: feeding results back to the model
- Headers, tokens, and latency information

When done, reset the base URL:

```bash
unset OPENAI_BASE_URL
```

## Cleanup environment

```bash
deactivate
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
