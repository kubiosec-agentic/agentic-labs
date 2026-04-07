"""
LangChain with OpenAI Responses API: code interpreter tool.

Same pattern as LC_03.py but uses the code_interpreter hosted tool
instead of web search. The model writes and executes Python code
server-side to solve a math problem.
"""

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", output_version="responses/v1")

tool = {
    "type": "code_interpreter",
    "container": {"type": "auto"},
}
llm_with_tools = llm.bind_tools([tool])

response = llm_with_tools.invoke("What is sqrt of 5499 times 89.3?")
print(response.content)
