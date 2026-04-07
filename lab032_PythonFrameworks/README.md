![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![ChatCompletion](https://img.shields.io/badge/ChatCompletion-green) ![Responses_API](https://img.shields.io/badge/Responses_API-brightgreen) ![Python](https://img.shields.io/badge/Python-blue)

# LAB032: Python Frameworks

## Introduction
In lab010 and lab020, you called the OpenAI API with `curl`. That works for quick experiments, but real integrations need a proper programming language. This lab makes the transition from curl to Python in three steps:

1. **`requests` library**: the Python equivalent of curl. You build the HTTP request yourself (headers, JSON body, response parsing). If you've been doing curl, this will feel familiar.
2. **OpenAI Python SDK**: a purpose-built library that hides the HTTP details. Two lines replace twenty.
3. **Responses API features**: multi-turn conversations with `previous_response_id`, code execution, and structured output with Pydantic.

Along the way, you'll also learn to use `mitmproxy` to intercept and inspect API traffic, a skill that transfers directly to security analysis and debugging.

## Set up your environment

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
./lab_setup.sh
source .lab032/bin/activate
```

## Lab instructions

### Step 1: From curl to Python with `requests`

Open `requests_01.py` in your editor and compare it to the curl commands from lab010. The structure is the same: you set the URL, headers (including the Bearer token), and a JSON body, then make a POST request and parse the response. This is literally what curl does, but now in Python where you can add logic, loops, and error handling around it.
```bash
python3 ./requests_01.py
```

**Things to observe:**
- The `headers` dict mirrors the `-H` flags from curl
- The `data` dict is the same JSON payload you passed with `-d`
- `response.json()['choices'][0]['message']['content']` is the Python equivalent of `| jq '.choices[0].message.content'`

This is useful to know, but verbose. For everything beyond one-off experiments, use the SDK.

### Step 2: The OpenAI Python SDK

The SDK wraps all that HTTP plumbing into a clean Python API. Compare `chat_01.py` to `requests_01.py`: same result, much less code, and the SDK handles authentication, retries, and error handling for you.
```bash
python3 ./chat_01.py
```

**Things to observe:**
- `OpenAI()` picks up `OPENAI_API_KEY` from the environment automatically
- `client.chat.completions.create(...)` replaces the manual HTTP request
- The response is a typed Python object, not raw JSON

### Inspecting API calls with mitmproxy

Regardless of whether you use `requests` or the SDK, the same HTTP requests are being made under the hood. `mitmproxy` lets you see exactly what's going over the wire, which is invaluable for debugging, security analysis, and understanding how tool calls and streaming work.

Start mitmproxy in a **second terminal**:
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

Open the mitmproxy web interface at `http://127.0.0.1:8081`

Back in your **first terminal**, redirect the SDK to go through mitmproxy:
```bash
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
python3 ./chat_01.py
```

Check the mitmproxy web interface: you'll see the full HTTP request and response, including headers, the JSON body, and token usage. Try running the other scripts through it too.

When done inspecting, restore the default base URL:
```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Step 3: Interactive chatbot with conversation history

`chat_02.py` builds a simple interactive chatbot. It keeps a `messages` list and appends every user message and assistant reply, so the model has full context on every turn. This is the same pattern you did manually in lab010 (resending the full history), but now in a loop.
```bash
python3 ./chat_02.py
```

Type a few messages, then ask it to summarize the conversation. Type `exit` to quit.

**Things to observe:**
- The `messages` list grows with every turn, each turn costs more tokens
- The conversation is stateful *in your code*, not on the server
- Compare this to `resp_01.py` below, which achieves the same thing server-side

### Step 4: Reasoning models and pentest prompt engineering

`chat_03.py` demonstrates two things at once: using a reasoning model (`o4-mini` with `reasoning_effort`) and the art of rephrasing a request so the model can help ethically. The conversation starts with "Can you hack this website?" (refused), pivots to "how should I phrase it?" (model explains), and ends with a properly scoped pentest methodology request (model complies with detailed output).
```bash
python3 ./chat_03.py
```

**Things to observe:**
- The `reasoning_effort="medium"` parameter controls how much the model "thinks" before answering. Try changing it to `"high"` and compare the output quality
- The multi-turn conversation history shows how context shapes the model's willingness to help
- The final response includes specific tools and commands for a legitimate penetration test, which the model only provides after proper authorization framing

This pattern is directly relevant for security professionals: the way you phrase a request determines what the model will and won't do.

### Step 5: Responses API with multi-turn conversations

Now switch from the Chat Completions SDK to the Responses API SDK. The key difference: instead of managing a `messages` list, you just pass `previous_response_id` and the server handles context.
```bash
python3 ./resp_01.py
```

`resp_02.py` extends this to three turns. Notice how each follow-up only sends the new input plus a reference to the previous response ID:
```bash
python3 ./resp_02.py
```

Compare the code in `chat_02.py` (manual history) vs `resp_01.py` (server-side history). Which is simpler? Which gives you more control?

### Step 6: Code Interpreter

The Responses API can spin up a sandboxed container and execute Python code inside it. This is useful when the model needs to compute something precisely rather than approximate it with language.
```bash
python3 ./resp_03.py
```

**Things to observe:**
- `client.containers.create()` provisions a sandbox
- The `code_interpreter` tool is passed in the `tools` list
- `tool_choice="required"` forces the model to use the tool (instead of just guessing the answer)
- Try running this through mitmproxy to see the tool call and execution flow

### Step 7: Structured output with Pydantic

In lab020's ADDON, you defined JSON schemas manually in curl. The Python SDK can generate schemas automatically from Pydantic models. This is cleaner, type-safe, and catches schema errors at development time rather than runtime.
```bash
python3 ./resp_04.py
```

**Things to observe:**
- The `Step` and `MathReasoning` Pydantic classes define the output schema in pure Python
- `client.responses.parse()` returns a typed Python object, not raw JSON
- `response.output_parsed` gives you direct attribute access (no `json.loads()` needed)
- Compare this to the manual `text.format` approach in lab020's ADDON

## Cleanup environment
Don't forget to **unset** the proxy variable if you used mitmproxy:
```bash
unset OPENAI_BASE_URL
deactivate
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
