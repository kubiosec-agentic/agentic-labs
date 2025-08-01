# Analyzing  `prompt.py`
## Introduction
Let's analyse the following code.
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
You can define `{topic}` later and fill in something like "robots" or "space" when you invoke the prompt.
```
# First chain generates a story
story_prompt = PromptTemplate.from_template("Write a short story about {topic}")
```
### Chains and LangChain Expression Language (LCE)
Create a chain
```
story_chain = story_prompt | llm | StrOutputParser()
```
The `|` (pipe operator) connects these steps into a chain: Prompt → Model → Output Parser. <br>
This syntax is known LCE = LangChain Expression Language <br>
It’s a new, simplified way introduced in LangChain to build and compose chains using the | (pipe) operator <br>

You can even combine chains
```
story_with_analysis = story_chain | analysis_chain
```
_Note: The output of `story_chain` becomes the input `analysis_chain`_

## Step 4 
Chains in LangChain let you connect multiple steps together into one logical pipeline.
They organize your prompt, model, parsing, and post-processing — so you don’t have to do everything manually.```
# Run the combined chain
story_analysis = story_with_analysis.invoke({"topic": "a rainy day"})
print("\nAnalysis:", story_analysis)
```
