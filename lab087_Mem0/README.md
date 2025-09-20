# LAB087 - Mem0 (Memory for AI Agents)
## Set up your environment
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```
```bash
./lab_setup.sh
```
```bash
source .lab087/bin/activate
```

## Lab instructions
### Mem0: Intelligent Memory Layer for AI Agents

This lab demonstrates how to use Mem0, an intelligent memory layer that enables AI agents to remember, learn, and improve over time. You'll explore both self-hosted and managed SaaS configurations.

### Self-hosted Setup with Qdrant Vector Store

For self-hosted memory storage, run Qdrant locally:

```bash
docker run -d --name qdrant \
   -p 6333:6333 -p 6334:6334 \
   -v $PWD/qdrant_storage:/qdrant/storage \
   qdrant/qdrant:latest
```

### Managed SaaS Setup

For the managed Mem0 service, set your API key:
```bash
export MEM0_API_KEY="your_mem0_api_key_here"
```

## Example Scripts

### Self-hosted Examples (with Qdrant)

#### Example 1: Basic Memory Operations (`mem_01.py`)
Demonstrates adding conversation memories to Qdrant:
```bash
python mem_01.py
```

#### Example 2: Retrieving Memories (`mem_02.py`)
Shows how to retrieve stored memories for a user:
```bash
python mem_02.py
```

#### Examples 3-5: Agent Integration (`mem_03.py`, `mem_04.py`, `mem_05.py`)
Demonstrates integrating Mem0 with OpenAI agents:
```bash
python mem_03.py
python mem_04.py
python mem_05.py
```

#### Example 6: Collaborative Memory (`mem_06.py`)
Shows collaborative memory sharing across multiple agents:
```bash
python mem_06.py
```

### Managed SaaS Examples (`mem0_managed/`)

#### Example 1: Basic SaaS Usage (`mem_01_saas.py`)
Basic memory operations using Mem0's managed service:
```bash
python mem0_managed/mem_01_saas.py
```

#### Example 2: Advanced SaaS Features (`mem_02_saas.py`)
Advanced features with the managed service:
```bash
python mem0_managed/mem_02_saas.py
```

#### Example 3: Search Functionality (`mem_03_search_functionality.py`)
Memory search capabilities:
```bash
python mem0_managed/mem_03_search_functionality.py
```

#### Example 4: Filtering with v2 (`mem_04_v2_filters.py`)
Advanced filtering features in Mem0 v2:
```bash
python mem0_managed/mem_04_v2_filters.py
```

### Key Concepts
- **Memory Storage**: Persistent memory using vector databases (Qdrant) or managed service
- **User Scoping**: Separate memories per user/session
- **Agent Integration**: Seamless integration with OpenAI agents
- **Search & Retrieval**: Semantic search through stored memories
- **Collaborative Memory**: Shared memory across multiple agents
- **SaaS vs Self-hosted**: Choose between managed service or local deployment

### Features Demonstrated
- Basic memory add/retrieve operations
- User-scoped memory management
- Agent tools for memory operations
- Collaborative memory sharing
- Semantic memory search
- Vector store configuration (Qdrant)
- Managed SaaS integration

## Cleanup environment
```bash
docker stop qdrant
```
```bash
deactivate
```
```bash
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
