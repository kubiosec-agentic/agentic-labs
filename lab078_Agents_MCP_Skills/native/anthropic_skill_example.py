"""
Exercise 4b: the same skill, uploaded to Anthropic and run via the SDK.

Anthropic's skills mirror OpenAI's hosted mode: upload the SKILL.md folder,
reference it by id, and the scripts run in Anthropic's sandboxed container
(the code execution tool). This is the third point on the spectrum:

  agent_01..03           local execution, your loop, model-agnostic (the lab)
  openai_uploaded_skill  uploaded, runs in OpenAI's sandbox (shell tool)
  this file              uploaded, runs in Anthropic's sandbox (code exec tool)

Same SKILL.md folder in all three. What changes is where the code runs, which
is where the blast radius lives.

Requirements:
  pip install anthropic
  export ANTHROPIC_API_KEY=...
  export ANTHROPIC_SKILL_MODEL=<a current model that supports code execution>
    (the doc example model strings move; do not trust a hardcoded one, read
     the current one from
     https://platform.claude.com/docs/en/build-with-claude/skills-guide)

Endpoints/shape verified against the Anthropic skills guide and the Skill
Management API reference:
  client.skills.create(files=files_from_dir(<dir>))   -> POST /v1/skills
  messages.create(container={"skills":[{type,skill_id,version}]},
                  tools=[{"type":"code_execution_20250825","name":"code_execution"}])
The Skills API is GA: no beta header.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
SKILL_DIR = HERE.parent / "skills" / "http-header-audit"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("export ANTHROPIC_API_KEY=... first")
    model = os.environ.get("ANTHROPIC_SKILL_MODEL")
    if not model:
        sys.exit("set ANTHROPIC_SKILL_MODEL to a current model that supports the code execution tool")

    import anthropic
    from anthropic.lib import files_from_dir

    client = anthropic.Anthropic()

    # 1. Upload skills/http-header-audit as a custom skill. files_from_dir walks
    #    the folder and builds the multipart upload; SKILL.md must be at its root.
    print(f"Uploading {SKILL_DIR.name} ...")
    skill = client.skills.create(files=files_from_dir(str(SKILL_DIR)))
    skill_id = skill.id                       # 'skill_...'
    print(f"skill_id = {skill_id}, latest_version = {getattr(skill, 'latest_version_id', '?')}")

    # 2. Run it. Headers are handed in inline, so the sandbox needs no network:
    #    the uploaded script grades what the message provides.
    headers = (
        '{"Strict-Transport-Security":"max-age=0",'
        '"Content-Security-Policy":"default-src \'self\'; script-src \'unsafe-inline\'",'
        '"Server":"nginx/1.18.0"}'
    )
    resp = client.messages.create(
        model=model,
        max_tokens=2048,
        container={"skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]},
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        messages=[{
            "role": "user",
            "content": (
                "Use the http-header-audit skill to grade these HTTP response headers, "
                f"then give me the letter grade and the two weakest headers. Headers: {headers}"
            ),
        }],
    )

    print("\n--- response ---")
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            print(block.text)

    print(
        "\nNote: the skill's script ran in Anthropic's sandbox (code execution), "
        "not on your machine. To use a built-in skill instead of uploading, pass "
        '{"type":"anthropic","skill_id":"pptx","version":"latest"} and skip step 1. '
        "Pin the version in production: an unpinned 'latest' is a rug-pull surface."
    )


if __name__ == "__main__":
    main()
