#!/usr/bin/env python3
"""
Deterministic grader for HTTP security response headers.

Reads a JSON object on stdin. Accepts either the raw header map
    {"Strict-Transport-Security": "max-age=63072000; includeSubDomains", ...}
or a wrapper
    {"headers": { ... }}

Prints a per-header table and an overall score / letter grade, then exits 0.
Pure function of its input: no network, no files. That is what makes it
testable and what lets the MCP server own the actual fetch.

Standalone use, for the lab and for tests:
    echo '{"Strict-Transport-Security":"max-age=31536000"}' | python3 audit_headers.py
"""

import json
import sys

# Each check: weight, and a grader(value) -> (points_fraction, note).
# Header lookups are case-insensitive (done in main()).


def _hsts(v):
    if v is None:
        return 0.0, "missing: no HTTP Strict Transport Security"
    maxage = 0
    for part in v.split(";"):
        part = part.strip().lower()
        if part.startswith("max-age="):
            try:
                maxage = int(part.split("=", 1)[1])
            except ValueError:
                maxage = 0
    if maxage == 0:
        return 0.2, "present but max-age=0 (disables HSTS)"
    if maxage < 15552000:  # 180 days
        return 0.6, f"present but weak max-age ({maxage}s < 180d)"
    note = "good"
    if "includesubdomains" not in v.lower():
        note = "good, but no includeSubDomains"
    return 1.0, note


def _csp(v):
    if v is None:
        return 0.0, "missing: no Content-Security-Policy"
    low = v.lower()
    if "unsafe-inline" in low or "unsafe-eval" in low:
        return 0.5, "present but allows unsafe-inline/unsafe-eval"
    if "default-src" not in low and "script-src" not in low:
        return 0.6, "present but no default-src/script-src"
    return 1.0, "good"


def _nosniff(v):
    if v is None:
        return 0.0, "missing: no X-Content-Type-Options"
    return (1.0, "good") if v.strip().lower() == "nosniff" else (0.3, f"unexpected value: {v!r}")


def _frame(v):
    if v is None:
        return 0.0, "missing: no X-Frame-Options (clickjacking)"
    val = v.strip().lower()
    if val in ("deny", "sameorigin"):
        return 1.0, "good"
    return 0.4, f"weak/allowall value: {v!r}"


def _referrer(v):
    if v is None:
        return 0.0, "missing: no Referrer-Policy"
    strong = {"no-referrer", "strict-origin", "strict-origin-when-cross-origin", "same-origin"}
    return (1.0, "good") if v.strip().lower() in strong else (0.5, f"leaky value: {v!r}")


def _permissions(v):
    if v is None:
        return 0.0, "missing: no Permissions-Policy"
    return 1.0, "good"


CHECKS = [
    ("Strict-Transport-Security", 25, _hsts),
    ("Content-Security-Policy", 25, _csp),
    ("X-Content-Type-Options", 15, _nosniff),
    ("X-Frame-Options", 15, _frame),
    ("Referrer-Policy", 10, _referrer),
    ("Permissions-Policy", 10, _permissions),
]

# Headers whose mere presence leaks stack detail. Not scored, flagged.
DISCLOSURE = ["Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version"]


def grade(headers: dict) -> dict:
    # case-insensitive lookup
    ci = {k.lower(): v for k, v in headers.items()}
    rows = []
    earned = 0.0
    total = 0
    for name, weight, fn in CHECKS:
        frac, note = fn(ci.get(name.lower()))
        rows.append({"header": name, "weight": weight, "score": round(frac * weight, 1), "note": note})
        earned += frac * weight
        total += weight
    disclosures = [{"header": h, "value": ci[h.lower()]} for h in DISCLOSURE if h.lower() in ci]
    pct = round(100 * earned / total, 1) if total else 0.0
    letter = "A" if pct >= 90 else "B" if pct >= 75 else "C" if pct >= 60 else "D" if pct >= 40 else "F"
    return {"rows": rows, "disclosures": disclosures, "score": pct, "grade": letter}


def render(result: dict) -> str:
    lines = ["HTTP security-header audit", "=" * 34]
    lines.append(f"{'Header':<28}{'Score':>7}  Note")
    lines.append("-" * 60)
    for r in result["rows"]:
        lines.append(f"{r['header']:<28}{r['score']:>4}/{r['weight']:<2}  {r['note']}")
    lines.append("-" * 60)
    lines.append(f"Overall: {result['grade']}  ({result['score']}/100)")
    if result["disclosures"]:
        lines.append("")
        lines.append("Information disclosure (not scored, but tighten):")
        for d in result["disclosures"]:
            lines.append(f"  {d['header']}: {d['value']}")
    return "\n".join(lines)


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        print("error: no JSON on stdin", file=sys.stderr)
        return 2
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON on stdin: {e}", file=sys.stderr)
        return 2
    headers = data.get("headers", data) if isinstance(data, dict) else {}
    if not isinstance(headers, dict):
        print("error: expected a headers object", file=sys.stderr)
        return 2
    print(render(grade(headers)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
