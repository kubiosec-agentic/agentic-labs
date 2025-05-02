import os
import openai
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
raw_documents = TextLoader('data/llms-full.txt').load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
db = Chroma.from_documents(documents, OpenAIEmbeddings())


query = "What is MCP?"

# Perform a similarity search using the query
print("========================================================================================================")
print("Similarity Search Results:")
print("========================================================================================================")
docs = db.similarity_search(query)
print(docs[0].page_content)

# Perform a similarity search using the embedding vector
print("========================================================================================================")
print("Vector Search Results:")
print("========================================================================================================")
embedding_vector = OpenAIEmbeddings().embed_query(query)
docs = db.similarity_search_by_vector(embedding_vector)
print(docs[0].page_content)