# Changes

Maintenance log for the labs (not part of the student material).

## 2026-09-02

### lab004_transformers
- `roberta.py`: rewritten with `AutoModelForQuestionAnswering` (tokenize → model → argmax start/end → decode). The `question-answering` pipeline was removed in `transformers` 5.x (verified on 5.16.1).
- `demo.py`: verified working on `transformers` 5.16.1 / `torch` 2.14; the earlier "degraded output on 5.x" observation was sampling variance, not a bug.
- Dropped the `transformers<5` pin in `requirements_docker.txt`; added `requirements.txt` so `lab_setup.sh` creates the venv for Option A.
- README: documented Option A commands.
- Added optional Example 3: `transformers serve` (OpenAI-compatible endpoint, CPU). Requires `transformers[serving]` + `requests` (the `serving` extra in 5.16.1 forgets `requests`); both added to the requirements files. A vLLM version was tried first and dropped (needs an NVIDIA GPU, nobody can test it).

## 2026-09-11

### lab060_OpenAI_Agents
- `agent_01.py`: switched from `Runner.run_sync` to a single awaited `Runner.run` inside `asyncio.run(main())`.
- README: Step 1 rewritten as a line-by-line walkthrough of the script (Agent vs Runner, `Runner.run` coroutine, `final_output`); table row and intro sentence updated.
- Added `agent_09.py` (Step 9): tool guardrails (`@tool_input_guardrail` / `@tool_output_guardrail`) on a fake `run_command` tool; README section added, table and intro updated.
- `requirements.txt`: `openai-agents>=0.22` (tool guardrails need a recent SDK; venv currently has 0.22.2).

## 2026-09-12

### lab060_OpenAI_Agents
- `requirements.txt`: dropped the `openai-agents>=0.22` floor to bare `openai-agents`. The floor froze nothing (`lab_setup.sh` installs latest anyway) and other agent labs (lab085/090/120) already use bare. Convention: unpinned by default, pin only when forced.

### lab070_MCP
- README: corrected the fastmcp version references and added a rationale note. The intro and sanity-check said `>=3.2` / "3.2 or newer", which contradicted the actual `fastmcp==3.4.7` pin in `requirements.txt` and would have allowed 4.x. fastmcp 4.x removed client-side sampling from the standard, so the sampling examples (section 5) require 3.x. Badge, intro, and sanity-check now state 3.4.7, with a note explaining the pin as the one deliberate exception to the "always latest" convention.

### tests
- `requirements.txt`: lifted the `transformers<5` cap to `transformers>=4.45`. Tests now run against 5.x, matching what students get from a fresh `lab_setup.sh`. Verified working on transformers 5.

### lab035_Langchain
- `requirements.txt`: lifted the `transformers<5` cap to `transformers>=4.45` and removed the "5.x degrades small-model output" comment. The langchain `==` pins stay (deliberate, to bound the dependency tree size); only the transformers cap was dropped. Confirmed working on transformers 5.
- README: removed the Step 5 note claiming the requirements pin `transformers<5` for degraded 5.x output (no longer true).

### lab035_Langchain
- `lc06_easy_swap.py`: updated the Gemini model from `gemini-2.0-flash` to `models/gemini-3.6-flash`. Synced the documented copy at `lab990_addendum/langchain/easy_swap.py` to match.

### Gemini model bump (3.6 generation)
Bumped all Gemini model references, preserving each tier. `models/` prefix kept in lab035 (matching LC_06), bare names in ADK files.
- `lab035_Langchain`: `lc01_chat.py`, `lc02_prompt.py`, `doc/chat.md`, `doc/prompt.md` (commented/example `gemini-2.0-flash` -> `models/gemini-3.6-flash`).
- `lab061_Google_Agents`: `adk/cyber_guardian/agent.py` and `adk/llm_red_team_agent/config.py` (`gemini-2.5-pro` -> `gemini-3.6-pro`); `adk_standalone/cyber_guardian/agent.py` and `adk/instructions.md` (`gemini-2.0-flash` -> `gemini-3.6-flash`). README model table corrected to match actual per-agent models (it had drifted, showing gemini-2.0-flash for all three): red team + cyber_guardian = `gemini-3.6-pro`, standalone = `gemini-3.6-flash`.
- `lab110_A2A/adk_server/.../check_prime_agent/agent.py`: `gemini-2.5-flash-lite` -> `gemini-3.6-flash-lite`.
- `lab990_addendum/a2a/adk_server/.../check_prime_agent/agent.py`: `gemini-2.0-flash` -> `gemini-3.6-flash`.

