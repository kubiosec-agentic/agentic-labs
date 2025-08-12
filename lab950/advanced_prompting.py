from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI

# Initialize chat model
chat = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=100)

# Define prompt using roles
system_msg = SystemMessagePromptTemplate.from_template("You are a witty assistant who tells short and funny jokes.")
user_msg = HumanMessagePromptTemplate.from_template("{input}")

prompt = ChatPromptTemplate.from_messages([system_msg, user_msg])

# Create the chain: prompt → model → output parser
from langchain_core.output_parsers import StrOutputParser
chain = prompt | chat | StrOutputParser()

# Run the chain
response = chain.invoke({"input": "Tell me a joke about light bulbs!"})
print(response)
