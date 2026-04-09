# Hacking Bot (teaser)

A tiny AI pentesting bot in ~100 lines, built on top of MCP. This is a
**teaser**, not a product: the point is to show how little wiring it
takes to turn "a sandboxed shell" plus "a reasoning scratchpad" into
something that looks and behaves like a very junior pentesting assistant,
and then to leave the hard parts (scope control, tool selection, result
triage, reporting) as homework.

## Architecture

```
  +---------------------+         +-----------------------+
  |  OA_pentester.py    |         |  Docker container     |
  |  (openai-agents)    |         |  ubuntu-node-python   |
  |                     |         |                       |
  |  Agent              |  MCP    |  supergateway         |
  |  ├─ kali-box  ──────┼────────▶│   └─ desktop-commander|
  |  └─ sequential-     |  HTTP   |      (stdio → HTTP)   |
  |     thinking (stdio)|         |                       |
  +---------────────────+         +-----------------------+
           │
           └─ MCP stdio
              npx @modelcontextprotocol/server-sequential-thinking
```

Two MCP servers feed the agent:

1. **kali-box**: a throwaway Ubuntu container with `desktop-commander`
   behind `supergateway`, exposed as streamable HTTP on
   `http://127.0.0.1:8000/mcp/`. This is the shell. The agent can
   install missing scanners with apt, run them in the background, read
   files in /tmp, and clean up.
2. **sequential-thinking**: the reference
   `@modelcontextprotocol/server-sequential-thinking` server, running
   locally over stdio. It exposes a single `sequentialthinking` tool
   the model uses as a revisable scratchpad: it writes thoughts, marks
   some as revisions of earlier ones, branches when it explores an
   alternative, and marks a final thought when it is done thinking.
   Wiring this server in tends to make multi-step tool use much more
   coherent; the model is forced to name its plan before it runs
   anything, and it revisits the plan when findings change.

## Getting started

Build the hacking container:

```bash
docker build -t ubuntu-node-python .
```

Start it as a remote MCP server:

```bash
docker run -p 8000:8000 \
    -v ./traces:/tmp \
    -d ubuntu-node-python \
    npx -y supergateway --outputTransport streamableHttp \
        --stdio "npx -y @wonderwhy-er/desktop-commander@latest"
```

Interactive shell (if you want to peek inside):

```bash
docker run -it ubuntu-node-python bash
```

## Run a scan

```bash
python3 ./OA_pentester.py
```

The script plans against a single authorized target, asks the
sequential-thinking server for a plan, uses kali-box to install nikto
if needed, runs it in the background, polls, and summarizes the top
findings. Conversation history is kept in a local SQLite session
("hackingbot") so you can re-run and continue the same engagement.

## Configuring VS Code to talk to the same MCP server

Create `.vscode/mcp.json` so you can poke at the container's tools
directly from your editor:

```bash
mkdir -p .vscode
```

```json
{
    "servers": {
        "kali-box": {
            "url": "http://127.0.0.1:8000/mcp/",
            "type": "http"
        }
    },
    "inputs": []
}
```

## Where to take this next

The whole script is deliberately short. Obvious next steps, in rough
order of payoff:

1. **Scope enforcement**: add a deny-list of hostnames and refuse
   before running any network command that targets something outside
   the list. Right now the scope lives in the prompt, which is the
   cheapest place for it to fail.
2. **Tool selection**: give the agent a short menu of scanners with a
   description of when each is appropriate, instead of assuming nikto.
   Couple that with sequential-thinking to force a "which tool, why"
   step.
3. **Result triage**: teach the agent to grep findings for signatures
   worth following up and to save a machine-readable artifact
   alongside the raw scan output.
4. **Reporting**: plug in the `docx` or `pdf` skills to turn the
   conclusions into a real report rather than a paragraph of text. The
   `reporting/` subfolder here contains example outputs from earlier
   runs; use them as reference for the format you want.
5. **Observability**: wrap every tool call in the openai-agents tracer
   (already done via `trace(...)`) and add a mitmproxy in front of the
   MCP server to see the JSON-RPC on the wire. Pair with lab071 for
   Inspector.
6. **Safety rail**: put the destructive commands behind a human-
   confirmation gate. The agent is allowed to plan anything, but shell
   execution of anything that writes off-box has to be approved.

Each of those is about a half-day of work and each one is more
interesting than the original "run nikto and print the output". The
point of the teaser is to show you that the wiring is the easy part,
and that where you spend your time is on the judgment layer around
the tools.

## Security caveats

This bot has no scope controls beyond the system prompt, no command
allowlist, and full root inside the container. Do not run it against
anything you do not own. Treat it as a lab exercise only. The section
at the bottom of [../README.md](../README.md) (lab070) covers the
broader MCP security risks that apply here: tool shadowing, indirect
prompt injection through scan output, sampling abuse, confused deputy
at the container boundary, and supply-chain risk on every `npx -y`
line in the Dockerfile.
