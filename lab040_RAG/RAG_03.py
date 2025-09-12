import os
import openai
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load and split document
raw_documents = TextLoader('data/llms-full.txt').load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
documents = text_splitter.split_documents(raw_documents)

# Print index info
print("===================================================================================")
print(f"Total chunks created: {len(documents)}")
for i, doc in enumerate(documents):
    print(f"Chunk {i}: {len(doc.page_content)} characters")
print("===================================================================================\n")

# Create vector store
db = Chroma.from_documents(documents, OpenAIEmbeddings())

# Query
query = "What is MCP?"
docs = db.similarity_search(query)

# Print found matches
print("===================================================================================")
print("TOP MATCHING DOCUMENT CHUNKS:")
for i, doc in enumerate(docs[:3]):
    snippet = doc.page_content.strip().replace("\n", " ")[:200]
    print(f"[Match {i}] {snippet}...")
print("===================================================================================\n")

# Prepare context
retrieved_text = "\n\n".join(doc.page_content for doc in docs[:3])

# LLM and prompt
llm = ChatOpenAI(temperature=0)
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert assistant. Use the following context to answer the question below concisely.

Context:
{context}

Question:
{question}

Answer:"""
)

# Run the prompt
chain = prompt | llm
response = chain.invoke({"context": retrieved_text, "question": query})

# Final result
print("===================================================================================")
print("SYNTHESIZED ANSWER FROM LLM:")
print("===================================================================================")
print(response.content)
