# LAB05: Tool Based Agents
## Introduction
This lab explores tool-augmented agents and API call inspection using LangChain and OpenAI. You’ll experiment with:
- LangChain ReAct agents (with and without tools)
- Tool calling via OpenAI’s function schema (e.g., custom SQL simulation)
- Wikipedia integration for real-world queries
- A small CTF-style challenge (via UI or API)
- Deep inspection of API behavior using mitmproxy

Great for learning how to build, extend, and debug LLM agents with real tool support.
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab05/bin/activate
```
To avoide the **_LangSmith_** warnings (build, test, debug, and monitor framework developed **_LangChain_**)
```
export LANGCHAIN_TRACING_V2" = "false"
export LANGCHAIN_API_KEY"= ""
```
In your code you can add:
```
# Suppress LangSmith warnings 
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langsmith")
```

## Lab instructions
#### Example 1: LangChain chain without tool support
This next code uses LangChain abstractions to construct **_a processing chain_** that takes an English input string, formats it into a translation prompt, sends it to OpenAI's GPT-4 model for French translation, parses the model's output, and prints the result, demonstrating how LangChain's prompt templates, runnables, and output parsers can be orchestrated for LLM driven language tasks.
```
python3 LC_01_core.py
```
#### Example 2: LangChain chain with tool integration and structured output example
This script demonstrates how to use a LangChain chain with tool integration and structured output: it connects an LLM to a simple weather tool, handles tool invocation and result parsing, and feeds the result back into the chain for a final response. It uses the `ChatOpenAI` from `langchain_openai` class that provides an interface for interacting with OpenAI's chat-based language models, like GPT-3.5 and GPT-4, within the LangChain framework. It simplifies the process of sending prompts to these models and receiving their responses, making it easier to build conversational AI applications.
```
python3 LC_01.py
```
#### Example 3: Langchain agent without tool support
This is a simple example sets up a LangChain ReAct agent using GPT-4o with access  It uses a prompt template from LangChain Hub and executes queries with step-by-step reasoning and code execution.
```
python3 Tools_01.py
```
#### Example 4: Langchain agent with tool support
This next example sets up a LangChain ReAct agent using GPT-4o with access to a Python REPL tool for solving math problems. It uses a prompt template from LangChain Hub and executes queries with step-by-step reasoning and code execution.
```
python3 Tools_02.py
```
#### Example 5: Small CTF
Start the ChatBot. Try to hack it via the user interface.
```
docker run -it -p 8501:8501 \
  --rm \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  --name demochatbox \
  xxradar/mymadchatbox:v2  \
  /bin/bash -c "./start.sh & tail -f /dev/null"
```
You can connect to `http://127.0.0.1:8501/`<br>

#### Example 6: Small CTF - Optional (middleware function only)
Start the ChatBot. Try to hack it via the api (openai compatible).
```
python3 ./Tools_03.py
```
```
curl -XPOST http://127.0.0.1:5000/v1/chat/completions  \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxxxxxxxx" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is the SQRT of 12345"
          }
        ]
      }
    ]
  }'
```
#### Example 5: Langchain agent with Wikipedia support
This code sets up a LangChain ReAct agent powered by GPT-3.5-turbo, with access to the Wikipedia tool. It uses a custom prompt template to guide the agent through reasoning and action steps to answer complex questions using external knowledge sources.
```
python3 Tools_04.py
```
#### Example 6: Openai with custom tools support
This script sets up a tool-augmented OpenAI chat workflow using the chat.completions API with function calling. It defines a local SQL simulation tool (find_product), registers it in the OpenAI tool schema, and allows GPT (e.g., GPT-4o) to automatically call this function to answer product-related queries. The tool is executed locally, and the result is sent back to the model for final response generation.
```
python3 Tools_05.py
```
#### Example 7: Openai with custom tools support DEEPDIVE
This setup enables inspection of OpenAI API calls by routing them through a local MITM proxy (mitmproxy) in reverse mode. <br>
You’ll launch the proxy in `terminal_2`, then set the `OPENAI_BASE_URL` to point to it in `terminal_1`, allowing you to run scripts like `Tools_05.py` while capturing and viewing requests/responses in the mitmweb dashboard at http://127.0.0.1:8081.
#### Open a new terminal_2
```
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 127.0.0.1:8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --mode reverse:https://api.openai.com:443
```
You can nw connect to `http://127.0.0.1:8081/?token=<see_your_terminal>`
#### Continue in terminal_1
```
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
```
```
python3 Tools_05.py
```
#### Optional for hackers
Modify `Tools_02.py` and `Tools_04.py`
```
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, base_url="http://127.0.0.1:8080/v1")
```

## Cleanup environment
```
unset OPENAI_BASE_URL
```
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
