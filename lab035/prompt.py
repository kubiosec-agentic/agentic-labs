from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
llm = ChatOpenAI(model="gpt-5-mini")
parser= StrOutputParser()

# First chain generates a story
story_prompt = PromptTemplate.from_template("Write a short story about {topic}")
story_chain = story_prompt | llm | parser

# Second chain analyzes the story
analysis_prompt = PromptTemplate.from_template(
    "Analyze the following story's mood:\n{story}"
)

analysis_chain = analysis_prompt | llm | parser

# Combine chains
story_with_analysis = story_chain | analysis_chain

# Run the combined chain
story_analysis = story_with_analysis.invoke({"topic": "a rainy day"})
print("\nAnalysis:", story_analysis)
