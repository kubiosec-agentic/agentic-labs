![MCP](https://img.shields.io/badge/MCP-purple) ![Inspector](https://img.shields.io/badge/Inspector-orange) ![Debugging](https://img.shields.io/badge/Debugging-yellow) ![Security](https://img.shields.io/badge/Security-red)

# LAB071: MCP Inspector and traffic debugging

## Introduction

This lab is the debugging companion to lab070. Once you have an MCP
server running, you need ways to look at it from the outside: what tools
does it actually expose, what do the JSON-RPC messages look like on the
wire, and where can you intercept them to understand (or attack) an
agentic flow. Two things are worth knowing well:

1. **MCP Inspector**, the official interactive UI for poking at an MCP
   server. It speaks every transport, lets you list tools, call them
   manually, and walk through prompts and resources.
2. The **mcp-firewall/mcp-debugging** companion repo, a curated set of
   worked examples for debugging MCP traffic with Inspector, mitmproxy,
   Wireshark, and Stratoshark. It covers stdio, SSE, SSE+proxy, and
   streamable HTTP side-by-side so you can see the wire differences
   between transports.

You should go through lab070 first. This lab assumes you already have
a working fastmcp server in your pocket and want to see what it looks
like from outside the Python process.

## Remote lab environment

All commands in this lab run **on the AWS box** over SSH. The MCP
Inspector serves a web UI that you open **in the browser on your
laptop**, reached through SSH port forwarding.

Inspector uses two ports: **6274** (proxy) and **5173** (UI). Both are
included in the main README's SSH command (see the
[port table](../README.md#-getting-access-to-the-lab-via-ssh)). If you
connected with that command, the tunnels are already in place and
`http://localhost:6274` in your laptop browser reaches Inspector on the
AWS box.

## Prerequisites

- Node.js 18+ with `npx` on PATH (already installed by `setup.sh`).
- A working lab070 environment, or any MCP server running at
  `http://127.0.0.1:8000/mcp` on the AWS box.
- Optional but recommended: mitmproxy, Wireshark, and
  [Stratoshark](https://stratoshark.org) for deep traffic analysis.

## Setup

No venv needed; Inspector runs via npx. Pin a version if you want
reproducibility across the training cohort:

```bash
npx -y @modelcontextprotocol/inspector@latest --help
```

## 1. MCP Inspector: interactive UI

Start your lab070 streamable HTTP server in one SSH terminal:

```bash
cd ../lab070_MCP
python3 server_streamable.py
```

Launch Inspector in a second SSH terminal:

```bash
npx -y @modelcontextprotocol/inspector
```

Inspector prints two URLs on startup. Open your **laptop browser** at
[http://localhost:6274](http://localhost:6274) (this reaches the AWS box
through the SSH tunnel).

In the connection panel, choose **Streamable HTTP** as the transport and
enter `http://127.0.0.1:8000/mcp` as the server URL. Click Connect.

> The server URL points at 127.0.0.1 from Inspector's perspective,
> which is correct: Inspector runs on the AWS box and talks to the MCP
> server on the same machine. Your laptop never contacts port 8000
> directly; it only tunnels 6274 and 5173.

Things to try in the UI:

- Open the **Tools** tab and list the tools. Confirm the names and
  descriptions match what `server_streamable.py` declares.
- Click a tool (e.g. `add`) and invoke it with sample arguments.
  Inspector shows you the raw JSON-RPC request and response, which is
  the quickest way to learn the wire format.
- Open the **Notifications** panel and watch what the server emits
  during a call. Log messages from `ctx.info/warning/error` show up
  here.
- Swap in the sampling server from lab070
  (`sampling/server_sampling_http.py`) and invoke `analyze_sentiment`.
  Inspector surfaces the `sampling/createMessage` request so you can
  see sampling flow from the server side without writing any client
  code.

## 2. MCP Inspector: CLI mode

Inspector also ships a scriptable CLI mode, which is the right tool
for smoke tests and CI. Run these in an SSH terminal on the AWS box:

```bash
# List tools
npx -y @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp \
    --transport http --method tools/list
```

```bash
# Call a tool
npx -y @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp \
    --transport http --method tools/call \
    --tool-name add --tool-arg a=7 --tool-arg b=22
```

```bash
# List prompts and resources
npx -y @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp \
    --transport http --method prompts/list
```

Use this mode to assert on your server's behavior from a shell script
without standing up a real agent.

## 3. Inspecting stdio servers

Inspector speaks stdio too. Point it at an `npx` launcher or any
command line that starts an MCP server on stdin/stdout. Example using
the filesystem server:

```bash
npx -y @modelcontextprotocol/inspector \
    npx -y @modelcontextprotocol/server-filesystem /tmp
```

The UI will launch the child process, speak JSON-RPC over its
stdin/stdout, and give you the same tool/prompt/resource tabs.

## 4. mcp-firewall/mcp-debugging: the reference

For anything more than casual poking, work through the
[`mcp-firewall/mcp-debugging`](https://github.com/mcp-firewall/mcp-debugging)
repo. It is a focused, example-driven reference for debugging MCP
traffic, covering:

- **stdio debugging**: attaching strace / Process Monitor to see
  JSON-RPC frames on the pipes.
- **SSE debugging**: listening on `/sse` and `/messages` endpoints and
  watching the session token handshake.
- **SSE with a proxy in the middle**: inserting mitmproxy between client
  and server to rewrite messages in flight. This is where you learn how
  the session actually reconstructs after a redirect.
- **Streamable HTTP debugging**: the current default transport, same
  idea, different framing.
- **MCP Inspector integration**: how to combine Inspector with a proxy
  so you get the UI and the packet capture at once.
- **Wireshark / Stratoshark**: using packet capture tooling to study
  MCP traffic with proper protocol dissectors. The repo includes pcap
  captures you can replay offline, which is the cleanest way to learn
  the transport framing without standing up any infrastructure.

Clone the repo on the AWS box and follow the walkthroughs after you
have finished the Inspector sections above:

```bash
git clone https://github.com/mcp-firewall/mcp-debugging
cd mcp-debugging
```

The repo is structured as a sequence of worked examples, not a single
script, so treat it as a reading exercise. For each transport, the
goal is to be able to answer: where does the session start, how is
state kept between calls, where can a middleman sit, and what does a
tampered message look like on the wire.

## 5. Putting it together: debug a shadowing attack

Combine lab070 section 3 with Inspector to make the attack visible.
You need three SSH terminals on the AWS box:

**Terminal A**: start the real server on port 8000.

```bash
cd ../lab070_MCP
python3 server_streamable.py
```

**Terminal B**: start the rogue server on port 8001.

```bash
cd ../lab070_MCP
python3 server_rogue_streamable.py
```

**Terminal C**: launch Inspector.

```bash
npx -y @modelcontextprotocol/inspector
```

Now, in your laptop browser at `http://localhost:6274`:

1. Connect to `http://127.0.0.1:8000/mcp` (the real server). List the
   tools and note names and descriptions.
2. Disconnect. Connect to `http://127.0.0.1:8001/mcp` (the rogue
   server). List the tools and note how the rogue server's names and
   descriptions overlap with the real one.
3. Then run `python3 mcp_03_streamable.py` from lab070 with the agent
   configured to both servers. Compare which tools the agent actually
   calls against the metadata you saw in Inspector.

This gives you the attacker's view (Inspector), the defender's view
(tool metadata audit), and the runtime view (the agent's trace) at the
same time, which is the minimum you want for root-causing a shadowing
incident in a real system.

## Cleanup

Inspector runs via npx and leaves no persistent state. Kill the
terminal and you are done. If you ran stdio servers through it, they
exit with the inspector process.

## What to take away

- Inspector is the right first stop for any "is my MCP server exposing
  what I think it is" question, in dev and in production.
- CLI mode is the right thing to wire into CI: smoke-test tool listing
  and a couple of representative tool calls on every deploy.
- For wire-level debugging and traffic forensics, use the
  `mcp-firewall/mcp-debugging` walkthroughs; do not try to learn SSE
  reconnection semantics by reading the spec.
- Every debugging tool in this lab is also an attacker tool. If you
  can sit between client and server with mitmproxy to learn, an
  attacker can sit in the same place to rewrite. Think of the
  debugging setup and the threat model as the same diagram.

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
