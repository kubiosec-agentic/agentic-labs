![MCP](https://img.shields.io/badge/MCP-purple) ![fastmcp](https://img.shields.io/badge/fastmcp-4.x-green) ![Stateless](https://img.shields.io/badge/Stateless-blue) ![Security](https://img.shields.io/badge/Security-red) ![Python](https://img.shields.io/badge/Python-blue)

# LAB073: Stateless MCP (and the price of a moving standard)

## Introduction

In lab070 you ran MCP servers on the standalone `fastmcp` library, pinned
to `3.4.7`. This lab runs the **fastmcp 4.x** generation, which adopts the
`2026-07-28` MCP spec revision. That revision made MCP **stateless-first**:
the transport no longer keeps a per-connection session for you, and a
fresh client negotiates a sessionless protocol era by default.

The lab has two jobs at once.

First, the **architecture**: what "stateless" actually means for an MCP
server (pure functions, no memory between calls), why it matters (a
stateless server scales to N identical replicas behind a load balancer
with no sticky sessions), and how to keep state when you need it without a
transport session (the explicit-handle pattern, where state travels as a
tool argument).

Second, and this is why the lab sits right after lab070/lab071, it is the
course's sharpest **"standards move fast"** case study. You will take the
*exact same server code* from lab070, run it under fastmcp 4.x, and watch
part of it keep working and part of it break. Nothing in the server changed.
The ground under it did. That is not a hypothetical about supply-chain risk,
it is a reproducible one, and it is why lab070 pins `fastmcp==3.4.7`.

> This lab uses fastmcp 4.x on purpose and keeps its own virtual environment,
> separate from lab070's 3.4.7 venv. The two live side by side. Do lab070
> first so you have the servers and the mental model.

## Set up your environment

This lab gets its own venv so fastmcp 4.x does not disturb lab070's pinned
3.4.7.

```bash
export OPENAI_API_KEY="xxxxxxxxx"
```
```bash
./lab_setup.sh
```
```bash
source .lab073/bin/activate
```

Confirm you are on the 4.x generation:

```bash
python3 -c "import fastmcp; print(fastmcp.__version__)"
```

You should see a `4.x` version. `requirements.txt` requests `fastmcp>=4,<5`:
the `<5` is deliberate, this whole lab is about 4.x-era behaviour and we do
not want a future 5.x to silently change it again. (That cap is itself the
lesson, see the meta-note at the end.)

## Lab instructions

### 1. Same server, new runtime

Take lab070's streamable server, unchanged, and run it under this venv
(fastmcp 4.x).

**Terminal 1 (server)** with `.lab073` activated:

```bash
cd ../lab070_MCP
python3 server_streamable.py
```

**Terminal 2 (client)** activate the same venv and hit it with this lab's client:

```bash
cd ../lab073_MCP_Stateless
source .lab073/bin/activate
python3 client_demo.py --url http://127.0.0.1:8000/mcp
```

Expected: the tools list and a working `add`.

```
Connecting to http://127.0.0.1:8000/mcp  (mode=auto)
Negotiated protocol era: None
Tools: ['add', 'get_secret_word', 'get_current_weather']
add(7, 5) -> {'result': 12}
```

The pure tools still work on the new runtime. Upgrading the package did not
break them, because they never depended on anything the spec revision
removed. Note the client connected in the default `mode=auto`, which
negotiates the modern sessionless era (that is why the protocol-era field
reads `None` rather than a dated string, there is no legacy session
handshake to report). Stop the server with `Ctrl+C`.

### 2. Where it breaks: sampling

Now run lab070's **sampling** server, also unchanged, under fastmcp 4.x.

**Terminal 1 (server):**

```bash
cd ../lab070_MCP
python3 sampling/server_sampling_http.py
```

**Terminal 2 (probe)** in this venv, trigger its `analyze_sentiment` tool:

```bash
cd ../lab073_MCP_Stateless
python3 sampling_probe.py http://127.0.0.1:8000/mcp
```

Expected:

```
Sampling FAILED (expected on fastmcp 4.x):
  ToolError: Error calling tool 'analyze_sentiment': 'Context' object has no attribute 'sample'
```

The tool body calls `await ctx.sample(...)`, the server-initiated
back-channel where a tool asks the client to run an LLM call. **fastmcp 4.x
removed `ctx.sample` from the server `Context` entirely** (the sessionless
era has no server-initiated back-channel). The server code is byte-for-byte
the same as in lab070. It ran fine on 3.4.7 and it raises on 4.x.

This is the concrete reason lab070 pins `fastmcp==3.4.7`: its sampling
examples (lab070 section 5) simply do not exist on the 4.x API. Here is the
minimal compatibility picture, enough to see the problem:

| Capability | fastmcp 3.4.7 | fastmcp 4.x (2026-07-28 era) |
|---|---|---|
| Pure tools (`add`, weather, math) | works | works |
| `ctx.sample(...)` server-side sampling | available | **removed** (`AttributeError`) |
| Client `mode=` (auto / legacy) | not present | new; `auto` = sessionless |
| Default HTTP session | stateful, per-connection session | client negotiates sessionless |
| `InitializeResult.protocolVersion` | that name | renamed to `protocol_version` |

None of these are bugs. They are a standard and a library moving between
major versions. The point of the row that says "removed" is that the same
code path is present in one generation and gone in the next, with no change
on your side.

### 3. A genuinely stateless server

`stateless_server.py` is what "stateless" means in the spec's sense: every
tool is a pure function of its arguments, with no memory between calls.

**Terminal 1 (server):**

```bash
python3 stateless_server.py
```

**Terminal 2 (client)** same venv:

```bash
python3 client_demo.py --url http://127.0.0.1:8100/mcp
```

```
Tools: ['add', 'multiply', 'celsius_to_fahrenheit']
add(7, 5) -> {'result': 12.0}
celsius_to_fahrenheit(21) -> {'celsius': 21.0, 'fahrenheit': 69.8}
```

Because nothing is remembered, you could run ten copies of this server
behind a load balancer and it would not matter which replica served which
request. No sticky sessions, no shared cache, no coordination. That is the
deployment shape the sessionless spec is built for.

### 4. State without sessions

Real agents often need state. The stateless spec does not forbid that, it
moves the state out of the hidden transport session and into explicit tool
arguments. `stateful_server.py` shows the wrong way and the right way in
one server.

**Terminal 1 (server):**

```bash
python3 stateful_server.py
```

**The anti-pattern (`increment`)** keeps a process-global counter. It looks
fine on one process, but each replica has its own copy, so under a load
balancer the numbers are meaningless.

**The pattern (`open_cart` / `add_item` / `view_cart`)** is the
explicit-handle approach: `open_cart()` returns an unguessable id, and the
client passes that id back as an argument on every follow-up call. The
server looks the state up by id. Here the store is an in-memory dict; in
production it is Redis or Postgres, shared by every replica, so any replica
can serve any request.

**Terminal 2 (client)** same venv:

```bash
python3 - <<'PY'
import asyncio
from fastmcp import Client
async def m():
    async with Client("http://127.0.0.1:8101/mcp") as c:
        cid = (await c.call_tool("open_cart", {})).data["cart_id"]
        print("cart:", cid)
        await c.call_tool("add_item", {"cart_id": cid, "item": "eBPF book"})
        r = await c.call_tool("add_item", {"cart_id": cid, "item": "Cilium sticker"})
        print("items:", r.data["items"])
asyncio.run(m())
PY
```

Notice what just happened on the wire: the cart id, which is the thing that
grants access to that state, travelled as an ordinary tool argument. Hold
that thought for the security section.

### 5. Visualize the difference with mitmproxy

lab070 section 7 and lab071 taught you to put mitmproxy in front of an MCP
server. Do it here to *see* the session appear and disappear depending on
which era the client negotiates. This exercise uses **three terminals**:
Terminal 1 the server, Terminal 2 the client, Terminal 3 mitmproxy.

Use lab070's `server_streamable.py` as the target. It binds `0.0.0.0:8000`,
which the mitmproxy Docker container can reach; `stateless_server.py` binds
`127.0.0.1` only, so the container could not reach it. The mode/session
behaviour we are inspecting is a property of the client, so the choice of
server does not change what you see.

**Terminal 1 (server)** with `.lab073` activated (fastmcp 4.x):

```bash
cd ../lab070_MCP
python3 server_streamable.py
```

**Terminal 3 (mitmproxy).** mitmproxy runs in Docker, so `127.0.0.1` inside
the container is the container itself, not the host. Set the host's LAN IP in
*this* terminal, then start the reverse proxy in front of the server (listens
on 8080, forwards to the server on 8000; mitmweb UI on 8081):

```bash
# Linux (e.g. the Ubuntu lab box):
export HOST_IP=$(hostname -I | awk '{print $1}')
# macOS (Wi-Fi); use en0 for Ethernet or adjust the interface:
# export HOST_IP=$(ipconfig getifaddr en0)
echo "host ip: $HOST_IP"   # must be non-empty

docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 8081:8081 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --set block_global=false \
        --mode reverse:http://${HOST_IP}:8000@8080
```

> If `HOST_IP` is empty the container cannot reach the server and the proxy
> fails to connect. Set it in this terminal before running Docker.

**Terminal 2 (client)** in the lab073 venv, hit the server *through the proxy*
once in each mode:

```bash
cd ../lab073_MCP_Stateless
python3 client_demo.py --url http://127.0.0.1:8080/mcp --mode legacy
python3 client_demo.py --url http://127.0.0.1:8080/mcp --mode auto
```

Now open the mitmweb UI at `http://127.0.0.1:8081`, find the `initialize`
request/response for each run, and compare:

- **`--mode legacy`**: the client negotiates the older era (its output shows
  `protocol_version` = `2025-11-25`), and the server's response carries an
  **`mcp-session-id`** header. That id is the session; subsequent requests
  are tied to it.
- **`--mode auto`**: the client negotiates the modern sessionless era. The
  handshake differs, there is no `mcp-session-id` header, and the client's
  protocol-era field reads `None` because there is no legacy session to
  report.

Seeing it on the wire is the point. The word "stateless" stops being an
abstraction once you have watched the `mcp-session-id` header be there in
one mode and not the other. Stop the server (`Ctrl+C` in Terminal 1) and the
proxy (`Ctrl+C` in Terminal 3) when done.

### 6. The full flow: an OpenAI Agents SDK agent through mitmproxy

Exercise 5 used the bare `fastmcp` client, so mitmproxy only saw the MCP leg.
Here `agent_demo.py` is a real **OpenAI Agents SDK** agent: it reasons with the
model *and* calls the stateless server's MCP tools. Routed through mitmproxy you
see **both legs of an agentic call** on the wire:

- agent to OpenAI API: the model deciding which tool to call, then composing
  the answer from the tool results;
- agent to MCP server: `initialize`, `tools/list`, and `tools/call` for `add`
  and `celsius_to_fahrenheit`.

This needs a real `OPENAI_API_KEY` (the model call is real) and the
`openai-agents` package (already in this lab's `requirements.txt`). It uses
**three terminals**: Terminal 1 the server, Terminal 2 the agent, Terminal 3
mitmproxy. The proxy runs two reverse modes at once, one per leg.

**Terminal 1 (server)** bind all interfaces so the Docker proxy can reach it:

```bash
python3 stateless_server.py --host 0.0.0.0
```

**Terminal 3 (mitmproxy)** one reverse mode for OpenAI (8080) and one for the
MCP server (8089); mitmweb UI on 8081:

```bash
# Linux (e.g. the Ubuntu lab box):
export HOST_IP=$(hostname -I | awk '{print $1}')
# macOS (Wi-Fi); use en0 for Ethernet or adjust the interface:
# export HOST_IP=$(ipconfig getifaddr en0)
echo "host ip: $HOST_IP"   # must be non-empty

docker run --rm -it \
    -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy \
    -p 8080:8080 \
    -p 8081:8081 \
    -p 8089:8089 \
    mitmproxy/mitmproxy mitmweb \
        --web-host 0.0.0.0 \
        --set block_global=false \
        --mode reverse:https://api.openai.com:443@8080 \
        --mode reverse:http://${HOST_IP}:8100@8089
```

**Terminal 2 (agent)** point both legs at the proxy, then run the agent:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1/"
export MCP_URL="http://127.0.0.1:8089/mcp"
python3 agent_demo.py
```

Now open the mitmweb UI at `http://127.0.0.1:8081`. You should see, in order:

- POST to `api.openai.com` (`/v1/responses`) as the model receives the task and
  the MCP tool schemas and decides to call a tool;
- POSTs to the MCP server (`/mcp`): `initialize`, `tools/list`, then
  `tools/call` for `add` and for `celsius_to_fahrenheit`;
- another POST to `api.openai.com` where the model reads the tool results and
  writes the final answer.

That is the whole agentic loop in cleartext at one vantage point. Note the
security weight of it: the model's full prompt (including the tool schemas and
the injected tool results) and every tool argument and result are readable at
the proxy. Anyone who can sit on that path, or read those logs, sees the
reasoning and the data, which is the point tied together in the next section.

**Cleanup.** Stop the agent, then `Ctrl+C` the server (Terminal 1) and the
proxy (Terminal 3). In Terminal 2, clear the proxy overrides so later runs are
not silently routed through a now-stopped mitmproxy:

```bash
unset OPENAI_BASE_URL MCP_URL
```

## Security risks of going stateless

Statelessness is good for scaling, but it moves several things around that
have security consequences. None of these are reasons to avoid stateless
MCP, they are things to design for.

### 1. State handles are credentials, and they ride in tool arguments

In Exercise 4 the cart id is what grants access to the cart. In the
sessionless world that id travels as a normal tool argument, which means it
lands in every place tool arguments land: application logs, tracing spans,
and the mitmproxy capture you just took. An id that authorizes access is a
credential, and this pattern puts credentials in plain sight on the wire and
in your logs. This is the same "durable stores and traces are a secrets
store you forgot you were running" lesson from lab064 and lab070's
persistent-state risk, now arriving through the front door. Treat session or
resource handles as secrets: make them unguessable (as `secrets.token_urlsafe`
does here), scope them, expire them, and redact them before you log.

### 2. Authentication has to be per-request

With a stateful session, a client authenticated once at session start and
the session carried that trust. Sessionless means there is no session to
carry it. Every request must stand on its own, so auth (a bearer token, mTLS,
a signed request) has to be presented and verified on every call. A design
that authenticated "at connect" and trusted the session afterwards has no
equivalent here, and porting it naively leaves the tools unauthenticated.

### 3. Any replica serves any request, which changes auditing

The scaling win, any replica can serve any request, also means a single
logical conversation can be spread across many processes and hosts. Your
audit trail has to be reconstructable across replicas from request-level
data (correlation ids, the handles above), because no single process saw the
whole interaction. Plan the observability the way lab090 and lab122 frame it,
at the request and syscall level, not per-session.

### 4. The meta-risk: a standard revision silently changed deployed behaviour

The sharpest lesson is Exercise 2. A spec revision, shipped as a library
major version, **removed a capability** (`ctx.sample`) and **flipped session
semantics** for servers whose code nobody touched. If your deployment tracks
"latest", an unattended upgrade can break a running server, or worse, change
its behaviour without breaking it loudly. This is the lab035 lesson (fast
APIs are an attack surface) and lab070's "MCP moves fast" meta-risk, made
concrete and reproducible. The defense is boring and effective: pin the
generation you validated (as lab070 does with `fastmcp==3.4.7` and as this
lab does with `fastmcp>=4,<5`), read the changelog on every bump, and have
tests that would catch a removed capability before your users do.

## Meta-lesson

You just ran identical server code on two library generations and got two
different behaviours: pure tools survived, sampling vanished, sessions became
optional. That is the whole security-of-fast-moving-standards story in one
lab. "Latest by default" keeps you current and is the right default for
learning, but for anything you deploy, know exactly which spec era and which
library generation you validated, and pin to it deliberately. The version in
`requirements.txt` is not bureaucracy, it is a statement about which behaviour
you tested.

## Cleanup environment

```bash
deactivate
```
```bash
./lab_cleanup.sh
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
