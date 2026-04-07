"""
LangChain with OpenAI Responses API: web search tool.

Uses output_version="responses/v1" to access the Responses API through
LangChain's ChatOpenAI wrapper. The web_search_preview tool lets the
model fetch live information from the web to answer current-events queries.
"""

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", output_version="responses/v1")

tool = {"type": "web_search_preview"}
llm_with_tools = llm.bind_tools([tool])

response = llm_with_tools.invoke("What was a positive news story from today?")
print(response)
