## Few-shot prompting example
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
            "text": "A whatpu is a small, furry animal native to Tanzania. An example of a sentence that uses the word whatpu is:\nWe were traveling in Africa and we saw these very cute whatpus.\n\nTo do a \"farduddle\" means to jump up and down really fast. An example of a sentence that uses the word farduddle is:"
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 1024,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }' | jq '.choices[0].message.content'
```
```
"The children were so excited about the news that they started to farduddle in the living room."
"During the festival, the children were so excited that they couldn't help but farduddle in the grass."
"The children were so excited about the carnival that they couldn't help but farduddle with joy."
```
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
            "text": "This is awesome! // Negative \nThis is bad! // Positive \n Wow that movie was rad! // Positive \n What a enlightening show! //"
          }
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 1024,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }' | jq '.choices[0].message.content'
