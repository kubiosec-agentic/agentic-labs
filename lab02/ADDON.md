#### Structered output (Response API)
This lab demonstrates how to request structured output using the Response API by passing a predefined JSON payload, ideal for extracting consistent, machine-readable responses from the model.
```
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json
```
#### Response
```
{
  "id": "resp_68131eb1af348191a020244d610d16a702e30b622906548d",
  "object": "response",
  "created_at": 1746083505,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "id": "msg_68131eb221408191b931d419b8c4b58f02e30b622906548d",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [],
          "text": "{\"steps\":[{\"explanation\":\"Start with the equation:\",\"output\":\"8x + 7 = -23\"},{\"explanation\":\"Subtract 7 from both sides to isolate the term with x:\",\"output\":\"8x + 7 - 7 = -23 - 7\"},{\"explanation\":\"This simplifies to:\",\"output\":\"8x = -30\"},{\"explanation\":\"Now, divide both sides by 8 to solve for x:\",\"output\":\"8x / 8 = -30 / 8\"},{\"explanation\":\"This simplifies to:\",\"output\":\"x = -30 / 8\"},{\"explanation\":\"Simplify the fraction by dividing both the numerator and the denominator by their greatest common divisor, which is 2:\",\"output\":\"x = -15 / 4\"}],\"final_answer\":\"x = -\\\\frac{15}{4}\"}"
        }
      ],
      "role": "assistant"
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "service_tier": "default",
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "json_schema",
      "description": null,
      "name": "math_reasoning",
      "schema": {
        "type": "object",
        "properties": {
          "steps": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "explanation": {
                  "type": "string"
                },
                "output": {
                  "type": "string"
                }
              },
              "required": [
                "explanation",
                "output"
              ],
              "additionalProperties": false
            }
          },
          "final_answer": {
            "type": "string"
          }
        },
        "required": [
          "steps",
          "final_answer"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 96,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 176,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 272
  },
  "user": null,
  "metadata": {}
}
```
#### Add some `jq` 
```
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json \
| jq -r '.output[].content[0].text' | jq -r .
```
```
{
  "steps": [
    {
      "explanation": "Start by isolating the term with the variable. We need to get rid of the constant on the left side of the equation.",
      "output": "8x + 7 - 7 = -23 - 7"
    },
    {
      "explanation": "Simplify both sides of the equation. The left side becomes just the term with the variable, and the right side simplifies to a new constant.",
      "output": "8x = -30"
    },
    {
      "explanation": "To solve for x, divide both sides by the coefficient of x.",
      "output": "x = -30 / 8"
    },
    {
      "explanation": "Simplify the fraction on the right side of the equation to get the final value for x.",
      "output": "x = -15/4 or x = -3.75"
    }
  ],
  "final_answer": "x = -15/4 or x = -3.75"
}
```
#### Structured output in python
Pydantic is a Python library for data validation and data parsing using Python type hints. <br>
It allows you to define data models with expected fields and types, and it will:
- validate incoming data
- parse it into structured objects
- raise clear errors if the data doesn't match
```
python3 ./resp_03.py
```
