import requests
import json
import os

# Get API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Prepare the request
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "what is AI ?"
                }
            ]
        }
    ],
    "response_format": {
        "type": "text"
    },
    "temperature": 1,
    "max_completion_tokens": 2048,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "store": False
}

# Make the API request
response = requests.post(url, headers=headers, json=data)

# Check if request was successful
if response.status_code == 200:
    response_data = response.json()
    print(response_data['choices'][0]['message']['content'])
else:
    print(f"Error: {response.status_code}")
    print(response.text)