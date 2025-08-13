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
      "role": "system",
      "content": [
        {
          "type": "input_text",
          "text": "You are a helpful assistant that provides information about the Model Context Protocol (MCP)."
        }
      ]
    }
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
        "vs_689bb74f20388191a7a26b548f72ccd3"
      ]
    }
  ],
  temperature=1,
  max_output_tokens=2048,
  top_p=1,
  store=True
)
print(response.output_text)
