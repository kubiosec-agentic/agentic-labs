# LAB01
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_Setup.sh
```
## Lab instructions
### Raw curl request
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthrough of ai in 2025?"
    }'
```
### jq to the rescue
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "input": "what are important breakthrough of ai in 2025?"
    }' | 
jq -r . 
```
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthrough of ai in 2025?"
    }'
| jq -r '.output[].content[0].text'
```
```
curl -XPOST "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthrough of ai in 2025?"
    }' |
jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | {text: .text, links: [.annotations[]?.url]}'
```
### Streaming
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
