![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Responses_API](https://img.shields.io/badge/Responses_API-brightgreen) ![Curl](https://img.shields.io/badge/Curl-orange) ![Tools](https://img.shields.io/badge/Tools-purple)

# LAB020: OpenAI Responses API

## Introduction
In lab010 you used the Chat Completions API, which is stateless: you send a list of messages, get a response, and manage conversation history yourself. The **Responses API** (`/v1/responses`) is OpenAI's newer endpoint, designed for agentic workflows. The key differences are:

- **`input`** replaces `messages`, and the response lives in an **`output`** array with typed items (not `choices`)
- **Built-in tools** like `web_search_preview` and `file_search` are first-class citizens, no manual implementation needed
- **Response IDs** let you recall any past response by ID, useful for async workflows and debugging
- **`previous_response_id`** handles multi-turn conversations server-side, so you don't have to resend the full message history on every call
- **Structured output** via `text.format` with full JSON Schema enforcement (more powerful than Chat Completions' `response_format`)

This lab walks you through each of these capabilities using `curl` and `jq`, building on the skills from lab010.

## Set up your environment

### Setup Commands
```bash
export OPENAI_API_KEY="xxxxxxxxx"
./lab_setup.sh
```

## Lab instructions

### OpenAI Responses API
https://platform.openai.com/docs/api-reference/responses

#### Simple textbook example
The simplest possible call. Notice the structure is leaner than Chat Completions: just a `model` and an `input` string. No `messages` array, no `role` wrappers.
```bash
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthroughs of AI in 2025?"
    }'
```

#### `jq` to the rescue
The raw response is verbose. Use `jq` to extract just the text. Notice the path is different from Chat Completions: instead of `.choices[0].message.content`, the Responses API uses `.output[].content[0].text`.
```bash
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthroughs of AI in 2025?"
    }' | jq -r '.output[].content[0].text'
```

Also try extracting the token usage to see how it compares to Chat Completions:
```bash
curl -s -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthroughs of AI in 2025?",
        "max_output_tokens": 200
    }' | jq '.usage'
```

**Note:** Without tools, the model can only answer from its training data. Its knowledge has a cutoff date, so the answer may be incomplete or outdated for recent events.

#### Adding `web_search_preview`
The Responses API has built-in tool support. Adding `web_search_preview` lets the model search the web in real time before answering. Compare this output to the previous call and notice the difference in freshness and specificity.
```bash
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthroughs of AI in 2025?"
    }' | jq -r '.output[] | select(.type == "message") | .content[0].text'
```

The response also contains link annotations (the sources the model used). Extract them with a more targeted `jq` filter:
```bash
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthroughs of AI in 2025?"
    }' | jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | {text: .text, links: [.annotations[]?.url]}'
```

#### File search
Upload a file and query its contents. This is a building block for RAG workflows (which you'll explore in depth in lab040). Here we upload a PDF and ask the model about it.
```bash
FILEID=$(curl -s https://api.openai.com/v1/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F purpose="assistants" \
    -F file="@./data/story.pdf" | jq -r .id)
```
```bash
echo $FILEID
```

Now query the uploaded file. Notice the `input` can also be an array of role-based messages (similar to Chat Completions), but with richer content types like `input_file`:
```bash
curl -s "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": "'$FILEID'"
                    },
                    {
                        "type": "input_text",
                        "text": "What is this about?"
                    }
                ]
            }
        ]
    }' | jq -r '.output[].content[0].text'
```

#### Message recall
Every response has a unique ID (the `id` field in the JSON). You can fetch any past response by that ID, which is useful for debugging, auditing, or async workflows where you fire a request and retrieve the result later.

First, capture the response ID from a call:
```bash
RESP_ID=$(curl -s -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "Give me a one-sentence summary of the Turing test."
    }' | jq -r '.id')
echo $RESP_ID
```

Now recall it:
```bash
curl -s "https://api.openai.com/v1/responses/$RESP_ID" \
    -H "Authorization: Bearer $OPENAI_API_KEY" | jq -r '.output[].content[0].text'
```
You get the exact same response back without making a new model call. This is stored server-side (notice `"store": true` in the raw response metadata).

#### Multi-turn conversations with `previous_response_id`
In lab010, continuing a conversation meant resending the *entire* message history on every call. The Responses API simplifies this with `previous_response_id`: you just point to the last response, and the API handles context automatically.
```bash
RESP1=$(curl -s -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "What is the CAP theorem in distributed systems?"
    }' | jq -r '.id')
echo "First response ID: $RESP1"
```

Now follow up, referencing the previous response:
```bash
curl -s -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "previous_response_id": "'$RESP1'",
        "input": "Give me a real-world example of choosing AP over CP."
    }' | jq -r '.output[].content[0].text'
```
The model has full context of the previous exchange without you having to resend it. This keeps payloads small and makes multi-step agent workflows much cleaner.

#### Streaming
Like Chat Completions, the Responses API supports streaming. Set `"stream": true` and the response arrives as Server-Sent Events (SSE), token by token.
```bash
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthroughs of AI?",
        "stream": true
    }'
```
The SSE event types are different from Chat Completions. Look for `response.output_text.delta` events that carry the text fragments.

#### Structured Output
See [./ADDON.md](./ADDON.md) for structured output with JSON Schema enforcement.

### Chat Completions vs Responses API: Quick Comparison

| | Chat Completions (`/v1/chat/completions`) | Responses API (`/v1/responses`) |
|---|---|---|
| **Input format** | `messages` array with role objects | `input` (string or message array) |
| **Output format** | `choices[0].message.content` | `output[].content[0].text` |
| **Multi-turn** | Resend full history every call | `previous_response_id` |
| **Built-in tools** | None (you implement them) | `web_search_preview`, `file_search`, etc. |
| **Response recall** | Not available | GET by response ID |
| **Structured output** | `response_format: {"type": "json_object"}` | `text.format` with full JSON Schema |

Both APIs use the same models. Chat Completions is simpler for one-shot tasks; the Responses API shines when you need tools, multi-turn state, or structured output.

## Cleanup environment
```bash
deactivate
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
