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
