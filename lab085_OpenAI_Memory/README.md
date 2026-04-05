![OpenAI](https://img.shields.io/badge/OpenAI-lightblue)
![Python](https://img.shields.io/badge/Python-blue)
![Agents](https://img.shields.io/badge/Agents-orange)

# LAB085: OpenAI Agents with Memory Persistence

## Introduction
This lab demonstrates how to implement conversation memory using OpenAI agents with SQLite session storage. You'll learn how to create agents that maintain conversation context across multiple interactions, use SQLite sessions to persist conversation history, manage different conversation sessions for different users, and handle asynchronous agent interactions.

## Set up your environment

### Setup Commands
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```
```bash
./lab_setup.sh
```
```bash
source .lab085/bin/activate
```

## Lab instructions

#### Example 1: Basic Memory Usage
Demonstrates basic conversation memory where the agent remembers previous context within a session using `OA_01.py`.

```bash
python OA_01.py
```

This example shows:
- Creating an agent with concise response instructions
- Using `SQLiteSession` for conversation persistence
- Multiple conversation turns where context is maintained
- Asynchronous agent execution

#### Example 2: Multiple Sessions
Shows how to manage separate conversation histories for different users using `OA_02.py`.

```bash
python OA_02.py
```

This example demonstrates:
- Using custom SQLite database files
- Maintaining separate conversation histories with different session IDs
- How different sessions don't share context

### Key Concepts
- **Agent**: The AI assistant with specific instructions
- **Runner**: Executes agent interactions asynchronously
- **SQLiteSession**: Provides persistent conversation memory
- **Session Management**: Separate conversations by user/session ID

## Cleanup environment
```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
