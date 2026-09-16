#!/usr/bin/env bash
#
# Exercise 4a: the same skill, uploaded to OpenAI and run on the hosted
# Responses API, driven with curl.
#
# This is the OTHER end of the spectrum from agent_01..03. There you ran the
# skill locally with your own loader. Here the skill folder is uploaded to
# OpenAI, referenced by id, and the scripts run in OpenAI's sandbox (the
# `shell` tool with a `container_auto` environment). curl on purpose: it is
# what you reach for in CI, a Makefile, or a shell one-liner, and it shows the
# raw API with nothing hidden.
#
# Requirements:
#   - OPENAI_API_KEY set, on an account with skills access.
#   - jq (to pull the skill id out of the upload response).
#   - OPENAI_SKILL_MODEL set to a CURRENT model that supports the Responses
#     API shell tool. The example model strings in the docs move; do not trust
#     a hardcoded one. Read the current model off:
#     https://developers.openai.com/api/docs/guides/tools-skills
#
# Endpoints (verified against the OpenAI skills guide + cookbook):
#   POST /v1/skills                      upload a skill (multipart or zip)
#   POST /v1/skills/{id}/versions        add a version
#   POST /v1/skills/{id}                 {"default_version": N}
#   POST /v1/responses                   tools[].type=shell,
#                                        environment.type=container_auto,
#                                        environment.skills=[skill_reference]
set -euo pipefail

: "${OPENAI_API_KEY:?set OPENAI_API_KEY}"
: "${OPENAI_SKILL_MODEL:?set OPENAI_SKILL_MODEL to a current model that supports the Responses shell tool}"
command -v jq >/dev/null || { echo "install jq"; exit 1; }

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$HERE/../skills/http-header-audit"

echo "== 1. Upload skills/http-header-audit to OpenAI =="
# Each file is sent with ;filename=<folder>/<path> so the server rebuilds the
# skill's directory tree under one top-level folder. SKILL.md must sit at the
# folder root; scripts/ and references/ ride along.
UPLOAD=$(curl -sS -X POST 'https://api.openai.com/v1/skills' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "files[]=@$SKILL_DIR/SKILL.md;filename=http-header-audit/SKILL.md;type=text/markdown" \
  -F "files[]=@$SKILL_DIR/scripts/audit_headers.py;filename=http-header-audit/scripts/audit_headers.py;type=text/plain" \
  -F "files[]=@$SKILL_DIR/references/grading.md;filename=http-header-audit/references/grading.md;type=text/markdown")
echo "$UPLOAD" | jq .

# The upload response field holding the id is not documented verbatim; accept
# either .id or .skill_id.
SKILL_ID=$(echo "$UPLOAD" | jq -r '.id // .skill_id // empty')
[ -n "$SKILL_ID" ] || { echo "could not read skill id from upload response"; exit 1; }
echo "skill_id = $SKILL_ID"

echo
echo "== 2. Run it on the Responses API =="
# The task hands the headers inline, so the sandbox needs no network: the
# uploaded script grades what it is given. (Fetching would be a separate tool.)
# Build the request body with jq so quoting/escaping is always valid JSON.
HEADERS='{"Strict-Transport-Security":"max-age=0","Content-Security-Policy":"default-src '\''self'\''; script-src '\''unsafe-inline'\''","Server":"nginx/1.18.0"}'

BODY=$(jq -n \
  --arg model "$OPENAI_SKILL_MODEL" \
  --arg skill_id "$SKILL_ID" \
  --arg headers "$HEADERS" \
  '{
    model: $model,
    tools: [
      { type: "shell",
        environment: {
          type: "container_auto",
          skills: [ { type: "skill_reference", skill_id: $skill_id, version: "latest" } ]
        } }
    ],
    input: ("Use the http-header-audit skill to grade these response headers, then give me the letter grade and the two weakest headers. Headers: " + $headers)
  }')

curl -sS -L 'https://api.openai.com/v1/responses' \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d "$BODY" | jq -r '.output_text // .output // .'

echo
echo "Notes:"
echo "  - The scripts ran in OpenAI's sandbox, not on your machine. Blast radius"
echo "    is the sandbox, but so is data residency: the headers went to OpenAI."
echo "  - Ship a v2 with: curl -X POST .../v1/skills/$SKILL_ID/versions -F files=@...zip"
echo "    and pin it in the call ('version': 2). An unpinned 'latest' is a"
echo "    rug-pull surface: whoever can push a version changes what every caller runs."
