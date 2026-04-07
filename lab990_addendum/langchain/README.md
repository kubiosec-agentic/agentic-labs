![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Google](https://img.shields.io/badge/Google-orange) ![Tools](https://img.shields.io/badge/Tools-purple) ![Security](https://img.shields.io/badge/Security-red)

# LAB990 Addendum: Advanced LangChain Examples

## Introduction

These examples go beyond the basics covered in [lab035](../../lab035_Langchain/README.md). They show how LangChain works in more realistic scenarios: calling external APIs through tools, running CLI commands, reviewing code for security issues, and building a simple writing assistant with a web UI.

Each script is self-contained and can be run independently.

## Set up your environment

This addendum runs inside the lab035 virtual environment. Complete the [lab035 setup](../../lab035_Langchain/README.md) first, then install the additional dependencies:

```bash
cd ../../lab035_Langchain
source .lab035/bin/activate
pip install -r ../lab990_addendum/langchain/requirements.txt
cd ../lab990_addendum/langchain
```

```bash
export OPENAI_API_KEY="your-key-here"

# Only needed for easy_swap.py (Google AI Studio key)
# export GOOGLE_API_KEY="your-key-here"
```

## Examples

### 1. Weather forecast with LangChain tools (`weather_forecast.py`)

A complete tool-use workflow: the LLM decides it needs weather data, calls a `get_weather` tool, gets real data from the Open-Meteo API (free, no key), and summarizes it in natural language.

What to observe: the 4-step tool-use loop (LLM decides, tool executes, result fed back, LLM summarizes). The geocoding step (Nominatim) can take a few seconds, which is a good reminder that tool latency comes from external services, not the model.

```bash
python3 weather_forecast.py
```

### 2. Multi-provider LLM swapping (`easy_swap.py`)

A single boolean flips the entire pipeline between OpenAI and Google Gemini. The prompt, chain, and output code stay identical. Generates Terraform plans as an example workload.

> **Note:** A copy of this script also lives in **lab035** as `lc06_easy_swap.py`.

```bash
# Requires GOOGLE_API_KEY for the Gemini path
python3 easy_swap.py
```

### 3. CLI command execution tool (`bash_tool.py`)

Gives the LLM a `run_cli_command` tool that can execute shell commands. Includes a safelist (`ls`, `pwd`, `whoami`, `date`, etc.) to prevent arbitrary execution. Demonstrates the full tool-call loop: LLM requests a command, tool runs it, output is fed back for a natural-language answer.

From a security training perspective, pay attention to the safelist approach and think about how it could be bypassed.

```bash
python3 bash_tool.py
```

### 4. Shell script security analysis, local files (`file_security_review.py`)

Loads `.sh` files from a local `test_repo/` directory and sends them to GPT-4o for a security review. Looks for command injection, hardcoded credentials, path traversal, missing error handling, and more.

```bash
# Prepare a test directory with shell scripts
mkdir -p test_repo
curl -O --output-dir test_repo https://raw.githubusercontent.com/xxradar/TLSSAN_scanner/refs/heads/master/tlssan_scan.sh

python3 file_security_review.py
```

### 5. Shell script security analysis, via Git (`review_with_gitloader.py`)

Same security review, but uses LangChain's `GitLoader` to clone a repository and extract `.sh` files directly. Useful when you want to analyze a remote repo without manually downloading files.

```bash
# Requires GitPython (included in requirements.txt)
# Clones the repo into ./git_repo on first run
python3 review_with_gitloader.py
```

### 6. Code security review with structured output (`security_review.py`)

Uses a Pydantic model (`SecurityAnalysis`) to get structured JSON output from the LLM: a list of vulnerabilities, mitigation suggestions, and a risk level. Analyzes any source file you point it at. Defaults to `sample.py` (an intentionally vulnerable Flask app with XSS).

```bash
# Analyze the included vulnerable sample
python3 security_review.py

# Or point it at any file
python3 security_review.py /path/to/your/code.py
```

### 7. Vulnerable Flask app (`sample.py`)

A deliberately vulnerable web application used as input for `security_review.py`. Contains an XSS vulnerability through unescaped user input in a Jinja2 template. Do not deploy this; it exists purely as a target for the security review.

```bash
# Only run this if you want to test the XSS manually
python3 sample.py
# Then visit http://127.0.0.1:5000/?q=<script>alert(1)</script>
```

### 8. Writing assistant with Gradio UI (`writing_assistant.py`)

A simple web-based writing assistant that checks grammar, spelling, style, and conciseness. Uses Gradio for the frontend and LangChain + GPT-4o for the analysis. Includes a temperature slider to control creativity.

```bash
pip install gradio
python3 writing_assistant.py
# Opens at http://127.0.0.1:7860
```

## Dependencies

See `requirements.txt`. Core packages: `langchain-openai`, `langchain-core`, `langchain`, `pydantic`. Weather-specific: `openmeteo-requests`, `pandas`, `requests-cache`, `retry-requests`, `geopy`. Writing assistant requires `gradio` (install separately).

## Notes

- The weather example uses the free Open-Meteo API (no key required), but Nominatim geocoding can be slow
- The multi-provider example requires both `OPENAI_API_KEY` and `GOOGLE_API_KEY`
- The security analysis tools are designed for educational purposes and defensive security only
- `sample.py` is intentionally vulnerable; do not expose it to a network

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
