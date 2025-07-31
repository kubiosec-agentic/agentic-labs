"""
This script analyzes GitHub repositories using LlamaIndex and OpenAI GPT models.

REQUIREMENTS:
- Install dependencies: pip install -r requirements_github_analysis.txt
- Set environment variables:
  * GITHUB_TOKEN: Your GitHub personal access token
  * OPENAI_API_KEY: Your OpenAI API key

USAGE:
- Modify the 'owner' and 'repo' variables to analyze different repositories
- The script will load repository documents, create a vector index, and use OpenAI to answer questions

FEATURES:
- Loads documents from GitHub repositories
- Creates semantic vector index for intelligent search
- Uses OpenAI GPT-3.5-turbo for natural language querying
- Asks multiple analytical questions about the repository
- Handles errors gracefully with fallback approaches
"""

import os
from llama_index.core import VectorStoreIndex, Settings
from llama_index.readers.github import GithubRepositoryReader, GithubClient


try:
    from llama_index.llms.openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    print("Error: Please set the GITHUB_TOKEN environment variable")
    print("You can get a GitHub token from: https://github.com/settings/tokens")
    exit(1)

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found. OpenAI inference will not be available.")
    print("To use OpenAI inference, set your API key: export OPENAI_API_KEY='your-key-here'")
    use_openai = False
else:
    use_openai = True
    print("OpenAI API key found - will use OpenAI for inference")


owner = "mcp-firewall"
repo = "mcp-firewall"
branch = "main"

print(f"Loading documents from {owner}/{repo}...")

github_client = GithubClient(github_token=github_token, verbose=True)

try:
    documents = GithubRepositoryReader(
        github_client=github_client,
        owner=owner,
        repo=repo,
        use_parser=False,
        verbose=True,
        filter_directories=(
            ["docs", "README", "readme", "documentation"],
            GithubRepositoryReader.FilterType.INCLUDE,
        ),
        filter_file_extensions=(
            [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json", ".ipynb"],
            GithubRepositoryReader.FilterType.EXCLUDE,
        ),
    ).load_data(branch=branch)
    print(f"Successfully loaded {len(documents)} documents")
except Exception as e:
    print(f"Error loading documents: {e}")
    print("Trying with simpler approach...")
    documents = GithubRepositoryReader(
        github_client=github_client,
        owner=owner,
        repo=repo,
        use_parser=False,
        verbose=True,
    ).load_data(branch=branch)
    print(f"Loaded {len(documents)} documents with fallback approach")

# Create vector index
print("Creating vector index...")
index = VectorStoreIndex.from_documents(documents)

# Configure OpenAI and run queries
if use_openai and openai_available:
    print("Setting up OpenAI LLM for inference...")
    llm = OpenAI(
        model="gpt-4o",
        api_key=openai_api_key,
        temperature=0.1
    )
    Settings.llm = llm
    
    query_engine = index.as_query_engine()
    
    questions = [
        "What is this repository about?",
        "What are the main features or components?",
        "How do you install and run this project?",
        "What technologies or frameworks does it use?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print('='*60)
        try:
            response = query_engine.query(question)
            print(response)
        except Exception as e:
            print(f"Error processing question: {e}")
            
else:
    print("OpenAI not available. Showing document content instead:")
    print(f"Total documents loaded: {len(documents)}")
    if documents:
        print("-" * 50)
        sample_text = documents[0].text[:500] + "..." if len(documents[0].text) > 500 else documents[0].text
        print(sample_text)
        print("-" * 50)

print("\nScript completed successfully!")
