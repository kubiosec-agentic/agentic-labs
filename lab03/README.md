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
    }'  | jq -r .id
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
  -F file="@tickets.jsonl" | jq -r .id
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

#### Analyze
```
url https://api.openai.com/v1/evals/eval_68148c0b34088190a6cf38e705e1ddbf/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json
```
```
{
  "object": "eval.run",
  "id": "evalrun_68148d1e89a08190bf5852498fcdb6db",
  "eval_id": "eval_68148c0b34088190a6cf38e705e1ddbf",
  "report_url": "https://platform.openai.com/evaluations/eval_68148c0b34088190a6cf38e705e1ddbf?project_id=proj_XxzlqLOnLi1bHLHQ1Ev5StfG&run_id=evalrun_68148d1e89a08190bf5852498fcdb6db",
  "status": "queued",
  "model": "gpt-4.1",
  "name": "Categorization text run",
  "created_at": 1746177311,
  "result_counts": {
    "total": 0,
    "errored": 0,
    "failed": 0,
    "passed": 0
  },
  "per_model_usage": null,
  "per_testing_criteria_results": null,
  "data_source": {
    "type": "completions",
    "source": {
      "type": "file_id",
      "id": "file-8rn4wHqWo14MaSFZAjC1S3"
    },
    "input_messages": {
      "type": "template",
      "template": [
        {
          "type": "message",
          "role": "developer",
          "content": {
            "type": "input_text",
            "text": "You are an expert in categorizing IT support tickets. Given the support ticket below, categorize the request into one of \"Hardware\", \"Software\", or \"Other\". Respond with only one of those words."
          }
        },
        {
          "type": "message",
          "role": "user",
          "content": {
            "type": "input_text",
            "text": "{{ item.ticket_text }}"
          }
        }
      ]
    },
    "model": "gpt-4.1",
    "sampling_params": null
  },
  "error": null,
  "metadata": {},
  "shared_with_openai": false
}
```
## Cleanup environment
```
./lab_cleanup.sh
```
