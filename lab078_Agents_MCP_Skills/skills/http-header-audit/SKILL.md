---
name: http-header-audit
description: Audit a website's HTTP security response headers (HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy) and report a graded findings table. Use when asked to check a URL's security headers.
---

# HTTP security-header audit

## When to use
The user gives you a URL (or asks you to check a site) and wants its HTTP
security headers assessed.

## Procedure
Do NOT eyeball the headers and improvise. Follow these steps.

1. Fetch the response with the MCP tool `http_get(url)`. It returns
   `{status, headers, body_snippet}`. You only need `headers`.

2. Grade the headers deterministically with the bundled script instead of
   judging them yourself. Call:

       run_skill_script("http-header-audit", "scripts/audit_headers.py",
                        stdin_text=<the headers object as JSON>)

   Pass a JSON object. Either the raw `{"Strict-Transport-Security": "...",
   ...}` map, or `{"headers": { ... }}`; the script accepts both. It prints a
   per-header table (present/quality, weight) and an overall letter grade and
   score. Report those numbers, do not invent your own.

3. If you need to explain WHY a header matters or what "good" looks like for
   it, read the rubric with
   `read_reference("http-header-audit", "grading.md")`. Do not recite header
   advice from memory; the reference is the source of truth for this skill.

4. Summarise: the grade and score, then the two or three headers that most
   hurt the score, each with the one-line fix from the rubric. If the user
   asked for a report or to record the finding, format it with the
   `incident-note` skill (read_skill("incident-note")).

## Notes
The grader is deterministic and offline: it only reads the headers you pass
it. The network fetch is the MCP tool's job, the grading is the script's job,
the knowledge is the reference's job. Keep them separate.
