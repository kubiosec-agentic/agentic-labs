# Analyzing Prompt and Chain Usage in prompt.py
## Introduction
Let’s analyze the following Python code that uses LangChain to generate and analyze a story.
```
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

llm = GoogleGenerativeAI(model="gemini-1.5-pro")

# First chain generates a story
story_prompt = PromptTemplate.from_template("Write a short story about {topic}")
story_chain = story_prompt | llm | StrOutputParser()

# Second chain analyzes the story
analysis_prompt = PromptTemplate.from_template(
    "Analyze the following story's mood:\n{story}"
)
analysis_chain = analysis_prompt | llm | StrOutputParser()

# Combine chains
story_with_analysis = story_chain | analysis_chain

# Run the combined chain
story_analysis = story_with_analysis.invoke({"topic": "a rainy day"})
print("\nAnalysis:", story_analysis)
```

## Step 1
###  Introducing package namespaces
```
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
```
Python packages and modules (like `langchain_core.prompts`) are used to organize code into logical groups.<br>
`prompts` and `output_parsers` are called a **namespace**.
## Step 2
### Instantiate the class
```
llm = GoogleGenerativeAI(model="gemini-1.5-pro")
```
## Step 3
###  Introducing `prompts`
`PromptTemplate.from_template(...)` creates a prompt with a placeholder `{topic}`, <br>
You can define `{topic}` later and fill in something like "robots" or "space" when you do the invokation.
```
# First chain generates a story
story_prompt = PromptTemplate.from_template("Write a short story about {topic}")
```
## Step 4
### Chains and LangChain Expression Language (LCE)
A chain is a sequence of steps (like `prompt → model → output`) that work together to turn input into meaningful output in LangChain and can be defined using _**LangChain Expression Language (LCE)**_. It’s a new, simplified way to build and compose chains using the | (pipe) operator.
```
story_chain = story_prompt | llm | StrOutputParser()
```
You can even combine chains
```
# Second chain analyzes the story
analysis_prompt = PromptTemplate.from_template(
    "Analyze the following story's mood:\n{story}"
)
analysis_chain = analysis_prompt | llm | StrOutputParser()
```
_Note: The output of `story_chain` becomes the input `analysis_chain`_

## Step 5
### Run the combined chain
Finally run the chain and define `{topic}` 
```
story_analysis = story_with_analysis.invoke({"topic": "a rainy day"})
print("\nAnalysis:", story_analysis)
```
