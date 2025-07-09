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
        "vs_686ed51e3c548191ab313b20504a268a"
      ]
    }
  ],
  temperature=1,
  max_output_tokens=2048,
  top_p=1,
  store=True
)
print(response.output_text)
