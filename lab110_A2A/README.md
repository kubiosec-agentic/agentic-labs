# LAB110 - A2A (Agent-to-Agent Communication)
## Set up your environment
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```
```bash
./lab_setup.sh
```
```bash
source .lab110/bin/activate
```

## Lab instructions
### Agent-to-Agent Communication Framework

This lab demonstrates the A2A (Agent-to-Agent) communication framework, which enables direct communication and coordination between autonomous AI agents. You'll learn how to:

- Set up and run A2A agents that can communicate with each other
- Implement agent discovery mechanisms using well-known endpoints
- Use A2A Inspector for monitoring and debugging agent interactions
- Understand agent card specifications and service discovery

The A2A framework provides a standardized way for agents to discover, communicate, and collaborate with each other in distributed systems.

## Example Scenarios

### Step 1: Setup Hello World Agent (Terminal_1)
Start a basic A2A agent that can receive and respond to messages from other agents:

```bash
git clone https://github.com/a2aproject/a2a-samples.git
cd a2a-samples/samples/python/agents/helloworld
uv run .
```

This creates a simple agent that:
- Listens for incoming agent-to-agent communications
- Exposes an agent card for service discovery
- Provides basic hello world functionality

### Step 2: Setup Hello World Client (Terminal_2)
Test the agent communication by running a client that connects to the agent:

```bash
cd a2a-samples/samples/python/agents/helloworld
```
```bash
uv run test_client.py
```

This demonstrates:
- How agents can discover and connect to other agents
- Basic message exchange patterns
- Agent response handling

### Step 3: Agent Discovery (Terminal_2)
Explore the agent's self-description and capabilities using the standard discovery endpoint:

```bash
curl http://127.0.0.1:9999/.well-known/agent-card.json | jq -r .
```

This shows:
- Agent metadata and capabilities
- Available services and endpoints
- Communication protocols supported

### Step 4: Setup A2A Inspector (Terminal_2)
Install and run the A2A Inspector for advanced monitoring and debugging:

```bash
cd ..
```
```bash
git clone https://github.com/a2aproject/a2a-inspector.git
cd a2a-inspector/
uv sync
cd frontend
npm install
cd ..
chmod +x scripts/run.sh
bash scripts/run.sh
```

The A2A Inspector provides:
- Real-time monitoring of agent interactions
- Message flow visualization
- Debugging tools for agent communication
- Performance metrics and analytics

### Key Concepts
- **Agent Cards**: Standardized agent self-description format
- **Service Discovery**: How agents find and connect to each other
- **Message Protocols**: Structured communication between agents
- **Well-known Endpoints**: Standard URLs for agent discovery
- **Inspector Tools**: Debugging and monitoring capabilities

### Features Demonstrated
- Basic agent setup and communication
- Service discovery mechanisms
- Client-server agent interactions
- Agent monitoring and inspection
- Standard protocol compliance

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
