![LangChain](https://img.shields.io/badge/LangChain-lightgrey) ![Python](https://img.shields.io/badge/Python-blue) ![ChatCompletion](https://img.shields.io/badge/ChatCompletion-green)

# LAB035: LangChain Quickstart

## Introduction

In the previous labs you talked to OpenAI through raw HTTP (curl, requests) and the official SDK. That works, but what if you want to swap providers, chain multiple calls together, or add conversation memory without rewriting everything?

LangChain is a framework that solves exactly that. It wraps every major LLM behind a common interface and lets you compose prompts, models, parsers, and memory into modular pipelines called **chains**. One import change and your code talks to Anthropic, Google, or a local model instead of OpenAI.

This lab walks you through LangChain's core building blocks, one script at a time. By the end you will have built a multi-turn chatbot with memory and even run a model locally on your own machine. LangGraph (stateful agent graphs) is covered separately in lab064.

> **Note:** LangChain's API moves fast. The examples here use the current stable packages (langchain-core 0.3+, langchain-openai 0.3+). If something breaks after a major release, check the [LangChain migration guide](https://python.langchain.com/docs/versions/v0_3/).

## Set up your environment

```bash
# Make sure your .env or shell exports are set
export OPENAI_API_KEY="your-key-here"

# Optional: only needed if you uncomment alternative providers in the scripts
# export ANTHROPIC_API_KEY="your-key-here"
# export GOOGLE_API_KEY="your-key-here"

./lab_setup.sh
source .lab035/bin/activate
```

## Lab instructions

### Step 1: Basic chat with multiple providers (`lc01_chat.py`)

The simplest possible LangChain program: create a chat model and call `.invoke()`. The script has several providers commented out (Anthropic, Google, Ollama). Try uncommenting them one at a time to see how LangChain's uniform interface lets you switch with a single line change.

```bash
python3 ./lc01_chat.py
```

Look at the output object. By default the script prints the full `AIMessage`, which includes `response_metadata` (token counts, model info). Uncomment `response.content` to get just the text, or `response.response_metadata` to inspect the raw provider response.

For details, see [doc/chat.md](./doc/chat.md).

### Step 2: Prompt templates and chaining (`lc02_prompt.py`)

LangChain's real power starts with the pipe (`|`) operator. This script builds two chains: one that generates a story, and one that analyzes mood. Then it pipes the output of the first into the second, creating a combined chain.

```bash
python3 ./lc02_prompt.py
```

Notice how `PromptTemplate`, the model, and `StrOutputParser` are composed together. This is LangChain Expression Language (LCEL): every component is a "Runnable" that you can plug together like Unix pipes.

For details, see [doc/prompt.md](./doc/prompt.md).

### Step 3: Structured prompts with roles (`lc03_advanced_prompting.py`)

Moving from a single string template to a proper chat prompt with `system` and `user` roles. This is where you control the model's persona.

```bash
python3 ./lc03_advanced_prompting.py
```

The script uses `ChatPromptTemplate.from_messages()` with separate system and user templates. Compare this with how you set roles in the raw Chat Completions API (lab010): same concept, different abstraction level.

For details, see [doc/advanced_prompting.md](./doc/advanced_prompting.md).

### Step 4: Multi-turn conversations with memory (`lc04_multi_turn.py`)

A stateless chain forgets everything between calls. This script adds `RunnableWithMessageHistory` to maintain conversation context across turns, so the model can answer follow-up questions correctly.

```bash
python3 ./lc04_multi_turn.py
```

The script asks three questions about the 2018 World Cup. The second and third questions ("Where was it held?", "Who was the top scorer?") only make sense if the model remembers the topic. Watch the message history printout at the end to see how LangChain tracks the full conversation.

For details, see [doc/multi-turn.md](./doc/multi-turn.md).

### Step 5: Local model with HuggingFace (`lc05_hf_local.py`)

Everything so far used cloud APIs. This script runs a small model (Qwen2-0.5B) entirely on your machine, no API key needed. Useful when you want to experiment offline, work with sensitive data, or just understand what happens under the hood.

```bash
# Optional: set a HuggingFace token for gated models
export HF_TOKEN="your-token-here"

python3 ./lc05_hf_local.py
```

The first run downloads the model (~1 GB). Subsequent runs use the cached version. Output quality is lower than GPT-4o (it is a 0.5B parameter model), but the point is to see LangChain's provider abstraction at work: same `ChatHuggingFace` interface, same `.invoke()` call.

> **Note:** The requirements pin `transformers<5` because version 5.x can produce degraded output with small models like Qwen2-0.5B.

For details, see [doc/huggingface.md](./doc/huggingface.md).

### Step 6: Swapping providers with a config switch (`lc06_easy_swap.py`)

This script makes the provider abstraction concrete. A single boolean (`use_gemini = True/False`) switches the entire pipeline between OpenAI and Google Gemini. The prompt, chain, and output code stay identical.

```bash
# Requires GOOGLE_API_KEY for the Gemini path
export GOOGLE_API_KEY="your-key-here"

python3 ./lc06_easy_swap.py
```

Try flipping `use_gemini` to `False` and running again with the same prompt. Compare the Terraform output from both providers. This is exactly the kind of flexibility LangChain gives you: write once, swap providers without touching your business logic.

## Cleanup environment

```bash
# Remove cached HuggingFace models (optional, frees ~1 GB)
rm -rf ~/.cache/huggingface

deactivate
./lab_cleanup.sh
```

## Going further

The [lab990_addendum/langchain](../lab990_addendum/langchain/) folder contains more advanced LangChain examples that build on what you learned here: a weather tool with real API integration, shell script security analysis (both local and via GitLoader), a Pydantic-based code security reviewer, a CLI tool executor, and a Gradio writing assistant.

## What's next

- **lab040**: RAG (Retrieval-Augmented Generation), combining LLMs with your own data
- **lab054**: LangChain Tools, giving the model the ability to call functions
- **lab064**: LangGraph, building stateful agent graphs with branching logic

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
