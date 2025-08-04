import os
import glob
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load shell scripts from local directory
def load_shell_scripts(directory_path):
    """Load all .sh files from the specified directory and subdirectories"""
    documents = []
    
    # Use glob to find all .sh files recursively
    pattern = os.path.join(directory_path, "**/*.sh")
    shell_files = glob.glob(pattern, recursive=True)
    
    print(f"📁 Found {len(shell_files)} shell script(s) in {directory_path}")
    
    for file_path in shell_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Create a document-like structure similar to GitLoader
                doc = {
                    'content': content,
                    'source': os.path.relpath(file_path, directory_path)
                }
                documents.append(doc)
                print(f"  ✅ Loaded: {doc['source']}")
        except Exception as e:
            print(f"  ❌ Error loading {file_path}: {e}")
    
    return documents

# Load repository context from local directory
documents = load_shell_scripts("./test_repo")

if not documents:
    print("⚠️  No shell scripts found in ./test_repo directory!")
    print("Make sure the directory exists and contains .sh files.")
    exit(1)

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
    repo_context += f"\n--- File: {doc['source']} ---\n"
    repo_context += doc['content']
    repo_context += "\n" + "="*50 + "\n"

# Run the security review
print("\n🔍 Starting security review of shell scripts...")
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
