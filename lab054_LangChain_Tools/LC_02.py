"""
Prompt templates and chains (LCEL).

Two ideas in one script:

  1. ChatPromptTemplate with system + user roles. The system role sets the
     persona, the user role carries the {input} variable.
  2. The pipe operator. prompt | llm | parser builds a chain where every
     piece is a "Runnable". The output of one flows into the next, like a
     Unix pipe. Chains can be piped into other chains.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
parser = StrOutputParser()   # turns the AIMessage into a plain string


# ---- 1. A prompt with roles, piped into the model ------------------------

joke_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a witty assistant who tells short and funny jokes."),
    ("user", "{input}"),
])

joke_chain = joke_prompt | llm | parser

print("\n=== Joke ===")
print(joke_chain.invoke({"input": "Tell me a joke about light bulbs!"}))


# ---- 2. Chaining chains ---------------------------------------------------

# The output string of joke_chain becomes the {joke} variable of this prompt.
review_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a comedy critic. Answer in two sentences."),
    ("user", "Rate this joke from 1 to 10 and explain why:\n\n{joke}"),
])

review_chain = review_prompt | llm | parser

joke_and_review = joke_chain | (lambda joke: {"joke": joke}) | review_chain

print("\n=== Joke + review ===")
print(joke_and_review.invoke({"input": "Tell me a joke about firewalls!"}))