### lab035_Langchain
- README Step 4: added a security-framed note on the `RunnableWithMessageHistory` `PendingDeprecationWarning`. Kept `lc04_multi_turn.py` as-is (still works; pattern is the point of the without-LangGraph step). Frames the deprecation as the course's recurring "things move fast" theme with a security angle: outdated code found online / emitted by LLMs is an attack surface (unpatched CVEs, abandoned transitive deps, insecure copy-paste). Points to lab050 pip-audit, lab990 SupplyChainGuard, and lab064 (LangGraph persistence as the modern replacement).
- README Step 4: sharpened the note to stress that `RunnableWithMessageHistory` was LangChain's OWN officially recommended API (first-party, `langchain_core.runnables.history`), already the second blessed answer (replaced `ConversationChain`/`langchain.memory`) and now superseded again by LangGraph persistence. Point: following the official docs still leaves you deprecated within a couple of years, which is why so much internet/LLM-sourced example code is stale. "Assume any example older than a few months is stale until checked against current docs."

### lab073_MCP_Stateless (new lab)
- New lab on stateless MCP and the fastmcp 3.x -> 4.x / 2026-07-28 spec shift, placed after lab071. Own venv on `fastmcp>=4,<5` (kept separate from lab070's pinned 3.4.7).
- Verified behaviour on fastmcp 4.0.3 vs 3.4.7 before writing: lab070's `server_streamable.py` runs unchanged and pure tools work on 4.x; lab070's sampling server raises `AttributeError: 'Context' object has no attribute 'sample'` on 4.x because `ctx.sample` was removed from the server Context; the 4.x Client gains `mode=` (auto=sessionless / legacy=2025-11-25), and `InitializeResult.protocolVersion` was renamed to `protocol_version`.
- Files: `stateless_server.py` (pure functions), `stateful_server.py` (global-counter anti-pattern vs explicit-handle pattern), `client_demo.py` (`--mode auto|legacy`), `sampling_probe.py` (triggers the lab070 sampling break with a canned handler, no key needed), `requirements.txt`. Exercises 1-2 reuse lab070's servers unchanged to make the point; 3-4 use the new servers; 5 uses mitmproxy (lab070/071 tooling) to see the session appear/disappear. Includes a small compatibility matrix and a security section (handles-as-credentials-on-the-wire, per-request auth, cross-replica auditing, standards churn as a security event).
- Wiring: added row to root README lab table; cross-linked lab070's fastmcp pin note to lab073; added `tests/test_lab073.py` (smoke: existence/syntax/no-em-dash/requirements+README content), registered the `lab073` marker in `pytest.ini`, and added `"lab073": []` to `LAB_REQUIRED_KEYS` (no API key needed). All smoke assertions pass.

### lab004_transformers
- README cleanup (Local Python / Option A): added `rm -rf ~/.cache/huggingface/hub` to clear the downloaded model cache. The default models are small, but swapping in a larger model can fill the disk. The Docker path already covered this via `docker volume prune`.

### lab061_Google_Agents (Gemini model fix)
- The "3.6 generation" bump pointed at model IDs that do not exist; `gemini-3.6-pro` returns `404 NOT_FOUND` from the Gemini API. Switched all lab061 defaults to `gemini-3.8-flash`, the current GA flash tier (verified against ai.google.dev/gemini-api/docs/latest-model, 2026-09-12), and used flash across all three agents (cheaper; was pro for red team + cyber_guardian).
- Files: `adk/cyber_guardian/agent.py`, `adk/llm_red_team_agent/config.py` (all three roles), `adk_standalone/cyber_guardian/agent.py`, `adk/instructions.md`, and the README model table.
- Not yet fixed elsewhere (same broken 3.6 family, will 404): `lab035_Langchain` (`models/gemini-3.6-flash` in lc06_easy_swap.py + commented examples), `lab110_A2A` (`gemini-3.6-flash-lite`), `lab990_addendum` (langchain/easy_swap.py, a2a check_prime_agent).

### lab061_Google_Agents (red team pipeline runtime fixes)
- `agent_utils.py`: `execute_sub_agent` split into a retrying inner `_run_agent_with_retry` plus a public wrapper that catches every exception and returns a readable string. Previously only `RuntimeError/ValueError/TypeError` were caught, so a google `ClientError` (bad model, quota, auth) propagated uncaught and the ADK web UI showed only "OTHER / undefined".
- Root cause of empty attack prompts: the agents set no `safety_settings`, so Gemini's platform filter blocked the red-team output (finish_reason=SAFETY -> empty string -> pipeline stalls). Added `permissive_safety_settings()` in `config.py` (BLOCK_NONE for the four harm categories) and applied it to the orchestrator and all three sub-agents (red_team, target, evaluator). Target uses it so only its constitution governs its replies.
- Reduced model refusals (flash declines "Prompt Injection" outright): added authorized-sandbox framing to the orchestrator and red_team instructions. Verified google.genai enum names (HarmCategory.*, HarmBlockThreshold.BLOCK_NONE) against a current google-genai; `OFF` is also available for a hard disable.
- NOTE: student must restart `adk web` to pick up module edits.

### lab061_Google_Agents (red team: attacker model refuses)
- Even with `safety_settings=BLOCK_NONE`, the flash model refuses to GENERATE adversarial prompts (alignment refusal, distinct from the platform filter). Verified independently: `gemini-3.8-flash` and `gpt-4o-mini` both decline "Prompt Injection"; `gpt-4o` complies.
- Made the pipeline provider-mixable. `config.resolve_model()` returns a plain string for Gemini names and wraps anything provider-prefixed (`openai/...`) in ADK `LiteLlm`. Defaults: `RED_TEAM_MODEL=openai/gpt-4o` (attacker + orchestrator), `TARGET_MODEL`/`EVALUATOR_MODEL=gemini-3.8-flash`. All three overridable by env.
- `safety_settings` (Gemini-only) are now attached only when the resolved model is a Gemini string, so they aren't sent to OpenAI via LiteLLM.
- `requirements.txt`: added `litellm>=1.0`. README: added OPENAI_API_KEY to env + `adk/.env`, updated model table, and added a "why two keys / alignment refusal vs platform filter" teaching note.
- Students must re-run `lab_setup.sh` (or `pip install litellm`) and restart `adk web`.

### lab064_Langgraph/ctf (stage 4 note)
- Added a docstring NOTE to `stage4_sandboxed.py`: active pen-testing can DoS the service because `exec(byte_code, globs)` runs in-process with no timeout/memory cap (stage 3's subprocess had timeout=10; stage 4 dropped it), and RestrictedPython does not stop control flow. Verified both Bandit (B102 exec_used, CWE-78) and Semgrep (exec-detected) flag the exec() call, with the nuance that SAST flags the primitive, not the missing-timeout DoS itself (that needs DAST/manual review). Stage 4 remains not solvable for flag extraction via the tool (confirmed offline against a replica and live against the running instance).

### lab070_MCP (Playwright browser MCP example)
- Added `mcp_08_playwright_interactive.py`: REPL agent (openai-agents + SQLiteSession) driving headless Chromium via `@playwright/mcp` over stdio. New file; the filesystem interactive example is untouched.
- Root cause of the "browser is unavailable" failure students hit: `@playwright/mcp` defaults to the Google Chrome CHANNEL (looks for branded Chrome), not the bundled `chromium` in ~/.cache/ms-playwright. Verified live on the Ubuntu box via the script's `/diag` (raw error: "Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome"). Fix: `npx playwright install chrome`, wired into `--install-browser`.
- Script flags: `--install-browser` (npx playwright install chrome), `--no-sandbox` (headless-server sandbox failures), and a `/diag <url>` REPL command that calls browser_navigate directly so the raw Playwright error is visible instead of the LLM's paraphrase. `client_session_timeout_seconds=60` for slow browser ops.
- README: new "### 11. Browser automation MCP (Playwright, headless)" section with the verified setup steps, the Chrome-channel gotcha, headless-server extras (install-deps, --no-sandbox), the /diag tip, and a [SECURITY] note (browser_run_code_unsafe + untrusted page content). Added item 6 to "What you will cover".
- Confirmed the alternative bundled-Chromium path works too (--browser chromium + `npx @playwright/mcp install-browser chrome-for-testing`); documented as the no-branded-Chrome option.

### lab080_MAS (agno bumped to 3.x)
- AN_03_mcp_agent.py failed at import: agno 2.5.16 imports `streamablehttp_client` from `mcp.client.streamable_http`, but the unbounded `mcp>=1.0.0` pin pulled a newer mcp that renamed it to `streamable_http_client`. Root cause: agno's mcp support is an optional extra with real bounds, but the lab pinned a bare `mcp` that resolved outside them.
- Fix: `requirements-agno.txt` now uses `agno[mcp]==3.0.9` (latest) and drops the bare `mcp>=1.0.0` line, so pip installs the mcp SDK agno supports (>=2.1,<3) plus fastmcp 4.x. Verified in a clean env: `from agno.tools.mcp import MCPTools` imports, and AN_01/AN_02/AN_03 use only APIs still present in agno 3.0.9 (Agent/Team/OpenAIChat/SqliteDb/MCPTools kwargs, print_response, get_chat_history, MCPTools(url=...)), so no script edits were needed.
- Students must reinstall the venv: `.venv-agno/bin/pip install -r requirements-agno.txt` (or delete and recreate .venv-agno).

### lab080_MAS (crewai bumped to 1.15.21)
- `requirements-crewai.txt`: crewai/crewai-tools 1.14.1 -> 1.15.21 (latest), kept equal (crewai's `tools` extra pins crewai-tools to the same version). CRAI_01 uses stable 1.x APIs (Task/Crew/Process/Agent, SerperDevTool, standard kwargs, crew.kickoff), so no script changes needed.
- Root `requirements.txt`: updated the pydantic-constraint note. crewai 1.15.21 now allows pydantic >=2.11.9,<2.13 (was <2.12), which overlaps pydantic-ai's >=2.12 on 2.12.x; per-framework venvs stay the default anyway to isolate transitive-dependency clashes.
- Verified: both packages have 1.15.21 on PyPI and crewai 1.15.21 metadata (pydantic range, crewai-tools pin). Not run end to end (crewai is a heavy install and CRAI_01 needs SERPER_API_KEY + OPENAI_API_KEY). Students reinstall: `.venv-crewai/bin/pip install -r requirements-crewai.txt`.

### lab080_MAS (crewai memory embedder pin)
- After the 1.15.21 bump, CRAI_01 flooded with EmbeddingDimensionMismatchError (store 1536-dim vs new default 3072-dim). Cause: crewai's default embedder changed text-embedding-3-small -> text-embedding-3-large between versions; existing memory stores are 1536-dim. The crew still completed (errors are caught per memory op), but the output is unusable noise.
- Fix: CRAI_01.py pins `embedder={"provider":"openai","config":{"model":"text-embedding-3-small"}}` on the Crew, matching existing stores (1536-dim) and making the run reproducible regardless of crewai's default drift. Alternative documented in-code: reset memories to adopt 3-large.

### lab080_MAS (crewai memory error - definitive fix)
- The embedder-pin approach only helps when it's actually deployed AND the on-disk store already matches; it does not fix a box still running the old file or a store built at a different dimension. Replaced it: CRAI_01.py now sets memory=False on both agents and the crew (was memory=True). This demo needs no cross-run vector memory, and disabling it removes the LanceDB store + embedder entirely, so EmbeddingDimensionMismatchError cannot occur regardless of crewai's default-embedder drift. Kept the pin recipe as an in-code comment for anyone who wants to demonstrate memory. No reset needed once memory=False is deployed (there is no store).

### lab080_MAS (pydantic-ai bumped to 2.43.0)
- `requirements-pydanticai.txt`: pydantic-ai 1.81.0 -> 2.43.0 (latest). The `builtin_tools=` Agent kwarg was removed in 2.x; native (provider-side) tools now go through `capabilities=[NativeTool(...)]` (`from pydantic_ai.capabilities import NativeTool`). Rewrote `pydanticai/PD_01.py` (`NativeTool(WebSearchTool())`) and `PD_02.py` (`NativeTool(CodeExecutionTool())`); `run_sync`/`result.output` unchanged. Verified both agents construct on 2.43.0 in a clean venv. Updated the pydanticai README "Native tools" bullet.

### lab080_MAS (FastAgent updated for fast-agent-mcp 0.10.x)
- The package was renamed internally `mcp_agent` -> `fast_agent` in the 0.10 line, so the import in all four `fastagent/example*/agent.py` is now `from fast_agent import FastAgent` (old `from mcp_agent.core.fastagent import FastAgent` no longer resolves). Confirmed against the 0.10.24 wheel that the decorator/runtime API is unchanged: `@fast.agent` / `@fast.orchestrator` signatures (name, instruction, servers, agents, plan_type) and `fast.run()` / `agent(...)` / `agent.<name>(...)` all still hold, so no other code changes were needed.
- `fastagent/README.md`: pinned setup to `fast-agent-mcp==0.10.24`, changed `uv venv` to `uv venv --python 3.12`, and added a note that 0.10.x requires Python 3.12+ and uses the new `fast_agent` import.

### lab087_Mem0 (Part 3 rewritten: OpenMemory archived -> hosted Mem0 MCP)
- Part 3 taught the self-hosted OpenMemory MCP server (git clone `mem0ai/mem0` -> `openmemory/`, docker-compose api+ui+qdrant, `make build/up`, a `limit`->`top_k` sed fix, `@openmemory/install`, SSE endpoint `http://localhost:8765/mcp/<client>/sse/<user>`). Verified against current sources that this is all obsolete: OpenMemory has been ARCHIVED and REMOVED from `mem0ai/mem0` (no `openmemory/` on main, HEAD 2026-09-11). The `mem0ai/openmemory` repo name now hosts an unrelated coding-session-sync tool; the old MCP server survives only as a read-only snapshot under `mem0ai/openmemory/openmemory-archive/` (its README states it is unmaintained).
- Rewrote Part 3 around the maintained hosted Mem0 MCP: endpoint `https://mcp.mem0.ai/mcp` (streamable HTTP, not SSE), browser sign-in or `Authorization: Bearer $MEM0_API_KEY` (same key as Part 2), `npx mcp-add --type http --url ... --clients ...` for registration, Claude Desktop manual connector, and MCP Inspector tests using `--transport http` + `--header`. Verified endpoint/transport/auth/tool-names against docs.mem0.ai/platform/mem0-mcp and the Inspector CLI flags (`--transport http`, `--header "Name: Value"`) against `@modelcontextprotocol/inspector --help`.
- Added a "What changed (2026)" note and a security section (data residency now that memory leaves the box, the API key as a memory credential, and exposed destructive tools `delete_all_memories`/`delete_entities`), cross-linking lab070/lab073. Noted the maintained local option is the mem0 self-hosted REST server (`cd server && make bootstrap`), which is REST, not MCP: there is no longer a maintained self-hosted + MCP mem0 server.

## 2026-09-15

### lab066_DeepAgents (new lab)
- New lab on LangChain's `deepagents` as a model-agnostic, general-purpose harness (the open equivalent of Claude Code / Codex CLI), placed after lab064 because it builds on LangGraph and the langchain v1 middleware stack. Uses OpenAI (`openai:gpt-4o-mini` by default, `DA_MODEL` to override).
- Written and verified against deepagents 0.7.14 / langchain 1.4.0 / langgraph 1.2.11. Notable 0.7 facts baked into the exercises: `write_todos` is no longer a built-in (needs `TodoListMiddleware`), built-ins are `ls/read_file/write_file/edit_file/delete/glob/grep/execute/task`; `FilesystemPermission.operations` is only `read`/`write`; sub-agent `permissions` replace (not extend) the parent's; `MemoryMiddleware` sits in the tail stack so user middleware cannot see the injected memory (hence `DA_TRACE` only in Exercise 3); openai models default to the Responses API (common.py forces Chat Completions for mitmproxy familiarity).
- Files: `common.py` (model factory, stream printer, `trace_prompt` middleware), `da_01..da_08` (harness basics, FilesystemBackend + permissions, skills, sub-agents, Docker sandbox vs LocalShellBackend with HITL, AGENTS.md memory + StoreBackend/CompositeBackend, tool-result eviction + summarisation, indirect prompt injection with memory poisoning: vulnerable vs hardened), `docker_sandbox.py` (BaseSandbox subclass, hardened `docker run` flags), `skills/port-triage/SKILL.md`, `memory/AGENTS.md` (+ `.orig`), `workspace/` fixtures incl. the poisoned `vendor/README.md`, `reset_workspace.sh`.
- `workspace/.env` (fake secret) is gitignored by the repo-wide `.env` rule, so `reset_workspace.sh` creates it; README setup tells students to run it first.
- Verification: every exercise was driven end to end with a scripted fake chat model (tool-call plumbing, permissions, traversal block, skill index injection, sub-agent isolation, sandbox file ops through `execute`, memory edit + store route, eviction to `/large_tool_results/`, summarisation trigger, HITL interrupt/reject on memory writes). Not yet run against a live OpenAI key or a real Docker daemon; `tests/test_lab066.py` has a `slow` live test for Exercise 1.
- Wiring: root README table row, `tests/test_lab066.py` (42 smoke assertions pass), `lab066` marker in `pytest.ini`, `"lab066": ["OPENAI_API_KEY"]` in `LAB_REQUIRED_KEYS`.

### lab066_DeepAgents (fixes from first live run on Mac, gpt-4o)
- da_04: parent `permissions` deny on `/**` did NOT block `/.env` (model listed `ls('./')` and read the secret). Root cause: deepagents 0.7.14 matches FilesystemPermission patterns without DOTGLOB, so `/**` excludes dotfiles. Added `EVERYTHING = ["/**","/**/.*","/**/.*/**"]` to common.py and used it for every "all files" deny (da_02 secondary write deny, da_04 parent + reviewer/fixer secondary denies). README section 4 gained a "dotfile trap" note. Verified: with EVERYTHING the parent's ls/read of `/.env` and `/app.py` are all denied and it must delegate.
- da_05 local: `Command(resume={"decisions":[one]})` crashed with "Number of human decisions (1) does not match number of hanging tool calls (4)" because the model emitted 4 execute calls in one turn. Rewrote the resume loop to prompt once per hanging call and send one decision each, in order. Verified with simulated y/n/y/y (rejected call returns the rejection message, others run).
- da_05 docker: every command failed with "cannot create /large_tool_results/...: Directory nonexistent" because FilesystemMiddleware offloads large execute output there inside the sandbox and the root is read-only. docker_sandbox.py now mounts a tmpfs at /large_tool_results.
- da_08: gpt-4o correctly refused the injection (summarised without touching /.env or memory). This is right behaviour, not a bug; strengthened the payload framing and rewrote README section 8 to lead with model variance (a well-aligned model may refuse; the mitigations must hold regardless) rather than promising the write always fires.

### lab066_DeepAgents (dotfile-trap turned into a red-team exercise)
- Turned the da_04 finding (deny on `/**` does not cover dotfiles, because deepagents 0.7.14 matches permission globs with GLOBSTAR on / DOTGLOB off, standard shell convention) into a first-class, reproducible exercise instead of just a code comment. It reproduced on a live gpt-4o run: a locked-down agent with `deny /**` still let the model `ls` and read `/.env`.
- da_02: added Task C, a red-team secret sweep against a second, "locked-down" agent whose blanket deny is the variable under test. `DA_WEAK_DENY=1` uses the mistake (`["/**"]`), default uses the fix (`EVERYTHING`). Under the weak rule `ls` returns ONLY the dotfiles (visible files are denied and filtered out, so the deny list hands the model a curated secrets index) and `/.aws/credentials` + `/.claude/settings.json` read straight through; under the fix every dotfile read is denied. Tasks A/B unchanged.
- Fixtures: added `workspace/.aws/credentials` and `workspace/.claude/settings.json` (the harness's OWN config, with a fake MCP token) alongside the existing `.env`, so the sweep has realistic dotfile targets. All values are obvious placeholders, deliberately NOT `AKIA...`/`ghp_...` shaped, so GitHub push protection / gitleaks will not flag them. `reset_workspace.sh` recreates all three (`.env` stays gitignored; `.aws`/`.claude` are committed fixtures).
- README: rewrote Exercise 2 with a "dotfile trap" subsection, the weak/strong invocation, the leaked-`ls` output, a target-file table (.env, .aws, .ssh, .git/config, .kube, .npmrc/.pypirc, .netrc/.docker, and .claude/.mcp.json as the harness's own front door), and a red-team rule-of-thumb box that chains into Exercise 8. Framed as "not strictly a deepagents bug (it follows glob convention) but a serious footgun for a deny-based security control".
- tests: +5 assertions (EVERYTHING covers dotfiles, DA_WEAK_DENY toggle present, fixtures exist and are marked FAKE); 47 smoke pass.
- Note: consider filing a deepagents issue proposing the FilesystemPermission docstring warn about DOTGLOB, or a `match_dotfiles`/dotfile-defaulting option for deny rules. Verified on 0.7.14; recheck current release first.

### lab078_Agents_MCP_Skills (new lab)
- New lab combining the OpenAI Agents SDK (lab060) with MCP (lab070) and adding a hand-built "skills" layer, placed after lab075, before lab080. Shows how MCP (capability), a skill (procedure), a script (deterministic compute) and a reference (knowledge) compose in one agent. Contrast with lab066 where deepagents provides skills built in; here the ~30-line skills runtime is explicit.
- API verified against openai-agents 0.22.2 / fastmcp 4.0.3 / mcp 2.2.0 (subagent introspected the installed SDK). Key facts baked in: MCPServerStdio takes a `params` TypedDict (command+args list, not a module path), tracing disabled via `set_tracing_disabled(True)` in common.py to avoid telemetry network calls, agent/MCP construction + list_tools() work with no API key (only Runner.run needs one).
- Files: `mcp_server.py` (fastmcp stdio server: `add`, `http_get`), `skills_runtime.py` (front-matter index + `read_skill`/`read_reference`/`run_skill_script` function tools, `_safe` path containment), `agent_01_mcp.py` (agent + MCP baseline), `agent_02_simple_skill.py` (instructions-only `incident-note` skill), `agent_03_power_skill.py` (`http-header-audit` skill = SKILL.md + `audit_headers.py` grader + `reference/grading.md`). Powerful skill orchestrates: http_get (MCP fetch) -> run script (grade) -> read reference (explain) -> incident-note (report).
- `audit_headers.py` is a pure, offline, deterministic grader (headers JSON on stdin -> weighted A-F score for HSTS/CSP/nosniff/X-Frame/Referrer/Permissions + disclosure flags); unit-tested in tests/test_lab078.py without a key.
- Security framing: `http_get` is an SSRF primitive (left open on purpose, README shows metadata-endpoint risk), `run_skill_script` is RCE if skills/ is attacker-writable (same boundary as lab066 ex.3), poisoned SKILL.md/reference is prompt injection you asked for.
- Verification: grader (all letter grades), skills runtime (discover/build_instructions/_safe containment blocks traversal), and MCP wiring (real MCPServerStdio subprocess -> list_tools() -> ['add','http_get'], all three agents build keyless) checked offline in the cloud. NOT yet run against a live OPENAI_API_KEY; tests/test_lab078.py has a `slow` live test for agent_01.
- Wiring: root README row, tests/test_lab078.py (24 smoke pass), lab078 marker in pytest.ini, `"lab078": ["OPENAI_API_KEY"]` in LAB_REQUIRED_KEYS.

### lab078_Agents_MCP_Skills (native skills: Exercise 4 + native layout)
- Restructured the http-header-audit skill to the vendor-native layout: `scripts/audit_headers.py` and `references/grading.md` under one top folder with `SKILL.md` at its root. Same folder now works both hand-built (ex. 1-3) and as an uploadable OpenAI/Anthropic skill. Updated skills_runtime.py (read_reference -> references/, run_skill_script docstring -> scripts/) and SKILL.md paths. (Left an empty `reference/` dir and a __pycache__ on disk from the in-place move; both gitignored.)
- Added Exercise 4 (`native/`): the same skill run through the two managed paths. `native/openai_uploaded_skill.sh` (curl, for CI/scripting): POST /v1/skills multipart upload of the skill folder, then POST /v1/responses with tools[].type="shell", environment.type="container_auto", environment.skills=[{type:"skill_reference",skill_id,version}]. Request body built with jq so header JSON is escaped correctly. `native/anthropic_skill_example.py` (SDK): client.skills.create(files=files_from_dir(...)) then messages.create(container={"skills":[{type:"custom",skill_id,version}]}, tools=[{type:"code_execution_20250825",name:"code_execution"}]).
- API surfaces verified: endpoint shapes + param nesting cross-checked across OpenAI skills guide, cookbook, Azure Foundry docs, and the Anthropic skills guide + Skill Management API reference (subagent research). Anthropic example verified against the INSTALLED anthropic 1.6.0 SDK (client.skills.create, anthropic.lib.files_from_dir, messages.create container= kwarg all exist). Model-name literals are NOT hardcoded (docs fetcher returned fabricated/inconsistent model strings); both examples read the model from OPENAI_SKILL_MODEL / ANTHROPIC_SKILL_MODEL with a helpful error, README links the live docs.
- README: Exercise 4 section with a where-does-it-run table (local DIY / OpenAI uploaded / OpenAI local-shell / Anthropic uploaded), 4a and 4b run instructions, and a security note on the managed modes (uploaded = vendor sandbox blast radius but data leaves your box; unpinned version = rug-pull surface; OpenAI local-shell = remote model driving your shell = the lab's local-RCE lesson).
- requirements.txt: added anthropic (only needed for 4b). tests/test_lab078.py: paths updated to scripts/references, +native-layout and +native-example-API-shape assertions. Native examples are not smoke-run (need keys + current models + skills access); grader/runtime/MCP checks stay offline.

## 2026-09-18

### lab035_Langchain merged into lab054_LangChain_Tools
- Reason: training timing, and less emphasis on LangChain as a provider adapter. lab054 was the better survivor (tool-call cycle, hosted vs local execution, unsandboxed REPL). lab054 `LC_01.py` already duplicated lab035 `lc01_chat.py`.
- lab054 now has six steps: `LC_01` bare call (unchanged), `LC_02` NEW prompts + LCEL (folds lab035 `lc02_prompt.py` and `lc03_advanced_prompting.py` into one script, roles + pipe + chain-into-chain), `LC_03` tool binding (was `LC_02`), `LC_04` NEW hosted tools (old `LC_03` web search + old `LC_04` code interpreter in one script), `LC_05` REPL agent loop and `LC_06` raw-OpenAI chain (unchanged, cross-reference in LC_05 docstring updated). README rewritten shorter; the lab035 "fast-moving APIs / deprecated memory" security note kept as a short section (lab073 references it, link updated from lab035 to lab054).
- Moved to `lab990_addendum/langchain/`: `lc04_multi_turn.py` -> `multi_turn.py` (kept as the live demo of the `RunnableWithMessageHistory` deprecation warning), `lc05_hf_local.py` -> `hf_local.py`, and the five `doc/*.md` write-ups -> `doc/`. `lc06_easy_swap.py` dropped (byte-identical to the existing `easy_swap.py`). lab990 README: setup now points at the `.lab054` venv, two new sections (3 and 4), others renumbered; `requirements.txt` gained `langchain-community` (ChatMessageHistory), torch/transformers/accelerate/langchain-huggingface listed as optional comments (large download, only for `hf_local.py`).
- Not carried over: lab035's `==` pins on langchain 0.3.x (were there to bound the torch/transformers tree; lab054 stays unpinned per convention) and the `lab_setup.sh`/`lab_cleanup.sh` of lab035.
- Wiring: root README row removed (lab054 row retitled "LangChain basics, chains and tools"), `tests/test_lab035.py` removed, `lab035` marker and `LAB_REQUIRED_KEYS` entry removed, `tests/test_lab054.py` +6 structural checks (LCEL in LC_02, tool binding in LC_03, responses/v1 + both hosted tools in LC_04, security warning in LC_05, deprecation note in README, no active gpt-3.5-turbo). 36 smoke pass; full suite still collects (737).
- Not live-run (no key on the machine): `LC_02.py` and `LC_04.py` are recombinations of previously working code, syntax-checked only. Ordering note: lab040 (RAG) now precedes the first LangChain lab; LCEL basics are covered in the slides before RAG.

### lab054_LangChain_Tools (dropped LC_06)
- `LC_06.py` moved to `lab990_addendum/langchain/runnable_lambda_tool.py`. It was raw OpenAI SDK function calling (already lab050) with only a `RunnableLambda` wrapper as LangChain content, and its docstring referenced a non-existent `LC_core.py` (fixed in the moved copy). lab054 is now five steps. README, lab990 README (new section 5, later sections renumbered), tests and CHANGES updated.

### lab054_LangChain_Tools (new LC_06: provider swap)
- Replaced the dropped raw-OpenAI chain with the lab035 `lc06_easy_swap.py` idea as `LC_06.py`, rewritten: provider chosen by `USE_GEMINI` env var (default OpenAI, so it runs with only `OPENAI_API_KEY`), `langchain_core.prompts` instead of the `langchain` meta-package, `StrOutputParser` added, Gemini model `gemini-3.8-flash` (the 3.6 names 404, see lab061 entry). `requirements.txt` +`langchain-google-genai`. README step 6 + table + optional GOOGLE_API_KEY in setup. Test +1 (both providers present, no 3.6 model).
- `lab990_addendum/langchain/easy_swap.py`: fixed `models/gemini-3.6-flash` -> `gemini-3.8-flash` (was on the "not yet fixed" list). README notes lab054 LC_06 as the cleaner version.

### lab040_RAG (RAG_02 rewrite)
- `RAG_02.py`: printed only `docs[0]` for both search modes, which hides that retrieval returns a ranked list. Now prints the top `K=4` chunks with distance scores for both entry points (`similarity_search_with_score` and `similarity_search_by_vector_with_relevance_scores`, both raw Chroma distance, lower = closer, verified on langchain-chroma 1.1.0), prints chunk count and the query vector length, reuses one `OpenAIEmbeddings` instance, and drops the dead `openai.api_key = ...` line (the embeddings class reads the env var). Based on a suggested rewrite (k=4 + loop); extended with scores and the vector printout. README step 2 observations rewritten. Not live-run.
