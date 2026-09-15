---
name: incident-note
description: Format a security finding as a standard incident note (title, severity, evidence, recommendation). Use when asked to record or report a finding.
---

# Incident note

## When to use
The user asks you to record, log, or report a security finding, or another
skill hands you findings to write up.

## Procedure
Produce exactly these fields, in this order, as markdown:

- **Title**: one line, what and where.
- **Severity**: one of info / low / medium / high / critical. Justify in half a sentence.
- **Evidence**: the concrete observation (a header value, a status code, a line from output). Quote it. Do not paraphrase away the specifics.
- **Impact**: what an attacker gains, in one or two sentences. No speculation beyond the evidence.
- **Recommendation**: the single most important fix, actionable, one or two sentences.

## Style
Terse. No preamble, no "as an AI". If severity is info, say so plainly rather
than inflating it. One note per finding; if given several, emit several notes.
