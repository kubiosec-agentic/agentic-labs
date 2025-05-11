from openai import OpenAI
client = OpenAI()

response = client.responses.create(
  model="gpt-4.1",
  input=[
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "What is MCP"
        }
      ]
    },
    {
      "id": "fs_6820af9d7fbc8191b9f05fac514db0ba0a638291e0ae4c37",
      "type": "file_search_call",
      "status": "completed",
      "queries": [
        "What is MCP?",
        "MCP definition",
        "meaning of MCP",
        "MCP abbreviation",
        "explanation of MCP"
      ],
    },
   
  ],
  text={
    "format": {
      "type": "text"
    }
  },
  reasoning={},
  tools=[
    {
      "type": "file_search",
      "vector_store_ids": [
        "vs_681a17ced92c8191ae16027451d95bec"
      ]
    }
  ],
  temperature=1,
  max_output_tokens=2048,
  top_p=1,
  store=True
)
print(response.output_text)
