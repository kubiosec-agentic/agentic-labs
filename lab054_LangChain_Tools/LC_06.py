"""
Swapping providers with a config switch.

The point of LangChain's model abstraction: the prompt, the chain and the
output code stay identical, only the model object changes. Flip USE_GEMINI
and the same pipeline runs on Google Gemini instead of OpenAI.

  export USE_GEMINI=1   # needs GOOGLE_API_KEY
  export USE_GEMINI=0   # needs OPENAI_API_KEY (default)
"""

import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

use_gemini = os.getenv("USE_GEMINI", "0") == "1"

if use_gemini:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
    print("Using Google Gemini")
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    print("Using OpenAI GPT")

# Everything below is provider-independent
prompt = PromptTemplate.from_template("Write me a terraform plan for {topic}.")
chain = prompt | llm | StrOutputParser()

result = chain.invoke(
    {"topic": "an S3 bucket with versioning enabled in us-west-2 and public access blocked"}
)
print("\nGenerated:")
print(result)
