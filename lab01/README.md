# LAB01
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
### OpenAI Chat Commpletion
#### Simple textbook example
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
```
curl -XPOST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d @request.json
```
### OpenAI Resonses API
#### Simple textbook example
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthrough of ai in 2025?"
    }'
```
#### `jq` to the rescue
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthrough of ai in 2025?"
    }' | jq -r . 
```
#### Adding `web_search_preview`
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthrough of ai in 2025?"
    }' | jq -r '.output[].content[0].text'
```
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthrough of ai in 2025?"
    }' | jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | {text: .text, links: [.annotations[]?.url]}'
```
#### Image analysis
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
#### Streaming
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthrough of ai in 2025?",
        "stream": true
    }' 
```
## Cleanup environment
```
./lab_cleanup.sh
```
