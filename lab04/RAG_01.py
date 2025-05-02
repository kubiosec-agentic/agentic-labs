# Import necessary classes and functions from llama_index
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.openai import OpenAIEmbedding  # For embeddings
from llama_index.llms.openai import OpenAI  # For response generation

# Import standard libraries
import openai
import os

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Path where the vector index is stored
PERSIST_DIR = "./storage"

# Toggle this to switch between retrieval-only and LLM synthesis modes
USE_LLM = True

# Define embedding model explicitly
embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

# Load or create the vector index
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)

# Create query engine based on whether LLM is used
if USE_LLM:
    llm = OpenAI(model="gpt-4o")  # You can use gpt-4 or gpt-3.5-turbo instead
    query_engine = index.as_query_engine(similarity_top_k=2, llm=llm)
else:
    retriever = VectorIndexRetriever(index=index, similarity_top_k=2)
    query_engine = RetrieverQueryEngine(retriever=retriever)

# Query the index
query = "what is MCP ?"
response = query_engine.query(query)

# --- Structured output ---
# 1. Retrieved documents (always available in .source_nodes)
print("\n📚 Retrieved Source Documents:\n")
for i, node in enumerate(response.source_nodes):
    print(f"--- Document {i+1} ---")
    print(f"Score: {node.score:.4f}")
    print("Content:\n", node.node.get_content())
    print("-------------------------\n")

# 2. Synthesized response (LLM mode only)
if USE_LLM:
    print("\n🧠 Synthesized Answer (LLM):\n")
    print(response)