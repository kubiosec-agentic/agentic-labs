# LAB05
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
### Langchain agent without tool support
```
python3 Tools_01.py
```
### Langchain agent with tool support
```
python3 Tools_02.py
```
### Small CTF
```
python3 ./Tools_03.py
```
```
curl -XPOST http://127.0.0.1:5000/v1/chat/completions  \
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
            "text": "What is the SQRT of 12345"
          }
        ]
      }
    ]
  }'
```
## Cleanup environment
```
./lab_cleanup.sh
```
