# LAB085 - OpenAI Memory
## Set up your environment
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
### OpenAI Agents with Memory Persistence

This lab demonstrates how to implement conversation memory using OpenAI agents with SQLite session storage. You'll learn how to:

- Create agents that maintain conversation context across multiple interactions
- Use SQLite sessions to persist conversation history
- Manage different conversation sessions for different users
- Handle asynchronous agent interactions

### Example 1: Basic Memory Usage (`OA_01.py`)
Demonstrates basic conversation memory where the agent remembers previous context within a session:

```bash
python OA_01.py
```

This example shows:
- Creating an agent with concise response instructions
- Using `SQLiteSession` for conversation persistence
- Multiple conversation turns where context is maintained
- Asynchronous agent execution

### Example 2: Multiple Sessions (`OA_02.py`)
Shows how to manage separate conversation histories for different users:

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
