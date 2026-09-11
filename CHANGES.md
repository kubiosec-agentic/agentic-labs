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
