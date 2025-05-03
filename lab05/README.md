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
Start the ChatBot
```
docker run -it -p 8501:8501 \
  --rm \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  --name demochatbox \
  xxradar/mymadchatbox:v2  \
  /bin/bash -c "./start.sh & tail -f /dev/null"
```
You can connect to `http://127.0.0.1:8501/`<br>
### Small CTF - Optional (middleware function only)
```
python3 ./Tools_03.py
```
```
curl -XPOST http://127.0.0.1:5000/v1/chat/completions  \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxxxxxxxx" \
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
### Langchain agent with Wikipedia support
```
python3 Tools_04.py
```
### Openai with custom tools support
```
python3 Tools_05.py
```
### Openai with custom tools support DEEPDIVE
```
docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 127.0.0.1:8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --mode reverse:https://api.openai.com:443
```
```
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
```
```
python3 Tools_05.py
```
#### Optional for hackers
Modify `Tools_04.py`
```
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, base_url="http://127.0.0.1:8080/v1")
```

## Cleanup environment
```
./lab_cleanup.sh
```
