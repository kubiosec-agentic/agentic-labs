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
            "text": "What is machine learning?"
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": "Machine learning is a subset of AI that enables computers to learn from data and improve over time without being explicitly programmed."
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Give an example of machine learning in daily life."
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": "A common example is email spam filtering, where the system learns to detect and block unwanted emails based on patterns in the data."
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is AI?\nHow is it used in daily life?\nIs it safe?"
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
"Artificial intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. It involves using algorithms and models to enable machines to perform tasks that typically require human intelligence, such as understanding natural language, recognizing patterns, and making decisions.\n\nIn daily life, AI is used in various ways:\n- **Virtual assistants** like Siri, Alexa, and Google Assistant help users with tasks and information through voice commands.\n- **Recommender systems** in platforms like Netflix and Amazon suggest movies, products, or music based on user preferences.\n- **Navigation apps** like Google Maps use AI to provide real-time traffic updates and route suggestions.\n- **Smart home devices** can automate and optimize energy usage or security through AI.\n- **Customer service chatbots** enhance user interactions and provide instant support on websites.\n\nRegarding safety, AI itself is generally safe, but its safety depends on how it is implemented, governed, and used. Concerns can arise from errors in decision-making, privacy and security breaches, or ethical issues like bias in algorithms. Ensuring safe AI requires robust design, ethical guidelines, and effective regulations. It is important for developers and users to remain vigilant about these factors to mitigate risks."
```
