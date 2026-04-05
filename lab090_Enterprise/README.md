![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Python](https://img.shields.io/badge/Python-blue) ![Security](https://img.shields.io/badge/Security-red) ![RAG](https://img.shields.io/badge/RAG-pink) ![Docker](https://img.shields.io/badge/Docker-blue)

# LAB090: Enterprise-Ready Agent Systems

## Introduction

This lab explores key concepts in Authentication, Authorization, and Observability for AI-integrated systems:
- OAuth flows for machine-to-machine (M2M) and web app auth using real code examples.
- Logging and tracing (coming soon) for monitoring agent behavior and API interactions
- RAG with metadata (coming soon) to enhance retrieval and reasoning with structured context

Ideal for securing and debugging AI-powered applications in production environments.

## Set up your environment

### Setup Commands

```bash
export OPENAI_API_KEY="xxxxxxxxx"
```

```bash
./lab_setup.sh
```

```bash
source .lab090/bin/activate
```
## Lab instructions
### OAuth 2.0
#### OAuth 2.0 M2M API Server with OpenAI Integration
Instructions see [OAuth 2.0 M2M API Server with OpenAI Integration](https://github.com/kubiosec-ai/openai-oauth-demo/)<br>

The `client.py` example demonstrates a Machine-to-Machine (M2M) authenticates with Amazon Cognito using the **OAuth 2.0 client credentials flow**, and interact with a protected FastAPI server. 

The FastAPI application `server.py` implements a secure Machine-to-Machine (M2M) service, implementing both authentication and authorization using OAuth 2.0 with Amazon Cognito. It protects endpoints by verifying incoming JWT access tokens against **Cognito’s public keys (JWKS)**, ensuring that only authorized services can access the API. The app also integrates OpenAI’s API to generate AI-powered responses for authenticated requests. 


#### OAuth 2.0 Web Application with OpenAI Integration
This project is a fully functional OAuth 2.0 web application demo that illustrates how to implement secure user authentication using Amazon Cognito as the identity provider. Built with Flask and Authlib, it showcases how to perform login, retrieve and inspect tokens, handle user session management, and access OpenID Connect (OIDC) claims. Designed for educational purposes, it also includes a token debug interface and an admin-only route that integrates with the OpenAI API for dynamic content generation. This demo is ideal for developers looking to understand OAuth/OIDC Authorization Code Flow in a Python-based web environment.
Instructions can be found here [OAuth Web Application Demo](https://github.com/kubiosec-codecamp/oauth-web-app.git)

### Logging and Tracing
#### Traceloop

This script demonstrates how to use OpenAI's GPT-4o model to generate a joke, while integrating Traceloop for observability and tracing. The create_joke function is decorated as a workflow, enabling detailed monitoring of the AI-powered joke generation process using OpenTelemetry standards. Checkout [traceloop](https://www.traceloop.com/)

```bash
export TRACELOOP_API_KEY=tl_xxxxxxxxxxxxx
```

```bash
python traceloop_01.py
```

#### OpenAI Tracing

This script is using the OpenAI Agent framework to build a triage agent that routes user questions to specialized tutors, while enforcing input safety using a custom guardrail. The guardrail checks whether a question is related to homework, and if not, the input is blocked. Accepted inputs are routed to either a math or history tutor agent for detailed responses. The entire process is traced and logged using OpenAI for observability.

```bash
python openai_trace_01.py
```

### RAG with Metadata
#### Chroma and Metadata

This script demonstrates how to use the Chroma database to store and retrieve documents with metadata-based access control. It simulates a real-world use case where documents are tagged as either public or confidential, and users can query the database with or without access filters.

```bash
python rag_metadata_01.py
```

#### Chroma, Metadata and OpenAI Embedding

This script demonstrates how to store and search documents in Chroma using automatic embedding via OpenAI's text-embedding-3-small model. Instead of manually generating embeddings, we configure Chroma with an OpenAIEmbeddingFunction, which automatically computes and stores embeddings when documents are added.

```bash
export CHROMA_OPENAI_API_KEY=$OPENAI_API_KEY
```

```bash
python rag_metadata_02.py
```

#### Semantic Search and Retrieval-Augmented Generation

This code demonstrates a Retrieval-Augmented Generation (RAG) pipeline that combines OpenAI's embedding capabilities with Chroma's vector storage to perform semantic search over documents. It then leverages GPT-4 to generate responses based on the retrieved information.

```bash
python rag_metadata_03.py
```

#### Setup with Persistent Storage

```bash
python rag_metadata_04.py
```
## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
