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
### OAuth 2.0 M2M API Server with OpenAI Integration
Instructions see [OAuth 2.0 M2M API Server with OpenAI Integration](https://github.com/kubiosec-ai/openai-oauth-demo/)<br>

The `client.py` example demonstrates a Machine-to-Machine (M2M) authenticates with Amazon Cognito using the **OAuth 2.0 client credentials flow**, and interact with a protected FastAPI server. 

The FastAPI application `server.py` implements a secure Machine-to-Machine (M2M) service, implementing both authentication and authorization using OAuth 2.0 with Amazon Cognito. It protects endpoints by verifying incoming JWT access tokens against **Cognito’s public keys (JWKS)**, ensuring that only authorized services can access the API. The app also integrates OpenAI’s API to generate AI-powered responses for authenticated requests. 


### OAuth 2.0 Web Applicaiton with OpenAI Integration
This project is a fully functional OAuth 2.0 web application demo that illustrates how to implement secure user authentication using Amazon Cognito as the identity provider. Built with Flask and Authlib, it showcases how to perform login, retrieve and inspect tokens, handle user session management, and access OpenID Connect (OIDC) claims. Designed for educational purposes, it also includes a token debug interface and an admin-only route that integrates with the OpenAI API for dynamic content generation. This demo is ideal for developers looking to understand OAuth/OIDC Authorization Code Flow in a Python-based web environment.
Instructions can be found here [OAuth Web Application Demo](https://github.com/kubiosec-codecamp/oauth-web-app.git)

### Logging and Tracing
#### Traceloop
Checkout [traceloop](https://www.traceloop.com/)
```
export TRACELOOP_API_KEY=tl_xxxxxxxxxxxxx
```
```
python traceloop_01.py
```

### Rag Metadata example
xxx

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
