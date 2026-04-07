![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Responses_API](https://img.shields.io/badge/Responses_API-brightgreen) ![Structured_Output](https://img.shields.io/badge/Structured_Output-purple)

# LAB020 ADDON: Structured Output with JSON Schema

In lab010's ADDON you saw `response_format: {"type": "json_object"}`, which forces the model to return valid JSON but gives you no control over the *shape* of that JSON. The Responses API takes this further with `text.format`, where you define a full JSON Schema and the model is **guaranteed** to conform to it. Every field, every type, every required property will match your specification.

This matters for automation. When your downstream code expects an object with specific keys, a missing field or wrong type breaks the pipeline. Structured output eliminates that class of errors entirely.

---

## 1. Math reasoning with step-by-step schema

The file `request.json` defines a structured output request that asks the model to solve a math problem and return the solution as a JSON object with `steps` (an array of explanation/output pairs) and a `final_answer` string.

Run it:
```bash
curl -s https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json
```

The raw response is large. Look at two things in it:

1. The `output[0].content[0].text` field contains the model's answer as a JSON *string*
2. The `text.format` section echoes back your schema, confirming the model was constrained to it

To extract just the structured answer:
```bash
curl -s https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json \
| jq -r '.output[].content[0].text' | jq .
```

You should see something like:
```json
{
  "steps": [
    {
      "explanation": "Start by isolating the term with the variable. Subtract 7 from both sides.",
      "output": "8x + 7 - 7 = -23 - 7"
    },
    {
      "explanation": "Simplify both sides.",
      "output": "8x = -30"
    },
    {
      "explanation": "Divide both sides by 8 to solve for x.",
      "output": "x = -30 / 8"
    },
    {
      "explanation": "Simplify the fraction.",
      "output": "x = -15/4 or x = -3.75"
    }
  ],
  "final_answer": "x = -15/4 or x = -3.75"
}
```

Notice the two-stage `jq` pipeline: the first `jq -r` extracts the text field (which is itself a JSON string), and the second `jq .` pretty-prints the parsed JSON. This double-extraction is a pattern you'll use whenever structured output is involved, because the API wraps the JSON content inside a text field.

Open `request.json` in your editor and look at the `text.format.schema` section. Every `required`, `additionalProperties: false`, and type constraint is enforced by the API. Try removing a required field from the schema and see how the output changes.

---

## 2. Data extraction from unstructured text

This is where structured output becomes practical. Given a blob of free text, the model extracts specific fields into a predictable JSON structure. This is directly useful for parsing emails, log entries, recon output, or any unstructured data.
```bash
curl -sS https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "input": "Extract contact information: John Smith works at Acme Corp as a Senior Developer. His email is john.smith@acme.com and he has 12 years of experience with Python, Go, and Kubernetes.",
    "text": {
      "format": {
        "type": "json_schema",
        "name": "contact_extraction",
        "strict": true,
        "schema": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "company": { "type": "string" },
            "position": { "type": "string" },
            "email": { "type": "string" },
            "phone": { "type": "string" },
            "skills": { "type": "array", "items": { "type": "string" } },
            "years_experience": { "type": "number" }
          },
          "required": [
            "name", "company", "position", "email",
            "phone", "skills", "years_experience"
          ],
          "additionalProperties": false
        }
      }
    }
  }' | jq -r '.output[0].content[0].text' | jq .
```

Expected output:
```json
{
  "name": "John Smith",
  "company": "Acme Corp",
  "position": "Senior Developer",
  "email": "john.smith@acme.com",
  "phone": "",
  "skills": ["Python", "Go", "Kubernetes"],
  "years_experience": 12
}
```

Notice that `phone` is an empty string (the text didn't mention one) and `years_experience` is a number, not a string. The schema enforces the types, so your downstream code can safely do `data["years_experience"] > 10` without type checking.

The `"strict": true` parameter is what makes this reliable. Without it, the model might approximate the schema but could still deviate. With `strict: true`, the API guarantees exact conformance.

---

## 3. Security-relevant extraction: CVE parsing

A more training-relevant example. Imagine you're parsing vulnerability advisories from a feed and need structured data for your tooling:
```bash
curl -sS https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "input": "Parse this advisory: CVE-2024-3094 is a critical backdoor vulnerability found in xz-utils versions 5.6.0 and 5.6.1 affecting Linux distributions. It was discovered on March 29, 2024 by Andres Freund. The CVSS score is 10.0. The backdoor was inserted into the build process through malicious modifications to the upstream tarball, targeting the SSH daemon through systemd integration.",
    "text": {
      "format": {
        "type": "json_schema",
        "name": "cve_extraction",
        "strict": true,
        "schema": {
          "type": "object",
          "properties": {
            "cve_id": { "type": "string" },
            "severity": { "type": "string" },
            "cvss_score": { "type": "number" },
            "affected_software": { "type": "string" },
            "affected_versions": { "type": "array", "items": { "type": "string" } },
            "discovery_date": { "type": "string" },
            "discoverer": { "type": "string" },
            "attack_vector": { "type": "string" },
            "summary": { "type": "string" }
          },
          "required": [
            "cve_id", "severity", "cvss_score", "affected_software",
            "affected_versions", "discovery_date", "discoverer",
            "attack_vector", "summary"
          ],
          "additionalProperties": false
        }
      }
    }
  }' | jq -r '.output[0].content[0].text' | jq .
```

This produces a clean, machine-readable CVE record that you could feed into a database, a Slack notification, or a SIEM integration. The schema guarantees you always get the same fields with the same types, regardless of how the advisory text is written.

---

## Structured output vs JSON mode: when to use which

| | JSON mode (Chat Completions) | JSON Schema (Responses API) |
|---|---|---|
| **Guarantee** | Valid JSON, any shape | Valid JSON, exact shape you defined |
| **Schema enforcement** | None (model guesses the structure) | Full (every field, type, and constraint) |
| **`strict` mode** | Not available | Available, guarantees conformance |
| **Best for** | Simple key-value extraction | Complex, typed structures for automation |
| **Risk** | Missing fields, wrong types, extra keys | None (schema violations are impossible) |

For anything you'll parse programmatically, prefer the Responses API with a schema. Reserve JSON mode for quick one-off extractions where the exact shape doesn't matter.
