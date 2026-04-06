![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![ChatCompletion](https://img.shields.io/badge/ChatCompletion-green) ![Curl](https://img.shields.io/badge/Curl-orange)

# LAB010: Chat Completions

## Introduction
LAB010 introduces the foundational steps for interacting with the OpenAI Chat Completions API using nothing but `curl` and `jq` — tools available on virtually any Linux system. This is deliberate: knowing how to call an LLM from the command line is one of the fastest ways to add AI capabilities to existing scripts, automation pipelines, or pentest tooling. A quick `curl` call can classify log entries, summarize recon output, generate phishing templates for red-team exercises, or extract structured data from unstructured text — all without writing a single line of Python.

You'll learn how to structure API requests, control the model with system prompts, parse JSON responses, handle multi-turn conversations, analyze images, and stream output token by token. Along the way you'll also pick up practical `curl`, `jq`, and `grep` skills that transfer well beyond AI work. The [ADDON](./ADDON.md) then takes these basics into prompting techniques, output format pitfalls, and your first look at prompt injection.

## Set up your environment

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
./lab_setup.sh
```

## Lab instructions
### OpenAI Chat Completion
https://platform.openai.com/docs/api-reference/chat

#### Simple textbook example
This is the most basic call to the Chat Completions API using `curl`. Notice the structure: you send a POST request with a JSON body containing the model name and a list of messages. The response comes back as a JSON object.
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is AI"
          }
        ]
      }
    ]
  }'
```
Take a moment to look at the raw JSON response. It contains the model's answer, but also metadata like the model version, token usage, and a `finish_reason`. We'll use `jq` shortly to make sense of this.

#### Adding a System prompt
The `system` role lets you set the behavior and personality of the assistant *before* the user speaks. Think of it as the instructions you'd give a human assistant before they start a task. This is a critical concept: how you write the system prompt directly affects the quality, safety, and predictability of the model's output.
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are a helpful assistant"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is AI"
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 2048,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }'
```
This example also introduces several parameters: `temperature` controls randomness (0 = deterministic, higher = more creative), `max_tokens` limits the response length, and `top_p` is an alternative way to control randomness (nucleus sampling). `frequency_penalty` and `presence_penalty` discourage repetition.

#### `jq` to the rescue
The raw API response is a large JSON object. `jq` is a command-line JSON processor that lets you extract exactly the field you need. Here we pull out just the assistant's reply text by navigating to `.choices[0].message.content`.
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are a helpful assistant"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is AI"
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 2048,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }' | jq '.choices[0].message.content'
```

Now try extracting the token usage instead. This tells you how many tokens the prompt and response consumed — important for understanding cost and rate limits:
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": "What is AI"
      }
    ],
    "max_tokens": 200
  }' | jq '.usage'
```
The response shows `prompt_tokens`, `completion_tokens`, and `total_tokens`. Every API call has a cost based on these numbers.

#### Continuing the conversation
The Chat Completions API is *stateless* — it has no memory of previous requests. To continue a conversation, you must include the full message history in every request. Notice how the `messages` array now contains the original system prompt, the first user question, the assistant's previous reply, and a new follow-up question.
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are a helpful assistant"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is AI"
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": "**AI** stands for **Artificial Intelligence**.\n\nIn simple terms, **AI** refers to the ability of a computer or a machine to perform tasks that would normally require human intelligence. These tasks include:\n\n- Understanding language (spoken or written)\n- Recognizing images or patterns\n- Learning from experience/data (machine learning)\n- Making decisions or solving problems\n- Playing games, driving cars, translating languages, and more\n\n**Types of AI:**\n1. **Narrow AI (Weak AI):** \n   - Specialized in one task (e.g., voice assistants, recommendation systems).\n2. **General AI (Strong AI):**\n   - Can understand and perform any intellectual task that a human can (still theoretical).\n3. **Superintelligent AI:**\n   - Intelligence far surpassing human capabilities (purely hypothetical at this stage).\n\n**Examples of AI in everyday life:**\n- Siri, Google Assistant, and Alexa\n- Recommendation on Netflix or YouTube\n- Face recognition in photos\n- Self-driving cars\n\n**In summary:**  \n**Artificial Intelligence is the science and technology of making machines smart, so they can mimic, help, or even surpass human thinking and actions.**"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Create me 2 line summary"
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 2048,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }' | jq '.choices[0].message.content'
```
This "manual context window" is how every chatbot works under the hood. It also means that longer conversations cost more tokens — a tradeoff you'll encounter throughout the training.

#### Attaching request.json
As requests get larger, embedding the JSON in the command line becomes impractical. You can place the payload in a file and reference it with `@`. This is the same as typing the JSON inline, but much cleaner.
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d @request.json
```
Open `request.json` in your editor and experiment with changing the prompt, the model, or the temperature.

#### Things to think about
See [./ADDON.md](./ADDON.md) for prompting techniques, output format gotchas, and a first look at prompt injection.

#### Image analysis
The Chat Completions API also handles multimodal input. Here we send an image URL alongside a text instruction, asking the model to extract a license plate number.
```bash
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "https://hpr.com/wp-content/uploads/2023/08/LP_USA_California_passenger-600x348.jpg"
            }
          },
          {
            "type": "text",
            "text": "Extract the license plate. Only answer with the license plate number as a string."
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 100
  }' | jq -r .
```
Now try this one ;-)
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "https://www.radarhack.com/demo/vuln.jpg"
            }
          },
          {
            "type": "text",
            "text": "Extract the license plate. Only answer with the license plate number as a string."
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 100
  }' | jq -r .
```
Now, try fixing it using natural language and the chat completion.

#### Streaming
So far, every request waits until the model finishes generating the entire response before returning anything. With `"stream": true`, the API sends back tokens as they are generated — one chunk at a time using Server-Sent Events (SSE). This is how ChatGPT shows text appearing word by word.
```bash
curl -XPOST "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Write a poem about the stars."}],
    "stream": true
  }'
```
Look at the raw output — each line starts with `data:` and contains a small JSON chunk with one token in `choices[0].delta.content`. The stream ends with `data: [DONE]`.

Adding some `grep` magic to extract just the text content:
```bash
curl -s -XPOST "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Write a poem about the stars."}],
    "stream": true
  }' 2>/dev/null | sed -n 's/^data: //p' | grep -v '^\[DONE\]' | jq -rj '.choices[0].delta.content // empty'
```
This pipes the SSE stream through `sed` to strip the `data:` prefix, filters out the `[DONE]` marker, and uses `jq` to extract the content delta from each chunk. The `-j` flag tells jq not to add newlines, so the text flows naturally.

## Cleanup environment
```bash
deactivate
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
