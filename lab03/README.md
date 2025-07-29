![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Evaluations](https://img.shields.io/badge/Evaluations-yellow) ![Curl](https://img.shields.io/badge/Curl-orange) 

# LAB03: Prompt Evaluation
## Introduction
This lab walks through setting up and running OpenAI Evals to test how well models perform on classification tasks. In this example we focus on IT ticket categorization.

You'll learn to:
- Make evaluation prompts using the Chat Completions API
- Define and create custom evals
- Upload test data (.jsonl) and run evaluations
- Fetch results and view reports via the API

Perfect for validating prompt quality and measuring model accuracy with structured, repeatable tests.
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
### Evals
This lab walks through the process of prompt evaluation, useful for testing how well the model handles classification tasks.
#### Create an request
An example prompt for ticket categorization.
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
A textbook response
```
{
  "id": "chatcmpl-BSiptlaw3aGt5e6WhLe1fFtMNkgtD",
  "object": "chat.completion",
  "created": 1746185233,
  "model": "gpt-4.1-2025-04-14",
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
  "system_fingerprint": "fp_7439084672"
}
```
#### Creating an eval
How to evaluate the prompts ?
```
EVAL=$(curl https://api.openai.com/v1/evals \
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
    }'  | jq -r .id)
```
```
echo $EVAL
```
<details>
<summary>
Complete example response
</summary>

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
    
</details>

#### Uploading the test data
Test data is upload in with filetype `jsonl` as `purpose="evals"`
```
FILEID=$(curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="evals" \
  -F file="@tickets.jsonl" | jq -r .id)
```
```
echo $FILEID
```
<details>
<summary>
Complete example response
</summary>

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
</details>

#### Run Evaluation
Update `request.json` manually with the `FILEID` or run
```
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' 's/"id": *"[^"]*"/"id": "'"$FILEID"'"/' request.json
else
  sed -i 's/"id": *"[^"]*"/"id": "'"$FILEID"'"/' request.json
fi
```
The evaluation is described in `request.json`
```
{
    "name": "Categorization text run",
    "data_source": {
      "type": "completions",
      "model": "gpt-4.1",
      "input_messages": {
        "type": "template",
        "template": [
          {
            "role": "developer",
            "content": "You are an expert in categorizing IT support tickets. Given the support ticket below, categorize the request into one of \"Hardware\", \"Software\", or \"Other\". Respond with only one of those words."
          },
          {
            "role": "user",
            "content": "{{ item.ticket_text }}"
          }
        ]
      },
      "source": {
        "type": "file_id",
        "id": "file-xxxxxxxxx"
      }
    }
  }
```
Run the evaluation
```
EVALRUN=$(curl https://api.openai.com/v1/evals/$EVAL/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json | jq -r .id)
```
```
echo $EVALRUN
```
<details>
<summary>
Complete example response
</summary>

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

</details>

#### Get the results
```
RESULTS=$(curl https://api.openai.com/v1/evals/$EVAL/runs/$EVALRUN \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" | jq -r .)
```
```
echo $RESULTS | jq -r '.report_url'
echo $RESULTS | jq -r '.result_counts'
echo $RESULTS | jq -r '.report_url'
```
<details>
<summary>
Complete example response
</summary>

```
{
  "object": "eval.run",
  "id": "evalrun_68148f7e68688190baf81ad26e979d79",
  "eval_id": "eval_68148f1f19788190b23bd7f696b4cbb8",
  "report_url": "https://platform.openai.com/evaluations/eval_68148f1f19788190b23bd7f696b4cbb8?project_id=proj_XxzlqLOnLi1bHLHQ1Ev5StfG&run_id=evalrun_68148f7e68688190baf81ad26e979d79",
  "status": "completed",
  "model": "gpt-4.1",
  "name": "Categorization text run",
  "created_at": 1746177918,
  "result_counts": {
    "total": 10,
    "errored": 0,
    "failed": 1,
    "passed": 9
  },
  "per_model_usage": [
    {
      "model_name": "gpt-4.1-2025-04-14",
      "invocation_count": 10,
      "prompt_tokens": 583,
      "completion_tokens": 20,
      "total_tokens": 603,
      "cached_tokens": 0
    }
  ],
  "per_testing_criteria_results": [
    {
      "testing_criteria": "Match output to human label-3c7654c3-a890-474b-b547-4a656a741727",
      "passed": 9,
      "failed": 1
    }
  ],
  "data_source": {
    "type": "completions",
    "source": {
      "type": "file_id",
      "id": "file-WhUVHwoc8MuWtoYZn9myXa"
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

</details>

## Cleanup environment
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
