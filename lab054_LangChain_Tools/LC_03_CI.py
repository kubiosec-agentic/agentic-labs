from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini", output_version="responses/v1")

tool =  {
      "type": "code_interpreter",
      "container": { "type": "auto" }
    }
llm_with_tools = llm.bind_tools([tool])

response = llm_with_tools.invoke("What is sqrt of 5499 times 89.3 ?")

print(response.content)



