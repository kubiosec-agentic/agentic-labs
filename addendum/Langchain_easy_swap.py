import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Set up your API keys as environment variables:
# export OPENAI_API_KEY="your-openai-key"
# export GOOGLE_API_KEY="your-google-key"

# Use a config switch or env variable to choose LLM
use_gemini = True  # Set to True to use Gemini, False for OpenAI

# Initialize the appropriate LLM
if use_gemini:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    print("Using Google Gemini")
else:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("Using OpenAI GPT")

# Define a simple prompt template
prompt_template = PromptTemplate(
    input_variables=["topic"],
    template="Write me a terraform plan for {topic}."
)

# Create the chain using modern RunnableSequence (prompt | llm)
chain = prompt_template | llm

# Example usage
if __name__ == "__main__":
    try:
        # Run the chain with a sample input using invoke method
        result = chain.invoke({"topic": "S3 bucket with versioning enabled in us-west-2 and public access blocked"})
        print("\nGenerated:")
        print(result.content)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your API keys as environment variables!")
