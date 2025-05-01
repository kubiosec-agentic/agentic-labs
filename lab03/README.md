# LAB03
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
### Evals
#### Create an request
```
curl https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json"     \
    -d '{
        "model": "gpt-4.1",
        "messages": [
            {
                "role": "developer",
                "content": "Categorize the following support ticket into one of Hardware, Software, or Other."
            },
            {
                "role": "user",
                "content": "My monitor wont turn on - help!"
            }
        ]
    }'
```
#### Creating an eval
```
curl https://api.openai.com/v1/evals \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "IT Ticket Categorization",
        "data_source_config": {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "ticket_text": { "type": "string" },
                    "correct_label": { "type": "string" }
                },
                "required": ["ticket_text", "correct_label"]
            },
            "include_sample_schema": true
        },
        "testing_criteria": [
            {
                "type": "string_check",
                "name": "Match output to human label",
                "input": "{{ sample.output_text }}",
                "operation": "eq",
                "reference": "{{ item.correct_label }}"
            }
        ]
    }'
```

```
{
  "object": "eval",
  "id": "eval_6813e1235630819094b3646a860de26f",
  "data_source_config": {
    "type": "custom",
    "schema": {
      "type": "object",
      "properties": {
        "item": {
          "type": "object",
          "properties": {
            "ticket_text": {
              "type": "string"
            },
            "correct_label": {
              "type": "string"
            }
          },
          "required": [
            "ticket_text",
            "correct_label"
          ]
        },
        "sample": {
          "type": "object",
          "properties": {
            "model": {
              "type": "string"
            },
            "choices": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "message": {
                    "type": "object",
                    "properties": {
                      "role": {
                        "type": "string",
                        "enum": [
                          "assistant"
                        ]
                      },
                      "content": {
                        "type": [
                          "string",
                          "null"
                        ]
                      },
                      "refusal": {
                        "type": [
                          "boolean",
                          "null"
                        ]
                      },
                      "tool_calls": {
                        "type": [
                          "array",
                          "null"
                        ],
                        "items": {
                          "type": "object",
                          "properties": {
                            "type": {
                              "type": "string",
                              "enum": [
                                "function"
                              ]
                            },
                            "function": {
                              "type": "object",
                              "properties": {
                                "name": {
                                  "type": "string"
                                },
                                "arguments": {
                                  "type": "string"
                                }
                              },
                              "required": [
                                "name",
                                "arguments"
                              ]
                            },
                            "id": {
                              "type": "string"
                            }
                          },
                          "required": [
                            "type",
                            "function",
                            "id"
                          ]
                        }
                      },
                      "function_call": {
                        "type": [
                          "object",
                          "null"
                        ],
                        "properties": {
                          "name": {
                            "type": "string"
                          },
                          "arguments": {
                            "type": "string"
                          }
                        },
                        "required": [
                          "name",
                          "arguments"
                        ]
                      }
                    },
                    "required": [
                      "role"
                    ]
                  },
                  "finish_reason": {
                    "type": "string"
                  }
                },
                "required": [
                  "index",
                  "message",
                  "finish_reason"
                ]
              }
            },
            "output_text": {
              "type": "string"
            },
            "output_json": {
              "type": "object"
            },
            "output_tools": {
              "type": "array",
              "items": {
                "type": "object"
              }
            }
          },
          "required": [
            "model",
            "choices"
          ]
        }
      },
      "required": [
        "item",
        "sample"
      ]
    }
  },
  "testing_criteria": [
    {
      "name": "Match output to human label",
      "id": "Match output to human label-f1c79982-df7e-4470-91d5-2008c67b8c9c",
      "type": "string_check",
      "input": "{{ sample.output_text }}",
      "reference": "{{ item.correct_label }}",
      "operation": "eq"
    }
  ],
  "name": "IT Ticket Categorization",
  "created_at": 1746133283,
  "metadata": {}
}
```
#### Uploading the test data
```
curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="evals" \
  -F file="@tickets.jsonl"
```
```
{
  "object": "file",
  "id": "file-EsrvPZ76WpsACkuVkyWoPq",
  "purpose": "evals",
  "filename": "tickets.jsonl",
  "bytes": 268,
  "created_at": 1746133376,
  "expires_at": null,
  "status": "processed",
  "status_details": null
}
```
#### Creating an eval run
```
curl https://api.openai.com/v1/evals/eval_6813e552ae1c8190a96990dbdf42cbf0/runs \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d @request.json


```
```
{
  "id": "chatcmpl-BSVEe2Oigm2M3k4hBZC00NRFiq9W0",
  "object": "chat.completion",
  "created": 1746132952,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hardware",
        "refusal": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 35,
    "completion_tokens": 2,
    "total_tokens": 37,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "audio_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "service_tier": "default",
  "system_fingerprint": "fp_a6889ffe71"
}
```
```

```
#### Analyze
curl https://api.openai.com/v1/evals/eval_abc123/runs/evalrun_abc123 \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json"


## Cleanup environment
```
./lab_cleanup.sh
```
