
![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![ChatCompletion](https://img.shields.io/badge/ChatCompetion-green)
# LAB035: LangChain and LangGraph Quickstart
This lab demonstrates how to build powerful language model workflows using LangChain and LangGraph.<br>

**LangChain** is a flexible framework for composing prompts, models, tools, and logic into modular pipelines called chains.<br>

**LangGraph** builds on top of LangChain by allowing you to define stateful, multi-step graphs with branching logic ideal for building agents and complex decision-making systems.

With just a few lines of code, you can:
- **Create structured chains:** connect prompts, language models, and output parsers
- **Build intelligent agents:** LLM-powered systems that can make decisions and call tools
- Use **LangGraph** to model flows as stateful graphs with memory and control

This lab includes minimal examples to help you get started with each concept.

## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
export ANTHROPIC_API_KEY="xxxxxxxxx"
export GOOGLE_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab035/bin/activate
```
## Lab instructions
For detailed guidance and examples, check out the following documentation files:

- [Chat Systems](./doc/chat.md) - Building conversational AI systems
- [Prompt Engineering](./doc/prompt.md) - Best practices for prompt design and optimization
- [Advanced Prompting](./doc/advanced_prompting.md) - Advanced techniques for crafting effective prompts
- [Multi-Turn Conversations](./doc/multi-turn.md) - Handling complex multi-turn dialogues
- [HuggingFace local model example](./doc/huggingface.md) - Handling complex multi-turn dialogues

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
