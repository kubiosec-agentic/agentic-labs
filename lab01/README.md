![ChatCompletion](https://img.shields.io/badge/ChatCompetion-green) ![Curl](https://img.shields.io/badge/Curl-orange) ![Python](https://img.shields.io/badge/Python-blue)

# LAB01: Chat Completions 
## Introduction
LAB01 introduces the foundational steps for interacting with the OpenAI Chat Completions API. You’ll set up a working development environment, learn how to send requests using curl, structure conversations with system prompts, extract responses using jq, and even perform image-based tasks. The lab also covers Python-based API usage and debugging tools like mitmproxy to deepen your understanding of how requests flow. This lab is ideal for anyone looking to build a solid grasp of OpenAI API mechanics through hands-on practice.
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab01/bin/activate
```
## Lab instructions
### OpenAI Chat Commpletion
https://platform.openai.com/docs/api-reference/chat
#### Simple textbook example
This lab demonstrates a simple textbook example of how to call the OpenAI Chat Completions API using `curl`.
```
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
#### Adding a System prompt
Next, add a system prompt to guide the behavior of the assistant in an OpenAI Chat API request.
```
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
#### `jq` to the rescue
This lab introduces the use of `jq` to neatly extract and display the assistant’s reply from the JSON response.
```
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
#### Continuing the conversation
This lab demonstrates how to continue a conversation by including previous messages in the prompt to maintain context and coherence.
```
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
#### Attaching request.json
This lab shows how to simplify API calls by placing the request payload in a separate `request.json` file and referencing it with `@`.
```
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d @request.json
```
#### Things to think about
See [./ADDON.md](./ADDON.md)

#### Image analysis
This lab illustrates how to perform image analysis with the Chat Completions API by sending an image URL and requesting a specific extraction task, such as reading a license plate.
```
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
Try this ;-)
```
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
              "url": "https://i.sstatic.net/Iodjt.jpg"
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
This example introduces streaming , allowing you to receive the model’s output token by token as it generates. This is great for faster feedback and interactive experiences.
```
curl -XPOST "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Write a poem about the stars."}],
    "stream": true
  }'
```
Adding some `grep` magic:
```
curl -XPOST "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Write a poem about the stars."}],
    "stream": true
  }' | grep -oP '(?<="content":")[^"]*'
```
#### Chat completion via Python
This lab demonstrates how to make a Chat Completions API call using Python, and how to intercept and inspect the request using `mitmproxy` for debugging or learning purposes. **(Terminal_1)**
```
export OPENAI_BASE_URL="https://api.openai.com/v1"
```
```
python3 chat_01.py
```
Inspect the Chat completion call with `mitmproxy` **(Terminal_2)**
```
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 127.0.0.1:8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --mode reverse:https://api.openai.com:443
```
Open your browser at `http://127.0.0.1:8081/?token=xxxxxx`<br><br>
In **Terminal_1**, update the base URL for you client application.
```
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
```
```
python3 chat_01.py
```
Don't forget to unset the environment variable !
```
unset OPENAI_BASE_URL
```
## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
