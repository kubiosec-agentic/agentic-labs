"""
Vector search with LangChain + Chroma.

Pipeline: load a text file -> split into chunks -> embed each chunk ->
store in Chroma -> search. No LLM yet, this is retrieval only. RAG_03 adds
the generation step.
"""

from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

embeddings = OpenAIEmbeddings()   # reads OPENAI_API_KEY from the environment

# 1. Load and chunk
raw_documents = TextLoader("data/llms-full.txt").load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
print(f"Loaded {len(raw_documents)} document(s), split into {len(documents)} chunks")

# 2. Embed and store (one embedding API call per chunk)
db = Chroma.from_documents(documents, embeddings)

query = "What is MCP?"
K = 4


def show(title, hits):
    print("\n" + "=" * 80)
    print(f"{title}   (query: {query!r}, top {K})")
    print("=" * 80)
    for rank, (doc, score) in enumerate(hits, start=1):
        print(f"\n--- Rank {rank}  distance={score:.4f}  ({len(doc.page_content)} chars) ---")
        print(doc.page_content[:500].strip())


# 3a. Similarity search: text in, Chroma embeds the query for you.
#     Lower distance = closer match. The list is ranked, not one answer.
show("similarity_search_with_score", db.similarity_search_with_score(query, k=K))

# 3b. Same thing, but you embed the query yourself and pass the vector.
#     Useful when the embedding is computed elsewhere (cached, batched,
#     or produced by a different service). Same chunks, same order.
query_vector = embeddings.embed_query(query)
print(f"\nQuery embedded as a vector of {len(query_vector)} floats: {query_vector[:5]} ...")
show(
    "similarity_search_by_vector_with_relevance_scores",
    db.similarity_search_by_vector_with_relevance_scores(query_vector, k=K),
)
