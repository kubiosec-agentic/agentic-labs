"""
Custom translation pipeline with LangChain runnables and OpenAI.

Wraps a raw OpenAI Chat Completions call inside a RunnableLambda, then
composes it into a LangChain chain: ChatPromptTemplate | LLM | StrOutputParser.

This shows how to use LangChain's chain abstraction while keeping full control
over the underlying API call.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

# ---- Prompt template ----
prompt = ChatPromptTemplate.from_template("Translate this to French: {text}")


# ---- OpenAI call wrapped as a Runnable ----
def call_openai(prompt_value):
    messages = prompt_value.to_messages()
    openai_messages = [
        {
            "role": "user" if msg.type == "human" else msg.type,
            "content": msg.content,
        }
        for msg in messages
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=openai_messages,
    )
    return response.choices[0].message.content


llm = RunnableLambda(call_openai)
parser = StrOutputParser()

# ---- Chain: Prompt -> LLM -> Output ----
chain = prompt | llm | parser

result = chain.invoke({"text": "Good morning, how are you?"})
print(result)
