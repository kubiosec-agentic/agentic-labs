## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_Setup.sh
```
## exercise 1
```
curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4.1",
        "input": "what are important breakthrough of ai in 2025?",
        "parallel_tool_calls": true,
        "store": false,
        "stream": false
    }' |
jq -r . 
```
```
curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4.1",
        "tools": [{"type": "web_search_preview"}],
        "input": "what are important breakthrough of ai in 2025?",
        "parallel_tool_calls": true,
        "store": false,
        "stream": false
    }' |
jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | {text: .text, links: [.annotations[]?.url]}'
```
