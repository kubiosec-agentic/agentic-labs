from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini", output_version="responses/v1")

tool = {"type": "web_search_preview"}
llm_with_tools = llm.bind_tools([tool])

response = llm_with_tools.invoke("What was a positive news story from today?")

print(response)
