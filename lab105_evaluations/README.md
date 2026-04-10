![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Evaluations](https://img.shields.io/badge/Evaluations-yellow) ![Curl](https://img.shields.io/badge/Curl-orange)

# LAB105: Prompt Evaluation with OpenAI Evals

## Introduction

When you deploy a prompt in production, how do you know it actually
works? Manually testing a few examples is not enough. OpenAI Evals
lets you define a test dataset, run your prompt against every row, and
automatically score the results.

This lab walks through the full eval workflow using only `curl`
commands against the OpenAI API. The use case is simple: classify IT
support tickets as "Hardware", "Software", or "Other". By the end
you will have created an eval, uploaded test data, run it, and
retrieved a scored report.

You will learn to:

- Call the Chat Completions API with a classification prompt
- Create a custom eval with a `string_check` testing criterion
- Upload a `.jsonl` test dataset
- Trigger an eval run and retrieve scored results
- Interpret pass/fail counts to measure prompt quality

## Why does this matter?

Evals turn "I think this prompt is good enough" into "this prompt
scores 80% on my test set." That number is what lets you compare
prompt versions, catch regressions, and decide whether a cheaper model
works just as well. Without evals, prompt engineering is guesswork.

## Set up your environment

You only need `curl` and `jq`. No Python, no virtual environment.

```bash
export OPENAI_API_KEY="sk-..."
```

```bash
./lab_setup.sh
```

## Lab instructions

### Step 1: Test the classification prompt

Before building an eval, verify that the prompt works for a single
example. This uses the standard Chat Completions API with the
`developer` role (system-level instructions):

```bash
curl https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
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

You should see `"content": "Hardware"` (or similar) in the response.

### Step 2: Create an eval

An eval defines what you are testing and how to score it. Here we
create a custom eval with:

- An **item schema** describing the test data (ticket_text + correct_label)
- A **string_check** criterion that compares the model output to the
  human label

```bash
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
    }' | jq -r .id)
```

```bash
echo $EVAL
```

This returns an eval ID like `eval_6813e123...`. You will use it in
the next steps.

### Step 3: Upload test data

The test data is a JSONL file where each line has a ticket and its
correct label. Take a look at `tickets.jsonl`:

```json
{ "item": { "ticket_text": "My monitor won't turn on!", "correct_label": "Hardware" } }
{ "item": { "ticket_text": "I'm in vim and I can't quit!", "correct_label": "Software" } }
{ "item": { "ticket_text": "Best restaurants in Cleveland?", "correct_label": "Other" } }
```

Upload it:

```bash
FILEID=$(curl https://api.openai.com/v1/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F purpose="evals" \
    -F file="@tickets.jsonl" | jq -r .id)
```

```bash
echo $FILEID
```

### Step 4: Run the evaluation

First, patch the file ID into `request.json`:

```bash
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' 's/"id": *"[^"]*"/"id": "'"$FILEID"'"/' request.json
else
    sed -i 's/"id": *"[^"]*"/"id": "'"$FILEID"'"/' request.json
fi
```

Then kick off the eval run. This sends every row in the test file
through the prompt template and scores each response:

```bash
EVALRUN=$(curl https://api.openai.com/v1/evals/$EVAL/runs \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d @request.json | jq -r .id)
```

```bash
echo $EVALRUN
```

### Step 5: Get the results

Wait a few seconds for the run to complete, then fetch the results:

```bash
RESULTS=$(curl -s https://api.openai.com/v1/evals/$EVAL/runs/$EVALRUN \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json")
```

```bash
echo $RESULTS | jq '{status, result_counts, report_url}'
```

You should see something like:

```json
{
  "status": "completed",
  "result_counts": {
    "total": 10,
    "errored": 0,
    "failed": 2,
    "passed": 8
  },
  "report_url": "https://platform.openai.com/evaluations/..."
}
```

Open the `report_url` in your browser to see the full evaluation
report with per-item results.

### Understanding the results

The `result_counts` tell you how many test items the model got right
(`passed`) vs wrong (`failed`). In this case 8/10 = 80% accuracy.

The `string_check` criterion uses exact string matching (`eq`), so if
the model returns "hardware" instead of "Hardware", it counts as a
failure. This is intentional: it forces you to think about how
strictly you want to evaluate.

### What to try next

- Edit `tickets.jsonl` to add more test cases and re-run
- Change the model in `request.json` from `gpt-4.1` to `gpt-4.1-mini`
  and compare accuracy
- Modify the developer prompt to be more specific and see if the score
  improves
- Try `"operation": "includes"` instead of `"eq"` in the testing
  criteria for a more lenient match

## How OpenAI Evals works

```
                      +-----------------+
  tickets.jsonl  ---> |  OpenAI Evals   |
  (test data)         |                 |
                      |  For each row:  |
  request.json  ----> |  1. Fill prompt |
  (prompt template)   |  2. Call model  |
                      |  3. Score output|
                      +-----------------+
                              |
                              v
                      result_counts:
                        passed: 8
                        failed: 2
```

The key insight: evals are just automated prompt testing. You define
the test cases, the prompt template, and the scoring criteria. OpenAI
handles the rest.

## Cleanup

```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
