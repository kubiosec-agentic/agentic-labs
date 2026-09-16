# HTTP security-header rubric

The reference the `http-header-audit` skill consults when it needs to explain
a header or say what "good" looks like. The grader script encodes this; this
file is the human-readable source of truth behind the scores.

## Strict-Transport-Security (HSTS), weight 25
Forces browsers to use HTTPS for the domain, defeating SSL-strip and
protocol-downgrade attacks after the first visit.
- Good: `max-age=63072000; includeSubDomains` (2 years). `preload` is a bonus.
- Weak: `max-age` under ~180 days, or no `includeSubDomains`.
- Broken: `max-age=0` (explicitly turns HSTS off).
- Fix: `Strict-Transport-Security: max-age=63072000; includeSubDomains`.

## Content-Security-Policy (CSP), weight 25
The strongest defence against cross-site scripting: restricts where scripts,
styles, frames and connections may come from.
- Good: a policy with an explicit `default-src`/`script-src` and no
  `unsafe-inline` or `unsafe-eval`.
- Weak: present but allows `unsafe-inline`/`unsafe-eval` (most of the XSS
  protection is gone), or has no `default-src`/`script-src`.
- Fix: start from `default-src 'self'` and add sources explicitly; move inline
  scripts to files or use nonces/hashes.

## X-Content-Type-Options, weight 15
Stops MIME sniffing, where the browser second-guesses Content-Type and may run
a file as script.
- Good: exactly `nosniff`.
- Fix: `X-Content-Type-Options: nosniff`.

## X-Frame-Options, weight 15
Anti-clickjacking: controls whether the page can be framed. (CSP
`frame-ancestors` is the modern equivalent; both are accepted in practice.)
- Good: `DENY` or `SAMEORIGIN`.
- Fix: `X-Frame-Options: SAMEORIGIN`, or `Content-Security-Policy:
  frame-ancestors 'self'`.

## Referrer-Policy, weight 10
Limits how much of the URL leaks to third parties in the `Referer` header.
- Good: `no-referrer`, `same-origin`, `strict-origin`, or
  `strict-origin-when-cross-origin`.
- Leaky: `unsafe-url` or unset.
- Fix: `Referrer-Policy: strict-origin-when-cross-origin`.

## Permissions-Policy, weight 10
Turns off powerful browser features (camera, microphone, geolocation, etc.)
the site does not use, shrinking the attack surface.
- Good: present and restrictive, e.g. `geolocation=(), camera=(), microphone=()`.
- Fix: enumerate the features you use and deny the rest.

## Information disclosure (flagged, not scored)
`Server`, `X-Powered-By`, `X-AspNet-Version` and friends advertise the stack
and version, which helps an attacker pick exploits. Not a vulnerability by
itself, but free reconnaissance you can remove.
- Fix: suppress or genericise these at the server/proxy.

## Grading
Weighted sum out of 100. Letters: A >= 90, B >= 75, C >= 60, D >= 40, else F.
