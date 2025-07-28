from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
import openai
import os

# --- Set OpenAI API key ---
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# --- Prompt Template ---
prompt = ChatPromptTemplate.from_template("Translate this to French: {text}")

# --- OpenAI call as a Runnable ---
def call_openai(prompt_value):
    messages = prompt_value.to_messages()
    openai_messages = [
        {"role": "user" if msg.type == "human" else msg.type, "content": msg.content}
        for msg in messages
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=openai_messages
    )
    return response.choices[0].message.content

llm = RunnableLambda(call_openai)
parser = StrOutputParser()

# --- Chain: Prompt → LLM → Output ---
chain = prompt | llm | parser 

# --- Run inference ---
result = chain.invoke({"text": "Good morning, how are you?"})
print(result)
