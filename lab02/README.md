# LAB02
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab02/bin/activate
```
## Lab instructions
### OpenAI Resonses API
https://platform.openai.com/docs/api-reference/responses
#### Simple textbook example
This lab provides a simple textbook example of making a basic API call to retrieve a response using the `/responses` endpoint.
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
Tired of digging through raw JSON? This lab shows how `jq` can make API responses clean, readable, and to the point.
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthrough of ai in 2025?"
    }' | jq -r . 
```
**Note:** The model may return outdated information, as its knowledge is limited to events before its training cutoff (e.g., mid-2023 for GPT-4o).
#### Adding `web_search_preview`
This lab demonstrates how to enable the `web_search_preview` tool, which lets the model search the web in real time, ideal for retrieving up-to-date information on recent breakthroughs, news, or current events.
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
#### File search
This lab demonstrates how to upload a file and query its contents using the API, perfect for letting the model analyze documents like PDFs.
```
FILEID=$(curl https://api.openai.com/v1/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F purpose="assistants" \
    -F file="@./data/story.pdf" | jq -r .id)
```
```
curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4.1",
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

#### Streaming
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthrough of ai?",
        "stream": true
    }' 
```
#### Message recall
```
curl "https://api.openai.com/v1/responses/resp_<id>" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### Message callback python
```
python3 ./resp_01.py
```
## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
