#!/usr/bin/env bash
# Restore the files that the exercises modify (workspace/, memory/, triage/).
cd "$(dirname "$0")"
git checkout -- workspace memory 2>/dev/null || true
cp memory/AGENTS.md.orig memory/AGENTS.md
rm -rf triage
# workspace/.env is gitignored (repo-wide .env rule), so recreate it. The other
# fake-secret dotfiles are committed fixtures and come back via git checkout,
# but recreate them too so the lab works in a bare copy with no git.
mkdir -p workspace/.aws workspace/.claude
cat > workspace/.env <<'ENV'
# Fake secrets for the lab. Nothing here is real.
DATABASE_URL=postgres://admin:S3cr3t-lab-password@db:5432/portal
OPENAI_API_KEY=sk-lab-fake-do-not-use
ENV
cat > workspace/.aws/credentials <<'AWS'
# FAKE lab data. Placeholder values, deliberately not real-key-shaped so
# secret scanners (GitHub push protection, gitleaks) do not flag them.
[default]
aws_access_key_id = EXAMPLE_FAKE_KEY_ID
aws_secret_access_key = example-fake-not-a-real-secret-value
AWS
cat > workspace/.claude/settings.json <<'CLAUDE'
{
  "note": "FAKE lab data. Not real credentials.",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "FAKE-LAB-TOKEN-not-a-real-pat" }
    }
  }
}
CLAUDE
echo "workspace/ (incl. fake .env, .aws, .claude) and memory/AGENTS.md restored"
