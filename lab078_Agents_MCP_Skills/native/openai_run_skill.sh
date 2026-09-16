#!/usr/bin/env bash
#
# Exercise 4a (run step, standalone): make the Responses API actually USE an
# already-uploaded skill.
#
# openai_uploaded_skill.sh does upload + run in one go. This script is just the
# run half, so once you have a skill_id you can call it as many times as you
# like without re-uploading, and see the raw curl with nothing built by jq.
#
#   export OPENAI_API_KEY=...
#   export OPENAI_SKILL_MODEL=<a current model that supports the Responses shell tool>
#   export SKILL_ID=skill_...        # from the upload step
#   ./native/openai_run_skill.sh
#   # optional: export SKILL_VERSION=1   to pin a specific integer version
#
# The skill is attached to the shell tool's environment. The model reads the
# skill, runs its script in OpenAI's sandbox on the headers given in `input`,
# and answers. Headers are inline, so the sandbox needs no network.
#
# On "version": we OMIT it, so the skill's default_version is used. The live API
# rejected version:"latest" ("Skill version '1' not found"); to pin a version,
# set SKILL_VERSION to the integer (e.g. 1), handled below.
set -euo pipefail
: "${OPENAI_API_KEY:?set OPENAI_API_KEY}"
: "${OPENAI_SKILL_MODEL:?set OPENAI_SKILL_MODEL to a current model that supports the Responses shell tool}"
: "${SKILL_ID:?set SKILL_ID to the id returned by the upload step}"

# Build the skill_reference: {skill_id} by default, plus integer version if pinned.
if [ -n "${SKILL_VERSION:-}" ]; then
  SKILL_REF="{ \"type\": \"skill_reference\", \"skill_id\": \"$SKILL_ID\", \"version\": $SKILL_VERSION }"
else
  SKILL_REF="{ \"type\": \"skill_reference\", \"skill_id\": \"$SKILL_ID\" }"
fi

# Plain, literal curl. Shell vars expand inside the unquoted heredoc; the header
# JSON is embedded as an escaped string (\" for its inner quotes).
curl -sS -L 'https://api.openai.com/v1/responses' \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d @- <<JSON | jq -r '.output_text // .output // .'
{
  "model": "$OPENAI_SKILL_MODEL",
  "tools": [
    {
      "type": "shell",
      "environment": {
        "type": "container_auto",
        "skills": [ $SKILL_REF ]
      }
    }
  ],
  "input": "Use the http-header-audit skill to grade these HTTP response headers, then give me the letter grade and the two weakest headers: {\"Strict-Transport-Security\":\"max-age=0\",\"Content-Security-Policy\":\"default-src 'self'; script-src 'unsafe-inline'\",\"Server\":\"nginx/1.18.0\"}"
}
JSON
