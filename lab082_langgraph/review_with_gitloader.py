from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import GitLoader

# Load repository context
repo_loader = GitLoader(
    repo_path="./test_repo",
    clone_url="https://github.com/xxradar/TLSSAN_scanner.git", 
    branch="master", 
    file_filter=lambda file_path: file_path.endswith(".sh")
)
documents = repo_loader.load()

# Create context-aware prompt for security review
system_template = """You are an expert cybersecurity analyst specializing in shell script security reviews. 
Analyze the following shell scripts for potential security vulnerabilities, best practices violations, and improvements.

Focus on:
- Command injection vulnerabilities
- Improper input validation
- Insecure file permissions
- Hardcoded credentials or sensitive data
- Path traversal issues
- Use of unsafe functions
- Missing error handling

Repository files:
{repo_context}"""

human_template = """Please perform a comprehensive security review of these shell scripts and provide:
1. A summary of security issues found
2. Severity levels (High/Medium/Low) for each issue
3. Specific recommendations for remediation"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template), 
    ("human", human_template)
])

# Create model with extended context window
model = ChatOpenAI(model="gpt-4o", temperature=0.2)

# Create the chain
chain = prompt | model

# Prepare repository context
repo_context = ""
for doc in documents:
    repo_context += f"\n--- File: {doc.metadata.get('source', 'unknown')} ---\n"
    repo_context += doc.page_content
    repo_context += "\n" + "="*50 + "\n"

# Run the security review
print("🔍 Starting security review of shell scripts...")
print("="*60)

try:
    result = chain.invoke({
        "repo_context": repo_context
    })
    
    print("📋 SECURITY REVIEW RESULTS:")
    print("="*60)
    print(result.content)
    
except Exception as e:
    print(f"❌ Error during security review: {e}")
    
print("\n" + "="*60)
print("✅ Security review completed!")

