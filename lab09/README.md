# LAB09: Enterprise ready Agents
## Introduction
This lab explores key concepts in Authentication, Authorization, and Observability for AI-integrated systems:
- OAuth flows for machine-to-machine (M2M) and web app auth using real code examples.
- Logging and tracing (coming soon) for monitoring agent behavior and API interactions
- RAG with metadata (coming soon) to enhance retrieval and reasoning with structured context

Ideal for securing and debugging AI-powered applications in production environments.
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab09/bin/activate
```
## Lab instructions
### OAuth 2.0
#### OAuth 2.0 M2M API Server with OpenAI Integration
Instructions see [OAuth 2.0 M2M API Server with OpenAI Integration](https://github.com/kubiosec-ai/openai-oauth-demo/)<br>

The `client.py` example demonstrates a Machine-to-Machine (M2M) authenticates with Amazon Cognito using the **OAuth 2.0 client credentials flow**, and interact with a protected FastAPI server. 

The FastAPI application `server.py` implements a secure Machine-to-Machine (M2M) service, implementing both authentication and authorization using OAuth 2.0 with Amazon Cognito. It protects endpoints by verifying incoming JWT access tokens against **Cognito’s public keys (JWKS)**, ensuring that only authorized services can access the API. The app also integrates OpenAI’s API to generate AI-powered responses for authenticated requests. 


#### OAuth 2.0 Web Applicaiton with OpenAI Integration
This project is a fully functional OAuth 2.0 web application demo that illustrates how to implement secure user authentication using Amazon Cognito as the identity provider. Built with Flask and Authlib, it showcases how to perform login, retrieve and inspect tokens, handle user session management, and access OpenID Connect (OIDC) claims. Designed for educational purposes, it also includes a token debug interface and an admin-only route that integrates with the OpenAI API for dynamic content generation. This demo is ideal for developers looking to understand OAuth/OIDC Authorization Code Flow in a Python-based web environment.
Instructions can be found here [OAuth Web Application Demo](https://github.com/kubiosec-codecamp/oauth-web-app.git)

### Logging and Tracing
#### Traceloop
This script demonstrates how to use OpenAI's GPT-4o model to generate a joke, while integrating Traceloop for observability and tracing. The create_joke function is decorated as a workflow, enabling detailed monitoring of the AI-powered joke generation process using OpenTelemetry standards. Checkout [traceloop](https://www.traceloop.com/)
```
export TRACELOOP_API_KEY=tl_xxxxxxxxxxxxx
```
```
python traceloop_01.py
```
#### Langtrace
This script demonstrates how to use the Langtrace SDK and the Agents framework to build a triage agent that routes user questions to specialized tutors, while enforcing input safety using a custom guardrail. The guardrail checks whether a question is related to homework, and if not, the input is blocked. Accepted inputs are routed to either a math or history tutor agent for detailed responses. The entire process is traced and logged using Langtrace for observability.
```
export LANGTRACE_API_KEY=xxxxxxxxxxxx
```
```
python langtrace_01.py
```


### Rag Metadata example
#### ChromaDB and metadata
This script demonstrates how to use ChromaDB to store and retrieve documents with metadata-based access control. It simulates a real-world use case where documents are tagged as either public or confidential, and users can query the database with or without access filters.
Key features of the script:
- Adds 40 unique documents (20 public, 20 confidential) with realistic chatbot-related content.
- Assigns metadata to each document ("access": "public" or "confidential").
- Supports filtered search using metadata to simulate access control (e.g., showing only public info to general users).
- Uses semantic search to return the most relevant documents to a given query.
- Outputs search results in a clean, structured format with document content, metadata, and similarity scores.

This serves as a foundation for building secure retrieval-augmented generation (RAG) systems or chatbot backends where information exposure needs to be restricted based on user roles.
Check out [ChromaDB Filters](https://cookbook.chromadb.dev/core/filters/#) for more advanced filtering.
```
python rag_metadat_01.py
```
#### Alternative approach
```
export CHROMA_OPENAI_API_KEY=$OPENAI_API_KEY
```
```
python rag_metadat_02.py
```
#### Semantic Search and Retrieval-Augmented Generation (RAG)
This code demonstrates a Retrieval-Augmented Generation (RAG) pipeline that combines OpenAI's embedding capabilities with ChromaDB's vector storage to perform semantic search over documents. It then leverages GPT-4 to generate responses based on the retrieved information.
To enable semantic search, the code first converts each document into a high-dimensional vector representation using OpenAI's text-embedding-3-small model. This process captures the semantic meaning of the text, allowing for effective similarity comparisons.
ChromaDB serves as a vector database that stores the document embeddings along with their metadata. This setup allows for efficient retrieval of documents based on semantic similarity and metadata filters.
When querying, you can apply metadata filters to restrict the search to specific subsets of documents.
then used to prompt GPT-4 for generating a response. This method grounds the AI's output in the retrieved information, enhancing accuracy and relevance.
```
python rag_metadat_03.py
```
## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
