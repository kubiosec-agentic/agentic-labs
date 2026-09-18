"""
Hosted tools via the OpenAI Responses API.

Setting output_version="responses/v1" makes ChatOpenAI talk to the Responses
API instead of Chat Completions. That unlocks OpenAI's hosted tools: the tool
runs on OpenAI's servers, nothing executes on your machine.

  - web_search_preview: the model searches the live web
  - code_interpreter:   the model writes and runs Python in an OpenAI sandbox

Compare with LC_03 (tool runs in your code) and LC_05 (tool runs in your
process, unsandboxed).

Note: in the responses/v1 format, response.content is a list of content
blocks (text, annotations with source URLs, ...) instead of a plain string.
"""

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", output_version="responses/v1")


# ---- 1. Web search --------------------------------------------------------

web_search = {"type": "web_search_preview"}

response = llm.bind_tools([web_search]).invoke(
    "What was a positive news story from today?"
)
print("\n=== Web search ===")
print(response.content)


# ---- 2. Code interpreter --------------------------------------------------

code_interpreter = {
    "type": "code_interpreter",
    "container": {"type": "auto"},   # OpenAI picks the runtime
}

response = llm.bind_tools([code_interpreter]).invoke(
    "What is sqrt of 5499 times 89.3?"
)
print("\n=== Code interpreter ===")
print(response.content)
