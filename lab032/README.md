
![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Responses_API](https://img.shields.io/badge/Responses_API-brightgreen) ![Python](https://img.shields.io/badge/Python-blue) ![Tools](https://img.shields.io/badge/Tools-purple)

# LAB32: Python Frameworks
This lab introduces frameworks, demonstrating how to build powerful language model workflows using Python and the OpenAI SDK.<br>
The lab also covers the use of `mitmproxy` to deepen your understanding and visualize the requests, including tool calls and reasoning patterns.
## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab032/bin/activate
```
## Lab instructions

##### From `curl` to Python Chat Completion
This very first example should help to understand how we can easily convert our previous `curl` examples into code and how to start abstracting away error-prone details using SDKs.
```
python3 ./requests_01.py
```
#### Chat completion via OpenAI Python SDK
This lab demonstrates how to make a Chat Completions API call using Python, and how to intercept and inspect the request using `mitmproxy` for debugging or learning purposes. **(Terminal_1)**
```
export OPENAI_BASE_URL="https://api.openai.com/v1"
```
```
python3 chat_01.py
```
Inspect the Chat completion call with `mitmproxy` **(Terminal_2)**
```
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 127.0.0.1:8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --set block_global=false \
        --mode reverse:https://api.openai.com:443
```
Open your browser at `http://127.0.0.1:8081/?token=xxxxxx`<br><br>
In **Terminal_1**, update the base URL for you client application.
```
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
```
```
python3 chat_01.py
```
Don't forget to unset the environment variable !
```
unset OPENAI_BASE_URL
```

#### Responses API via OpenAI Python SDK and message callback
This lab shows how to build a multi-turn conversation using the `previous_response_id`, allowing the model to maintain context and respond more naturally across messages.
```
python3 ./resp_01.py
```
Also check out the next sample. What do you notice?
```
python3 ./resp_02.py
```
#### Interactive Chatbot with Chat Completions
This example demonstrates building an interactive chatbot that maintains conversation history across multiple turns.
```
python3 ./chat_02.py
```

#### Responses API and Code Executor
The Code Interpreter tool requires a container object. A container is a fully sandboxed virtual machine that the model can run Python code in. 
This container can contain files that you upload, or that it generates. Note: Uses gpt-4.1 model which may need to be updated to a valid model like gpt-4o.
```
python3 ./resp_03.py
```
Apply the previous technique using `mitmproxy` to analyse what is happening under the hood.

#### Responses API and Structured output using Pydantic
Pydantic is a Python library for data validation and data parsing using Python type hints. <br>
It allows you to define data models with expected fields and types, and it will:
- validate incoming data
- parse it into structured objects
- raise clear errors if the data doesn't match

```
python3 ./resp_04.py
```

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
